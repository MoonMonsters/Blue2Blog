#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import render_template, request

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/')
def index():
	print('blog.index')
	print(request.endpoint)
	return render_template('blog/index.html')


@blog_bp.route('/about')
def about():
	pass
