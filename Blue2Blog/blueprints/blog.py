#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, current_app
from flask import render_template, request, url_for, flash, redirect, abort, make_response
from flask_login import current_user
from sqlalchemy.orm import joinedload_all

from Blue2Blog.models import Post, Category, Comment
from Blue2Blog.forms import AdminCommentForm, CommentForm
from Blue2Blog.emails import send_new_comment_mail, send_new_reply_mail
from Blue2Blog.extensions import db
from Blue2Blog.utils import logger, redirect_back
from Blue2Blog.utils import CacheUtil

blog_bp = Blueprint("blog", __name__)


# 需要构建两个route
@blog_bp.route("/", defaults={"page": 1})
@blog_bp.route("/page/<int:page>")
def index(page):
	logger.debug('request.url = ' + str(request.url))
	# 得到当前页数
	# page = request.args.get('page', 1, type=int)
	# 每一页的数量，从配置中读取，如果没有配置，则设置为15
	per_page = current_app.config.get("BLUE2BLOG_POST_PER_PAGE", 15)
	# 从SQLAlchemy中获取Pagination对象，分页对象
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
		page, per_page=per_page
	)
	# 获取分页中的博客数据
	posts = pagination.items

	# 传递数据到html中
	# posts = Post.query.order_by(Post.timestamp.desc()).all()
	context = {}
	context.update(posts=posts)
	context.update(pagination=pagination)

	return render_template("blog/index.html", **context)


@blog_bp.route("/about")
def about():
	logger.debug('request.url = ' + str(request.url))
	return render_template("blog/about.html")


@blog_bp.route("/category/<int:category_id>")
def show_category(category_id):
	logger.debug('request.url = ' + str(request.url))
	# 根据id获取Category对象
	category = Category.query.get_or_404(category_id)
	page = request.args.get("page", 1, type=int)
	per_page = current_app.config.get("BLUE2BLOG_POST_PER_PAGE", 15)
	# with_parent
	# order_by: 传入排序的属性
	# paginate: 第一个参数是分页后的第n页，第二个参数是取出n个数据
	pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
	posts = pagination.items
	context = {}
	context.update(posts=posts)
	context.update(category=category)
	context.update(pagination=pagination)
	return render_template("blog/category.html", **context)


@blog_bp.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
	logger.debug('request.url = ' + str(request.url))

	try:
		# 如果文章没有缓存，那么久会报错
		post = CacheUtil.get_posts_from_cache(post_id)
	except TypeError:
		# 博客内容
		# 文章没有缓存，就从数据库中读取，并且缓存
		post = Post.query.get_or_404(post_id)
		category = Category.query.get(post.category.id)
		CacheUtil.save_posts_to_cache(post, category)

	# 根据post_id获取文章评论
	page = request.args.get("page", 1, type=int)
	per_page = current_app.config["BLUE2BLOG_COMMENT_PER_PAGE"]
	if current_user.is_authenticated:
		# 如果管理员已经登录，那么将显示所有的评论
		pagination = (
			Comment.query.options(joinedload_all('*')).with_parent(post)
				.order_by(Comment.timestamp.asc())
				.paginate(page, per_page)
		)
	else:
		pagination = (
			Comment.query.options(joinedload_all('*')).with_parent(post)
				.filter_by(reviewed=True)  # 没有登录，则过滤出已经审核的评论
				.order_by(Comment.timestamp.asc())
				.paginate(page, per_page)
		)
	comments = pagination.items

	# 如果当前用户已经登录
	if current_user.is_authenticated:
		# if False:
		# 如果管理员登录了，那么久使用AdminCommentForm
		form = AdminCommentForm()
		# 直接从登录的管理员中取出需要的数据
		form.author.data = current_user.name
		form.email.data = current_app.config["BLUE2BLOG_EMAIL"]
		form.site.data = url_for("blog.index", _external=True)
		from_admin = True
		# 管理员发表的评论不需要审核
		reviewed = True
	else:
		# 如果没有登录，则构建CommentForm对象
		form = CommentForm()
		from_admin = False
		reviewed = False
	# 从提交的POST请求中读取form数据
	if form.validate_on_submit():
		post = Post.query.get(post.id)
		author = form.author.data
		email = form.email.data
		site = form.site.data
		body = form.body.data
		comment = Comment(
			author=author,
			email=email,
			site=site,
			body=body,
			from_admin=from_admin,
			post=post,
			reviewed=reviewed,
		)

		# 如果是回复某一条评论的话，获取评论的id
		# 判断是否从reply_comment转发过来的
		# 如果有数据，则说明是对评论进行评论
		comment_id = request.args.get('reply')
		logger.debug('comment_id = ' + str(comment_id))
		if comment_id:
			# 获取被评论的Comment对象
			replied_comment = Comment.query.options(joinedload_all('*')).get_or_404(comment_id)
			logger.debug('replied_comment.id = ' + str(replied_comment.id))
			# 管理评论与被评论对象
			comment.replied_id = replied_comment.id
		# send_new_reply_mail(comment)

		db.session.add(comment)
		db.session.commit()

		if current_user.is_authenticated:
			# if False:
			flash("Comment published.", "success")
		else:
			flash("Thanks, your comment will be published after reviewed.", "info")
		# send_new_comment_mail(post)

		return redirect(url_for("blog.show_post", post_id=post_id))

	context = {}
	context.update(post=post)
	context.update(comments=comments)
	context.update(pagination=pagination)
	context.update(form=form)
	return render_template("blog/post.html", **context)


@blog_bp.route("/reply/comment/<int:comment_id>", methods=["GET", "POST"])
def reply_comment(comment_id):
	logger.debug('request.url = ' + str(request.url))
	comment = Comment.query.get_or_404(comment_id)
	url = redirect(
		url_for(
			"blog.show_post",
			# 博客id
			post_id=comment.post_id,
			# 回复的评论id
			reply=comment_id,
			# 回复评论，发表该评论的作者名字
			# 会在博客页面下方的评论表单上加上作者名字
			author=comment.author,
		)
		+ "#comment-form"
	)
	logger.debug('redirect.url = ' + str(url))
	# 转发到show_post中去处理
	return url


@blog_bp.route('/change-theme/<theme_name>')
def change_theme(theme_name):
	logger.debug('request.url = ' + str(request.url))
	"""
	更改博客主题
	:param theme_name: 主题名称
	"""
	if theme_name not in current_app.config['BLUE2BLOG_THEMES'].keys():
		abort(404)
	response = make_response(redirect_back())
	logger.debug('response = ' + str(response))
	response.set_cookie('theme', theme_name, max_age=30 * 24 * 60 * 60)
	return response
