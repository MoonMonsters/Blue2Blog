#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
创建测试用例
"""
import random

from faker import Faker

from Blue2Blog.models import Admin, Post, Comment, Category
from Blue2Blog.extensions import db

faker = Faker()


def fake_admin():
	"""
	创建测试用户
	"""
	admin = Admin(
		username='admin001',
		blog_title='Blue2Blog',
		blog_sub_title='This is a flask blog',
		name='ChenTao',
		about='I am a test admin, having no permissions to delete/create/modify anything',
	)
	admin.set_password('123456')
	db.session.add(admin)
	db.session.commit()


def fake_categories(count=10):
	"""
	添加category数据
	"""
	category = Category(name='default')
	db.session.add(category)

	for _ in range(count):
		category = Category(name=faker.word())
		db.session.add(category)

		try:
			# category中设置成不能重复，而faker生成的word是可能重复的
			# 如果提交出错，则回滚
			db.session.commit()
		except InterruptedError:
			db.session.rollback()


def fake_posts(count=50):
	"""
	创建测试文章
	"""
	for _ in range(count):
		post = Post(
			title=faker.sentence(),
			body=faker.text(2000),
			category=Category.query.get(random.randint(1, Category.query.count())),
			timestamp=faker.date_time_this_year()
		)
		db.session.add(post)
	db.session.commit()


def fake_comments(count=500):
	"""
	创建测试评论
	"""
	for _ in range(count):
		# 已审核的评论
		comment = Comment(
			author=faker.name(),
			email=faker.email(),
			site=faker.url(),
			body=faker.sentence(),
			timestamp=faker.date_time_this_year(),
			reviewed=True,
			post=Post.query.get(random.randint(1, Post.query.count()))
		)
		db.session.add(comment)

	salt = int(count * 0.1)
	for _ in range(salt):
		# 为审核评论
		comment = Comment(
			author=faker.name(),
			email=faker.email(),
			site=faker.url(),
			body=faker.sentence(),
			timestamp=faker.date_time_this_year(),
			reviewed=True,
			post=Post.query.get(random.randint(1, Post.query.count()))
		)
		db.session.add(comment)

		# 管理员发表的评论
		comment = Comment(
			author=faker.name(),
			email=faker.email(),
			site=faker.url(),
			body=faker.sentence(),
			timestamp=faker.date_time_this_year(),
			reviewed=True,
			from_admin=True,
			post=Post.query.get(random.randint(1, Post.query.count()))
		)
		db.session.add(comment)

	db.session.commit()
