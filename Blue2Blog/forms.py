#!/usr/bin/env python
# -*- coding: utf-8 -*-


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length, ValidationError, Email, URL, Optional
from flask_ckeditor import CKEditorField

from Blue2Blog.models import Category


class LoginForm(FlaskForm):
	"""登录"""
	username = StringField("Username", validators=[DataRequired(), Length(1, 20)])
	password = PasswordField("Password", validators=[DataRequired(), Length(1, 128)])
	remember = BooleanField("Remember me")
	submit = SubmitField("Login")


class PostForm(FlaskForm):
	"""发表文章"""
	title = StringField("Title", validators=[DataRequired(), Length(1, 60)])
	# 默认选中第一项
	category = SelectField("Category", coerce=int, default=1)
	body = CKEditorField("Body", validators=[DataRequired()])
	submit = SubmitField("Publish")

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# 设置SelectField的可选值
		# Flask-SQLAlchemy需要依赖上下文才能正常工作，所以才设置choices放到__init__中来
		self.category.choices = [
			(category.id, category.name)
			for category in Category.query.order_by(Category.name).all()
		]


class CategoryForm(FlaskForm):
	"""分类"""
	name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
	submit = SubmitField()

	def validate_name(self, field):
		if Category.query.filter_by(name=field.data).first():
			raise ValidationError('Name already in use')


class CommentForm(FlaskForm):
	"""评论"""
	author = StringField('Name', validators=[DataRequired(), Length(1, 30)])
	email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 254)])
	site = StringField('Site', validators=[Optional(), URL(), Length(0, 255)])
	body = TextAreaField('Comment', validators=[DataRequired()])
	submit = SubmitField()


class AdminCommentForm(FlaskForm):
	"""管理员可以不需要填写这些项"""
	author = HiddenField()
	email = HiddenField()
	site = HiddenField()
