"""
IAM Stack
---------
Defines shared IAM roles/policies used by Lambda functions invoked from
Amazon Connect contact flows. Kept separate from lambda_stack.py so that
permission changes can be reviewed/rolled back independently of function
code or infra changes.
"""

from aws_cdk import (
    Stack,
    aws_iam as iam,
)
from constructs import Construct


class IamStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Base execution role for all IVR-related Lambdas.
        # Add resource-specific policies (DynamoDB, RDS, Secrets Manager, etc.)
        # as your Lambdas need them -- avoid using AWS-managed "FullAccess"
        # policies in production.
        self.lambda_execution_role = iam.Role(
            self,
            "IvrLambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            description="Execution role for IVR Lambda functions invoked by Amazon Connect",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
            ],
        )

        # Example: allow Lambdas to read/write a customer-lookup table.
        # Uncomment and adjust once you have a real table/resource ARN.
        #
        # self.lambda_execution_role.add_to_policy(
        #     iam.PolicyStatement(
        #         actions=["dynamodb:GetItem", "dynamodb:PutItem"],
        #         resources=["arn:aws:dynamodb:REGION:ACCOUNT_ID:table/CustomerLookup"],
        #     )
        # )

        # Role that Amazon Connect assumes to invoke Lambda functions.
        # CDK's lambda.grant_invoke() (used in lambda_stack.py) handles the
        # resource-based policy on the function itself; this role is here
        # in case you need a Connect-side IAM role for other integrations
        # (e.g. Kinesis Data Streams for contact trace records).
        self.connect_service_role = iam.Role(
            self,
            "ConnectServiceRole",
            assumed_by=iam.ServicePrincipal("connect.amazonaws.com"),
            description="Service role for Amazon Connect instance integrations",
        )
