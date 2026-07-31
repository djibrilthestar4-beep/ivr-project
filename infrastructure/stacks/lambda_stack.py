"""
Lambda Stack
------------
Defines the Python Lambda functions invoked by Amazon Connect contact
flows (via "Invoke AWS Lambda function" blocks). Each function lives in
its own folder under /lambda with its own handler + requirements.txt.
"""

from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_iam as iam,
)
from constructs import Construct


class LambdaStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        execution_role: iam.Role,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda: looks up customer info (e.g. from a CRM/DB) to personalize
        # the call -- typically called early in the contact flow.
        self.get_customer_info_fn = _lambda.Function(
            self,
            "GetCustomerInfoFunction",
            function_name="ivr-get-customer-info",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("../lambda/get_customer_info"),
            role=execution_role,
            timeout=Duration.seconds(8),
            memory_size=128,
            environment={
                "LOG_LEVEL": "INFO",
            },
        )

        # Lambda: decides which queue/agent to route the caller to, based
        # on business hours, IVR menu selection, customer tier, etc.
        self.route_to_agent_fn = _lambda.Function(
            self,
            "RouteToAgentFunction",
            function_name="ivr-route-to-agent",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("../lambda/route_to_agent"),
            role=execution_role,
            timeout=Duration.seconds(8),
            memory_size=128,
            environment={
                "LOG_LEVEL": "INFO",
            },
        )

        # Grant Amazon Connect permission to invoke both functions.
        # This adds the resource-based policy Connect needs -- without
        # this, the contact flow's Lambda block will fail at runtime.
        for fn in (self.get_customer_info_fn, self.route_to_agent_fn):
            fn.add_permission(
                "AllowConnectInvoke",
                principal=iam.ServicePrincipal("connect.amazonaws.com"),
            )
