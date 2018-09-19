#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from functools import wraps
from datetime import datetime
from urllib.parse import urlparse, urljoin
import redis
import pickle

from flask import request, redirect, url_for, flash, current_app
from flask_login import current_user
from Blue2Blog import settings


def _log():
	# 创建logger，如果参数为空则返回root logger
	logger = logging.getLogger("Blue2Blog")
	logger.setLevel(logging.DEBUG)  # 设置logger日志等级
	# 这里进行判断，如果logger.handlers列表为空，则添加，否则，直接去写日志
	if not logger.handlers:
		# 创建handler
		fh = logging.FileHandler("test.log", encoding="utf-8", mode="a")
		ch = logging.StreamHandler()
		# 设置输出日志格式
		formatter = logging.Formatter(
			fmt="%(asctime)s %(thread)d %(filename)s %(funcName)s %(lineno)d %(message)s",
			datefmt="%Y/%m/%d %X",
		)
		# 为handler指定输出格式
		fh.setFormatter(formatter)
		ch.setFormatter(formatter)
		# 为logger添加的日志处理器
		logger.addHandler(fh)
		logger.addHandler(ch)

	logger.debug(msg="\n" * 10)
	logger.debug(msg="now time is " + str(datetime.now()))
	logger.debug("-" * 80)

	return logger  # 直接返回logger


logger = _log()


def is_safe_url(target):
	ref_url = urlparse(request.host_url)
	test_url = urlparse(urljoin(request.host_url, target))
	return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def redirect_back(default="blog.index", **kwargs):
	"""
	返回原链接
	"""
	for target in request.args.get("next"), request.referrer:
		if not target:
			continue
		if is_safe_url(target):
			return redirect(target)

	return redirect(url_for(default, **kwargs))


def stint_login_user(func):
	"""
	当使用admin001测试账号时，限制权限，只有查看后台权限，无法修改
	"""
	logger.debug("func.__name__ = " + str(func.__name__))

	@wraps(func)
	def wrapper(*args, **kwargs):
		logger.debug("current_user.username = " + str(current_user.username))
		# 如果是admin001账号，只能查看后台，不能修改任何数据
		if current_user.username == "admin001":
			# 如果网页中使用的是ajax异步请求，该flash消息无法发送到网页中，暂时不清楚如何解决
			flash("Sorry, You Do Not Have Enough Permission To Do This.", "warning")
			return redirect_back()
		else:
			f = func(*args, **kwargs)
			return f

	return wrapper


class CacheUtil(object):
	"""
	缓存工具类
	"""
	pool = redis.ConnectionPool()
	cache = redis.Redis(
		host=settings.BaseConfig.CACHE_REDIS_HOST,
		port=settings.BaseConfig.CACHE_REDIS_PORT,
		db=settings.BaseConfig.CACHE_REDIS_DB,
		# host=current_app.config["CACHE_REDIS_HOST"],
		# port=current_app.config["CACHE_REDIS_PORT"],
		# db=current_app.config["CACHE_REDIS_DB"],
		connection_pool=pool,
	)

	@staticmethod
	def save_posts_to_cache(
			post, category, expired=settings.BaseConfig.CACHE_REDIS_EXPIRED_TIME
	):
		logger.debug("save cache, post.id = " + str(post.id))
		"""
		将文章缓存
		之所以将post和category同时传进来是因为
		1.缓存是为了缓解数据库压力，如果只将post缓存，但在jinja2中仍然需要通过post.category.id获取数据，也就是
		说，还是查询了数据库了
		2.当从redis中获取到post对象时没有经过SQLAlchemy的Session，所以数据库其实是关闭的，那么在jinja2中
		通过post.category.id获取数据时就会报错
		:param post: Post对象
		:param category: Category对象
		:param expired: 过期时间
		"""
		# 缓存的时候会以二进制存进去
		# 将Post和Category都用post.id做为key值存进去
		# 在获取缓存文章的时候，并不一定可以category的id，而且Post和Category是一对多的关系
		# 不会出现混乱的情况
		CacheUtil.cache.set(
			current_app.config["CACHE_REDIS_BLOG_POST_ID_"] + str(post.id),
			pickle.dumps(post),
			ex=expired,
		)

		CacheUtil.cache.set(
			current_app.config["CACHE_REDIS_BLOG_CATEGORY_ID_"] + str(post.id),
			pickle.dumps(category),
			ex=expired,
		)

	@staticmethod
	def get_posts_from_cache(post_id):
		logger.debug("get cache, post.id = " + str(post_id))
		"""
		从缓存中读取文章数据
		:param post_id: 文章id
		"""
		post = pickle.loads(
			CacheUtil.cache.get(
				current_app.config["CACHE_REDIS_BLOG_POST_ID_"] + str(post_id)
			)
		)
		category = pickle.loads(
			CacheUtil.cache.get(
				current_app.config["CACHE_REDIS_BLOG_CATEGORY_ID_"] + str(post_id)
			)
		)
		# 在读取完后，将post和category关联起来，就不再需要从数据库中读取category了
		post.category = category
		return post

	@staticmethod
	def delete_posts_from_cache(post_id):
		logger.debug('delete cache, post_id = ' + str(post_id))
		"""
		删除缓存中的Post和Category
		:param post_id: 文章id
		"""
		CacheUtil.cache.delete(current_app.config["CACHE_REDIS_BLOG_POST_ID_"] + str(post_id))
		CacheUtil.cache.delete(current_app.config["CACHE_REDIS_BLOG_CATEGORY_ID_"] + str(post_id))

	@staticmethod
	def set_comments_of_posts_to_cache(post_id, page_id, *comments):
		"""
		缓存某篇文章下的所有评论
		:param post_id: 文章id
		:param page_id: 这篇文章下评论很多，需要分页查询，那么也需要分页缓存
		:param comments: 所有评论
		"""
		# 以post的id和page做为key值，分页缓存这篇文章下的所有的评论
		CacheUtil.cache.sadd(
			current_app.config["CACHE_REDIS_BLOG_POST_COMMENTS_"] + str(post_id) + '_PAGE_' + str(page_id),
			*[pickle.dumps(comment) for comment in comments]
		)

	@staticmethod
	def get_comments_of_posts_from_cache(post_id, page_id):
		"""
		获取某篇文章下的所有评论
		:param post_id: 文章id
		:param page_id: 评论分页后的页码
		:return: 评论集合
		"""
		comments = CacheUtil.cache.smembers(
			current_app.config["CACHE_REDIS_BLOG_POST_COMMENTS_"] + str(post_id) + '_PAGE_' + str(page_id))

		return [pickle.loads(comment) for comment in comments]
