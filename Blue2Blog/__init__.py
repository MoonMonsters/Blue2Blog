#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import click
from flask import Flask
from flask import render_template

from Blue2Blog.settings import config
from Blue2Blog.blueprints.admin import admin_bp
from Blue2Blog.blueprints.auth import auth_bp
from Blue2Blog.blueprints.blog import blog_bp
from Blue2Blog.extensions import bootstrap, db, moment, mail, ckeditor, login_manager
from Blue2Blog.fakes import fake_admin, fake_categories, fake_comments, fake_posts
from Blue2Blog.models import Admin, Category
from Blue2Blog.emails import send_new_comment_mail
from Blue2Blog.utils import logger


def create_app(config_name=None):
	if config_name is None:
		# 从环境读取config的名称
		config_name = os.getenv("FLASK_CONFIG", "development")

	app = Flask("Blue2Blog")
	# 配置需要的环境
	app.config.from_object(config[config_name])

	register_blueprints(app)
	register_commands(app)
	register_errors(app)
	register_extensions(app)
	register_shell_context(app)
	register_template_context(app)

	return app


def register_blueprints(app):
	# 注册蓝本
	app.register_blueprint(admin_bp, url_prefix="/admin")
	app.register_blueprint(auth_bp, url_prefix="/auth")
	app.register_blueprint(blog_bp)


def register_extensions(app):
	# 初始化第三方库
	bootstrap.init_app(app)
	db.init_app(app)
	moment.init_app(app)
	mail.init_app(app)
	ckeditor.init_app(app)
	login_manager.init_app(app)


def register_shell_context(app):
	# 使用shell时传入参数
	@app.shell_context_processor
	def make_shell_context():
		return dict(db=db)


def register_template_context(app):
	@app.context_processor
	def make_template_context():
		admin = Admin.query.first()
		categories = Category.query.order_by(Category.name).all()
		return dict(admin=admin, categories=categories)


def register_errors(app):
	# 自定义常见错误处理
	@app.errorhandler(404)
	def bad_request(e):
		return render_template("errors/400.html"), 400


def register_commands(app):
	"""
	该函数下的内部函数，都可以使用使用  flask + 函数名称 执行
	"""

	@app.cli.command()
	@click.option(
		"--category", default=10, help="Quantity of categories, default is 10"
	)
	@click.option("--post", default=50, help="Quantity of posts, default is 50")
	@click.option("--comment", default=500, help="Quantity of comments, default is 500")
	def forge(category, post, comment):
		"""
		创建测试数据
		"""
		db.drop_all()
		db.create_all()

		click.echo("Generating the admin")
		fake_admin()

		click.echo("Generating %d categories" % category)
		fake_categories(category)

		click.echo("Generating %d posts" % post)
		fake_posts(post)

		click.echo("Generating %d comments" % comment)
		fake_comments()

		click.echo("All Done...")

	@app.cli.command()
	def send_email():
		"""
		测试邮件功能
		"""
		click.echo("Send a new mail")
		from Blue2Blog.models import Post

		post = Post.query.get(1)
		send_new_comment_mail(post)

	@app.cli.command()
	# prompt: 将提示信息的首字母大写，例如username -> Username
	# help：提示消息
	# hide_input: 隐藏输入的字符串
	# confirmation_prompt: 再次输入
	@click.option("--username", prompt=True, help="The username used to login")
	@click.option(
		"--password",
		prompt=True,
		hide_input=True,
		confirmation_prompt=True,
		help="The password used to login",
	)
	def init_admin(username, password):
		"""
		创建admin账号，如果已经有了，则覆盖
		"""

		logger.debug("admin.username = " + str(username))

		click.echo("Init the database")
		db.create_all()

		admin = Admin.query.first()
		if admin is None:
			click.echo("The admin is not exists, create")
			admin = Admin(
				username=username,
				blog_title="Blue2Blog",
				blog_sub_title="I am a serious man.",
				about="Nothing of you",
			)
			admin.set_password(password)
		else:
			click.echo('The admin is exists, update')
			admin.username = username
			admin.set_password(password)
		db.session.add(admin)
		category = Category.query.first()
		if category is None:
			click.echo("Creating the default category...")
			category = Category(name="default")
			db.session.add(category)

		db.session.commit()
		click.echo("Init_admin done.")
