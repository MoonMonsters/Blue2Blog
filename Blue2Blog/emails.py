#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Thread

from flask import url_for, current_app
from flask_mail import Message

from Blue2Blog.extensions import mail


def _send_async_mail(app, message):
	# 需要在上下文中操作
	with app.app_context():
		mail.send(message)


def send_mail(subject, to, html):
	# 在新建的线程中需要真正的程序对象来创建上下文，所以不能直接传入current_app
	# 传入调用_get_current_object()的方法获取到的被代理的程序实例
	app = current_app._get_current_object()
	message = Message(subject, recipients=[to], html=html)
	thr = Thread(target=_send_async_mail, args=[app, message])
	# 在子线程中发送邮件
	thr.start()
	return thr


def send_new_comment_mail(post):
	# 获取决定url，并且点击链接时直接跳转到评论出
	post_url = url_for("blog.show_post", post_id=post.id, _external=True) + "#comments"
	send_mail(
		subject="New Comment",
		to=current_app.config["BLUE2BLOG_EMAIL"],
		html="<p>New comment in post <i>%s</i>, click the link below to check:</p>"
		     '<p><a href="%s">%s</a></p>'
		     '<p><small style="color:#868e96">Do not reply this mail.</small></p>'
		     % (post.title, post_url, post_url),
	)


def send_new_reply_mail(comment):
	post_url = (
			url_for("blog.show_post", post_id=comment.post_id, _external=True) + "#comments"
	)
	send_mail(
		subject="New Comment",
		to=comment.email,
		html="<p>New reply for the comment in post <i>%s</i>, click the link below to check:</p>"
		     '<p><a href="%s">%s</a></p>'
		     '<p><small style="color:#868e96">Do not reply this mail.</small></p>'
		     % (comment.post.title, post_url, post_url),
	)
