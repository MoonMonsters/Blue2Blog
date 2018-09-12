#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
