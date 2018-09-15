#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

# 绝对路径
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class BaseConfig(object):
	SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')

	SQLALCHEMY_TRACK_MODIFICATIONS = False

	MAIL_SERVER = os.getenv('MAIL_SERVER')
	# SERVER_NAME = MAIL_SERVER
	MAIL_PORT = 25
	MAIL_USE_SSL = False
	MAIL_USERNAME = os.getenv('MAIL_USERNAME')
	MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
	MAIL_DEFAULT_SENDER = ('Blue2Blog Admin', MAIL_USERNAME)

	BLUE2BLOG_EMAIL = os.getenv('BLUE2BLOG_EMAIL')
	BLUE2BLOG_POST_PER_PAGE = 10
	BLUE2BLOG_MANAGE_POST_PER_PAGE = 15
	BLUE2BLOG_COMMENT_PER_PAGE = 15

	DEBUG = False

	BLUE2BLOG_THEMES = {'perfect_blue': 'Perfect Blue', 'black_swan': 'Black Swan'}


class DevelopmentConfig(BaseConfig):
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.db')
	DEBUG = True


class TestingConfig(BaseConfig):
	TESTING = True
	WTF_CSRF_ENABLED = False
	SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory'
	DEBUG = True


class ProductionConfig(BaseConfig):
	SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@127.0.0.1:3306/blue2blog'


config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig,
	'production': ProductionConfig
}
