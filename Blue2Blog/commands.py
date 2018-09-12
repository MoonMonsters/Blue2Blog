#!/usr/bin/env python
# -*- coding: utf-8 -*-


import click
from flask import Flask

from Blue2Blog.fakes import fake_admin, fake_categories, fake_comments, fake_posts
from Blue2Blog.extensions import db


def register_commands(app: Flask):
	@app.cli.command()
	@click.option('--category', default=10, help='Quantity of categories, default is 10')
	@click.option('--post', default=50, help='Quantity of posts, default is 50')
	@click.option('--comment', default=500, help='Quantity of comments, default is 500')
	def forge(category, post, comment):
		db.drop_all()
		db.create_all()

		click.echo('Generating the admin')
		fake_admin()

		click.echo('Generating %d categories' % category)
		fake_categories(category)

		click.echo('Generating %d posts' % post)
		fake_posts(post)

		click.echo('Generating %d comments' % comment)
		fake_comments()

		click.echo('All Done...')
