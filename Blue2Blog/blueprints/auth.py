#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask import Blueprint
from flask import redirect, url_for, request, flash, render_template
from flask_login import login_user, current_user, login_required, logout_user
from Blue2Blog.models import Admin
from Blue2Blog.forms import LoginForm
from Blue2Blog.utils import redirect_back, logger

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
	logger.debug('is_authenticated = ' + str(current_user.is_authenticated))
	# 如果当前已经登录，则跳转到主页
	if current_user.is_authenticated:
		return redirect(url_for('blog.index'))
	form = LoginForm()
	if form.validate_on_submit():
		username = form.username.data
		password = form.password.data
		remember = form.remember.data
		logger.debug('admin.username = ' + str(username))
		admin = Admin.query.filter_by(username=username).first()
		if admin:
			# 验证账号和密码是否匹配
			if username == admin.username and admin.validate_password_hash(password):
				logger.debug('login success')
				# 传入remember参数，表示是否记得长时间登录
				login_user(admin, remember)
				flash('Welcome back', 'info')
				return redirect_back()
			logger.debug('login fail')
			logger.debug(f'username is right ? {username},----{admin.username}')
			logger.debug('password is right ? ' + str(admin.validate_password_hash(password)))
		else:
			flash('No account.', 'warning')
	logger.debug('redirect to login.html')
	# 没有登录，则跳转到登录页面
	return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
	logger.debug('user logout')
	# 退出，详细可以查看代码，很容易理解
	logout_user()
	flash('Logout success.', 'info')
	return redirect(url_for('blog.index'))
