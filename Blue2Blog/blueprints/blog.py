#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, current_app
from flask import render_template, request, url_for, flash, redirect
from flask_login import current_user

from Blue2Blog.models import Post, Category, Comment
from Blue2Blog.forms import AdminCommentForm, CommentForm
from Blue2Blog.emails import send_new_comment_mail, send_new_reply_mail
from Blue2Blog.extensions import db

blog_bp = Blueprint("blog", __name__)


# 需要构建两个route
@blog_bp.route("/", defaults={"page": 1})
@blog_bp.route("/page/<int:page>")
def index(page):
	# 得到当前页数
	# page = request.args.get('page', 1, type=int)
	# 每一页的数量
	per_page = current_app.config.get("BLUE2BLOG_POST_PER_PAGE", 15)
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
		page, per_page=per_page
	)
	posts = pagination.items

	# posts = Post.query.order_by(Post.timestamp.desc()).all()
	context = {}
	context.update(posts=posts)
	context.update(pagination=pagination)

	return render_template("blog/index.html", **context)


@blog_bp.route("/about")
def about():
	return render_template("blog/about.html")


@blog_bp.route("/category/<int:category_id>")
def show_category(category_id):
	category = Category.query.get_or_404(category_id)
	page = request.args.get("page", 1, type=int)
	per_page = current_app.config.get("BLUE2BLOG_POST_PER_PAGE", 15)
	pagination = (
		Post.query.with_parent(category)
			.order_by(Post.timestamp.desc())
			.paginate(page, per_page=per_page)
	)
	posts = pagination.items
	context = {}
	context.update(posts=posts)
	context.update(category=category)
	context.update(pagination=pagination)
	return render_template("blog/category.html", **context)


@blog_bp.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
	# 博客内容
	post = Post.query.get_or_404(post_id)

	page = request.args.get("page", 1, type=int)
	per_page = current_app.config["BLUE2BLOG_COMMENT_PER_PAGE"]
	pagination = (
		Comment.query.with_parent(post)
			# 过滤出已经审核的评论
			.filter_by(reviewed=True)
			.order_by(Comment.timestamp.asc())
			.paginate(page, per_page)
	)
	# 获取文章评论
	comments = pagination.items

	# 如果当前用户已经登录
	# if current_user.is_authenticated:
	if False:
		form = AdminCommentForm()
		form.author.data = current_user.name
		form.email.data = current_app.config["BLUE2BLOG_EMAIL"]
		form.site.data = url_for("blog.index")
		from_admin = True
		reviewed = True
	else:
		form = CommentForm()
		from_admin = False
		reviewed = False

	if form.validate_on_submit():
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

		replied_id = request.args.get('reply')
		if replied_id:
			replied_comment = Comment.query.get_or_404(replied_id)
			comment.replied_id = replied_comment
			# send_new_reply_mail(comment)

		db.session.add(comment)
		db.session.commit()

		# if current_user.is_authenticated:
		if False:
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
	comment = Comment.query.get_or_404(comment_id)
	return redirect(
		url_for(
			"blog.show_post",
			post_id=comment.post_id,
			reply=comment_id,
			author=comment.author,
		)
		+ "#comment-form"
	)
