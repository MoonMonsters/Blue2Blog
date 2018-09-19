#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Flynn on 2018-09-19 23:28


import os

os.system('celery -A Blue2Blog worker -l debug -P eventlet')
