#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Flynn on 2018-09-19 23:38

from celery import Celery

celery_app = Celery('Blue2Blog')
celery_app.config_from_object('Blue2Blog.celeryconfig')
