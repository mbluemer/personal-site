#!/usr/bin/env python3

from aws_cdk import core

from stacks.blog_stack import BlogStack
from stacks.hosted_zone_stack import HostedZoneStack

DOMAIN_NAME = 'theblue.dev'

env = core.Environment(account='974155864450', region='us-east-1')

app = core.App()
hosted_zone_stack = HostedZoneStack(app, 'HostedZoneStack', env=env,
    domain_name=DOMAIN_NAME)
BlogStack(app, 'Blog', env=env,
    hosted_zone=hosted_zone_stack.hosted_zone,
    domain_name=DOMAIN_NAME)

app.synth()
