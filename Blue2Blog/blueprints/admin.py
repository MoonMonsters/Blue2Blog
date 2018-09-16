#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from flask import Blueprint, current_app
from flask import request, redirect, url_for, render_template, flash
from flask_login import login_required

from Blue2Blog.models import Post, Category, Comment
from Blue2Blog.utils import logger, redirect_back
from Blue2Blog.forms import PostForm
from Blue2Blog.extensions import db

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/post/new", methods=['POST', 'GET'])
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


@admin_bp.route("/category/new", methods=['GET', 'POST'])
@login_required
def new_category():
	logger.debug('request.url = ' + str(request.url))

	category_name = request.args.get('category_name')
	category = Category(name=category_name)

	db.session.add(category)

	info = {}

	try:
		db.session.commit()
		info['success'] = True
		info['description'] = 'Add category success'
	except Exception as e:
		logger.debug('添加category失败: ' + str(e.args))
		info['success'] = False
		info['description'] = 'Category already exists, please input again'
		db.session.rollback()

	logger.debug('info = ' + str(json.dumps(info)))
	return json.dumps(info)


@admin_bp.route('/category/edit', methods=['POST', 'GET'])
@login_required
def edit_category():
	"""
	更新category的名称
	"""
	logger.debug('request.url = ' + str(request.url))
	# 获取id
	category_id = request.args.get('category_id')
	# 获取新的名字
	category_name = request.args.get('category_name')
	# 获取category对象
	category = Category.query.get_or_404(category_id)
	# 更新
	category.name = category_name

	info = dict()
	try:
		db.session.commit()
		info['success'] = True
		info['description'] = 'Update Success'
	except Exception as e:
		logger.debug('update category fail: ' + str(e.args))
		info['success'] = False
		info['success'] = 'Update Fail, Please try it again'

	return json.dumps(info)


@admin_bp.route('/category/delete/<int:category_id>', methods=['GET', 'POST'])
@login_required
def delete_category(category_id):
	if category_id == 1:
		flash('Can Not Delete The Default Category', 'warning')
		return redirect_back()

	category = Category.query.get_or_404(category_id)

	# 如果只是删除了category，那么post的category_id将会报错
	posts = Post.query.filter_by(category_id=category_id).all()
	# 数据库是从1开始的，前面写成了0，调试了好久
	default_category = Category.query.get(1)
	for post in posts:
		# 将所有的post的category设置为默认的
		post.category = default_category

	db.session.delete(category)
	try:
		db.session.commit()
	except Exception:
		db.session.rollback()

	return redirect_back()


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
	categories = Category.query.all()

	context = {}
	context.update(categories=categories)

	return render_template('admin/manage_category.html', **context)


@admin_bp.route("/manage_comment")
def manage_comment():
	logger.debug('request.url' + str(request.url))


@admin_bp.route('/post/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
	logger.debug('request.url = ' + str(request.url))
	form = PostForm()
	# 根据要编辑的博客id，获取Post对象
	post = Post.query.get_or_404(post_id)
	# 如果是修改文章时提交的form对象
	if form.validate_on_submit():
		# 更新post对象
		post.title = form.title.data
		post.body = form.body.data
		post.category = Category.query.get(form.category.data)
		flash('Post updated', 'success')
		# 提交
		db.session.commit()

		# 跳转到博客详细页面
		return redirect(url_for('blog.show_post', post_id=post.id))

	# 如果是跳转到编辑文章页面去，那么将post的值赋值给form对象
	# html页面中，将会显示这些值
	form.title.data = post.title
	form.body.data = post.body
	form.category.data = post.category_id
	return render_template('admin/edit_post.html', form=form)


@admin_bp.route('/post/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
	"""
	删除博客
	:param post_id: 博客id
	:return: 返回到原页面去
	"""
	logger.debug('request.url = ' + str(request.url))
	# 根据id获取，如果不存在，报404错误
	post = Post.query.get_or_404(post_id)
	# 删除
	db.session.delete(post)
	db.session.commit()
	flash('Post deleted', 'success')

	return redirect_back()


@admin_bp.route("/settings")
def settings():
	logger.debug('request.url ' + str(request.url))


@admin_bp.route('/post/comment_enabled/<int:post_id>', methods=['GET', 'POST'])
@login_required
def comment_enabled(post_id):
	logger.debug('request.url = ' + str(request.url))
	# post_id = request.args.get('post_id')
	post = Post.query.get_or_404(post_id)
	# 将comment_enabled值转成相反的即可
	if post.comment_enabled:
		flash('Comment Disabled', 'info')
		post.comment_enabled = False
	else:
		flash('Comment Enabled', 'info')
		post.comment_enabled = True
	db.session.commit()

	return redirect_back()


@admin_bp.route('/comment/delete/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def delete_comment(comment_id):
	"""
	删除评论
	:param comment_id: 评论id
	:return: 原页面
	"""
	logger.debug('request.url = ' + str(request.url))
	comment = Comment.query.get_or_404(comment_id)
	db.session.delete(comment)
	db.session.commit()

	return redirect_back()


@admin_bp.route('comment/review/<int:comment_id>', methods=['GET', 'POST'])
@login_required
def review_comment(comment_id):
	"""
	评论审核通过
	:param comment_id: 评论id
	:return: 原页面
	"""
	logger.debug('request.url = ' + str(request.url))
	comment = Comment.query.get_or_404(comment_id)
	# 更新值
	comment.reviewed = True

	db.session.commit()

	return redirect_back()
