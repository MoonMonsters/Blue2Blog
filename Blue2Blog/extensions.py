#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_ckeditor import CKEditor
from flask_moment import Moment
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# 创建第三方库对象，但此时不传入app对象做参数
bootstrap = Bootstrap()
db = SQLAlchemy()
moment = Moment()
ckeditor = CKEditor()
mail = Mail()
login_manager = LoginManager()
csrf = CSRFProtect()


@login_manager.user_loader
def load_user(user_id):
	"""
	用户加载函数
	session中只会保存用户id，所以需要设置一个用户加载函数，来返回对应的用户对象
	:param user_id: 用户id
	:return: Admin对象实例
	"""
	from Blue2Blog.models import Admin
	admin = Admin.query.get(int(user_id))
	return admin
