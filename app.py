#!/usr/bin/env python3

from aws_cdk import core

from blog_stack.blog_stack import BlogStack

env = core.Environment(account='974155864450', region='us-east-1')

app = core.App()
BlogStack(app, 'Blog', env=env)

app.synth()
