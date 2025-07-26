#!/usr/bin/env python3
import os

import aws_cdk as cdk

from infrastructure.vpc_stack import VPCStack
from infrastructure.security_group import SecurityGroupStack
from infrastructure.compute_stack import ComputeStack


app = cdk.App()
env_name = app.node.try_get_context("env") or "dev"

# Create VPC stack
vpc_stack = VPCStack(
    app, 
    f"VPCStack-{env_name}",
    environment=env_name,
    env=cdk.Environment(account='180294218712', region='us-east-1')
    )
# Create Security Group stack
sg_stack = SecurityGroupStack(
    app,
    f"SecurityGroupStack-{env_name}",
    environment=env_name,
    vpc_id=vpc_stack.vpc.ref,
    env=cdk.Environment(account='180294218712', region='us-east-1')
)

# Create Compute stack
compute_stack = ComputeStack(
    app,
    f"ComputeStack-{env_name}",
    environment=env_name,
    # vpc_id=vpc_stack.vpc.ref,
    security_group_id=sg_stack.web_sg.attr_group_id,
    public_subnets=vpc_stack.public_subnets,
    env=cdk.Environment(account='180294218712', region='us-east-1')
)
# security groups depend on VPC
sg_stack.add_dependency(vpc_stack)
# compute_stack depends on both vpc_stack and sg_stack
compute_stack.add_dependency(vpc_stack)
compute_stack.add_dependency(sg_stack)

app.synth()
