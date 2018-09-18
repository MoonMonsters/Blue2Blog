#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from functools import wraps
from datetime import datetime
from urllib.parse import urlparse, urljoin

from flask import request, redirect, url_for, flash
from flask_login import current_user


def _log():
	# 创建logger，如果参数为空则返回root logger
	logger = logging.getLogger("Blue2Blog")
	logger.setLevel(logging.DEBUG)  # 设置logger日志等级
	# 这里进行判断，如果logger.handlers列表为空，则添加，否则，直接去写日志
	if not logger.handlers:
		# 创建handler
		fh = logging.FileHandler("test.log", encoding="utf-8", mode='a')
		ch = logging.StreamHandler()
		# 设置输出日志格式
		formatter = logging.Formatter(
			fmt="%(asctime)s %(thread)d %(filename)s %(funcName)s %(lineno)d %(message)s",
			datefmt="%Y/%m/%d %X"
		)
		# 为handler指定输出格式
		fh.setFormatter(formatter)
		ch.setFormatter(formatter)
		# 为logger添加的日志处理器
		logger.addHandler(fh)
		logger.addHandler(ch)

	logger.debug(msg='\n' * 10)
	logger.debug(msg='now time is ' + str(datetime.now()))
	logger.debug('-' * 80)

	return logger  # 直接返回logger


logger = _log()


def is_safe_url(target):
	ref_url = urlparse(request.host_url)
	test_url = urlparse(urljoin(request.host_url, target))
	return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='blog.index', **kwargs):
	"""
	返回原链接
	"""
	for target in request.args.get('next'), request.referrer:
		if not target:
			continue
		if is_safe_url(target):
			return redirect(target)

	return redirect(url_for(default, **kwargs))


def stint_login_user(func):
	"""
	当使用admin001测试账号时，限制权限，只有查看后台权限，无法修改
	"""
	logger.debug('func.__name__ = ' + str(func.__name__))

	@wraps(func)
	def wrapper(*args, **kwargs):
		logger.debug('current_user.username = ' + str(current_user.username))
		# 如果是admin001账号，只能查看后台，不能修改任何数据
		if current_user.username == 'admin001':
			# 如果网页中使用的是ajax异步请求，该flash消息无法发送到网页中，暂时不清楚如何解决
			flash('Sorry, You Do Not Have Enough Permission To Do This.', 'warning')
			return redirect_back()
		else:
			f = func(*args, **kwargs)
			return f

	return wrapper
