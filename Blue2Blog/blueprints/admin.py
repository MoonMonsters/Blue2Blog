#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, current_app
from flask import request, redirect, url_for, render_template, flash
from flask_login import login_required

from Blue2Blog.models import Post, Category, Comment
from Blue2Blog.utils import logger
from Blue2Blog.forms import PostForm
from Blue2Blog.extensions import db

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/post/new")
@login_required
def new_post():
	logger.debug('request.url = ' + str(request.url))
	form = PostForm()
	if form.validate_on_submit():
		title = form.title.data
		body = form.body.data
		# 根据id得到category对象
		category = Category.query.get(form.category.data)
		post = Post(title=title, body=body, category=category)

		# 添加
		db.session.add(post)
		db.session.commit()

		flash('Post created', 'success')

		logger.debug('publish a new post, id = ' + str(post.id))
		# 添加完成后跳转到博客详情页面查看具体内容
		return redirect(url_for('blog.show_post', post_id=post.id))

	return render_template('admin/new_post.html', form=form)


@admin_bp.route("/category/new")
def new_category():
	logger.debug('request.url = ' + str(request.url))
	pass


@admin_bp.route("/post/manage")
@login_required
def manage_post():
	logger.debug('request.url = ' + str(request.url))
	# 页数设置
	page = request.args.get('page', 1, type=int)
	per_page = current_app.config.get('BLUE2BLOG_MANAGE_POST_PER_PAGE', 15)
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
	posts = pagination.items
	context = dict()
	context.update(posts=posts)
	context.update(pagination=pagination)

	return render_template('admin/manage_post.html', **context)


@admin_bp.route("/category/manage")
def manage_category():
	logger.debug('request.url = ' + str(request.url))


@admin_bp.route("/manage_comment")
def manage_comment():
	logger.debug('request.url' + str(request.url))


@admin_bp.route('/post/edit/<int:post_id>')
def edit_post(post_id):
	logger.debug('request.url = ' + str(request.url))
	pass


@admin_bp.route('/post/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
	logger.debug('request.url = ' + str(request.url))


@admin_bp.route("/settings")
def settings():
	logger.debug('request.url ' + str(request.url))
