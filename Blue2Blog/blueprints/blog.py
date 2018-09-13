#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, current_app
from flask import render_template, request

from Blue2Blog.models import Post, Category, Comment

blog_bp = Blueprint('blog', __name__)


# 需要构建两个route
@blog_bp.route('/', defaults={'page': 1})
@blog_bp.route('/page/<int:page>')
def index(page):
	# 得到当前页数
	# page = request.args.get('page', 1, type=int)
	# 每一页的数量
	per_page = current_app.config.get('BLUE2BLOG_POST_PER_PAGE', 15)
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
	posts = pagination.items

	# posts = Post.query.order_by(Post.timestamp.desc()).all()
	context = {}
	context.update(posts=posts)
	context.update(pagination=pagination)

	return render_template('blog/index.html', **context)


@blog_bp.route('/about')
def about():
	return render_template('blog/about.html')


@blog_bp.route('/category/<int:category_id>')
def show_category(category_id):
	category = Category.query.get_or_404(category_id)
	page = request.args.get('page', 1, type=int)
	per_page = current_app.config.get('BLUE2BLOG_POST_PER_PAGE', 15)
	pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
	posts = pagination.items
	context = {}
	context.update(posts=posts)
	context.update(category=category)
	context.update(pagination=pagination)
	return render_template('blog/category.html', **context)


@blog_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
	# 博客内容
	post = Post.query.get_or_404(post_id)

	page = request.args.get('page', 1, type=int)
	per_page = current_app.config['BLUE2BLOG_COMMENT_PER_PAGE']
	pagination = Comment.query.with_parent(post).filter_by(reviewed=True).order_by(Comment.timestamp.asc()).paginate(
		page, per_page)
	# 获取文章评论
	comments = pagination.items

	context = {}
	context.update(post=post)
	context.update(comments=comments)
	context.update(pagination=pagination)
	return render_template('blog/post.html', **context)


@blog_bp.route('/comment/<int:comment_id>', methods=['GET', 'POST'])
def reply_comment(comment_id):
	pass
