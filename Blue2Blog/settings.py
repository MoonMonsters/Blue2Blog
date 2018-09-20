#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import uuid

# 绝对路径
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class BaseConfig(object):
	SECRET_KEY = os.getenv('SECRET_KEY', str(uuid.uuid4().hex) + str(uuid.uuid4().time))
	# 是否修改就提交
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	MAIL_SERVER = os.getenv('MAIL_SERVER')
	# SERVER_NAME = MAIL_SERVER
	MAIL_PORT = 25
	MAIL_USE_SSL = False
	MAIL_USERNAME = os.getenv('MAIL_USERNAME')
	MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
	MAIL_DEFAULT_SENDER = ('Blue2Blog Admin', MAIL_USERNAME)

	BLUE2BLOG_EMAIL = os.getenv('BLUE2BLOG_EMAIL')
	# 每一页博客数量
	BLUE2BLOG_POST_PER_PAGE = 10
	# 管理博客时每一页数量
	BLUE2BLOG_MANAGE_POST_PER_PAGE = 15
	# 每一页评论数量
	BLUE2BLOG_COMMENT_PER_PAGE = 15

	DEBUG = False

	# 可更换的主题
	BLUE2BLOG_THEMES = {'perfect_blue': 'Perfect Blue', 'black_swan': 'Black Swan'}

	CACHE_REDIS_HOST = 'http://127.0.0.1'
	CACHE_REDIS_PORT = 6379
	CACHE_REDIS_DB = 1
	# 默认是一天
	CACHE_REDIS_EXPIRED_TIME = 60 * 60 * 24
	# 缓存文章前缀
	CACHE_REDIS_BLOG_POST_ID_ = 'cache_blog_post_id_'
	CACHE_REDIS_BLOG_CATEGORY_ID_ = 'cache_blog_category_id_'
	# 缓存评论前缀
	CACHE_REDIS_BLOG_POST_COMMENTS_ = 'cache_blog_post_comments_'
	CACHE_REDIS_COMMENT_ID_ = 'cache_blog_comment_id_'


class DevelopmentConfig(BaseConfig):
	# 使用sqlite数据库
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.db')
	DEBUG = True


class TestingConfig(BaseConfig):
	TESTING = True
	WTF_CSRF_ENABLED = False
	SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory'
	DEBUG = True


class ProductionConfig(BaseConfig):
	SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@127.0.0.1:3306/blue2blog'


# 配置，加载哪一个类
config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig,
	'production': ProductionConfig
}
