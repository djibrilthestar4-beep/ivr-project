#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.iam_stack import IamStack
from stacks.lambda_stack import LambdaStack
from stacks.connect_stack import ConnectStack

app = cdk.App()

env = cdk.Environment(
    account=app.node.try_get_context("account"),
    region=app.node.try_get_context("region") or "us-east-1",
)

iam_stack = IamStack(app, "IvrIamStack", env=env)

lambda_stack = LambdaStack(
    app,
    "IvrLambdaStack",
    execution_role=iam_stack.lambda_execution_role,
    env=env,
)
lambda_stack.add_dependency(iam_stack)

connect_stack = ConnectStack(app, "IvrConnectStack", env=env)

app.synth()
