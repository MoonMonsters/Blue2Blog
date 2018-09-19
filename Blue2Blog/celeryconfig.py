#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Flynn on 2018-09-19 22:55

from kombu import Exchange, Queue

BROKER_URL = 'redis://127.0.0.1:6379/2'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/3'

CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ENABLE_UTC = True

CELERYD_CONCURRENCY = 20
CELERYD_PREFETCH_MULTIPLIER = 4
# 每个worker最大执行任务数量，不要设置太大，否则容易内存泄漏
CELERYD_MAX_TASKS_PER_CHILD = 100

# 每个任务执行超时时间
CELERY_TASK_RESULT_EXPIRES = 60 * 5
# 每个任务最大执行时间
CELERYD_TASK_TIME_LIMIT = 60 * 2

CELERY_IMPORTS = (
	'Blue2Blog.blueprints.admin',
	'Blue2Blog.blueprints.auth',
	'Blue2Blog.blueprints.blog',
)

CELERY_QUEUES = (
	Queue('default', exchange=Exchange('default'), routing_key='default'),
	Queue('long_time_task', exchange=Exchange('long_time_task'), routing_key='long_time_task'),
	Queue('short_time_task', exchange=Exchange('short_time_task'), routing_key='short_time_task')
)
