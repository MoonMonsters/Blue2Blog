#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/post')
def new_post():
	pass
