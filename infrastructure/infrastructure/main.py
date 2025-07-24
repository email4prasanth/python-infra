#!/usr/bin/env python3
import aws_cdk as cdk
from infrastructure.vpc_stack import VPCStack
from infrastructure.security_group import SecurityGroupStack

app = cdk.App()

# Get environment from context (default: dev)
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

# Add dependency - security groups depend on VPC
sg_stack.add_dependency(vpc_stack)

app.synth()