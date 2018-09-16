#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from Blue2Blog.extensions import db


class Admin(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20))
	password_hash = db.Column(db.String(128))
	blog_title = db.Column(db.String(60))
	blog_sub_title = db.Column(db.String(100))
	name = db.Column(db.String(30))
	about = db.Column(db.Text)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def validate_password_hash(self, password):
		return check_password_hash(self.password_hash, password)

	def __str__(self):
		return f'username={self.username},name={self.name}'


class Category(db.Model):
	"""分类"""
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(30), unique=True)
	posts = db.relationship('Post', back_populates='category')


class Post(db.Model):
	"""文章"""
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(60))
	body = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow)
	category_id = db.Column(db.Integer, db.ForeignKey('category.id'), default=0)
	category = db.relationship('Category', back_populates='posts')
	comment_enabled = db.Column(db.Boolean, default=True)

	# 当删除文章时，评论也全部删除
	comments = db.relationship('Comment', backref='post', cascade='all')

	def __str__(self):
		return f'id={self.id},title={self.title},category_id={self.category_id}'


class Comment(db.Model):
	"""评论"""
	id = db.Column(db.Integer, primary_key=True)
	author = db.Column(db.String(30))
	email = db.Column(db.String(254))
	site = db.Column(db.String(255))
	body = db.Column(db.Text)
	# 是否是管理员的评论
	from_admin = db.Column(db.Boolean, default=False)
	# 该评论是否通过审核
	reviewed = db.Column(db.Boolean, default=False)
	# 时间
	timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
	# 关联的博客的id
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
	# post = db.relationship('Post', back_populates='comments')

	# 给评论添加级联关系，可以回复评论
	# 关联自身
	replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
	# remote_side，建立多对一的关系
	# 建立层级关系，每个评论对象都可以包含多个子评论
	replied = db.relationship('Comment', back_populates='replies', remote_side=[id])
	replies = db.relationship('Comment', back_populates='replied', cascade='all')
