#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from urllib.parse import urlparse, urljoin

from flask import request, redirect, url_for


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
	for target in request.args.get('next'), request.referrer:
		if not target:
			continue
		if is_safe_url(target):
			return redirect(target)

	return redirect(url_for(default, **kwargs))
