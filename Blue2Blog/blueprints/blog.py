#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, current_app
from flask import render_template, request

from Blue2Blog.models import Post

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
	return render_template('blog/category.html')


@blog_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
	post = Post.query.get_or_404(post_id)
	context = {}
	context.update(post=post)
	return render_template('blog/post.html', **context)
