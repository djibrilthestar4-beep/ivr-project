"""
Connect Stack
-------------
Defines the Amazon Connect instance and associates contact flows exported
to /connect-flows. Amazon Connect only has L1 (Cfn) CDK constructs today,
so this stack uses aws_connect.Cfn* resources directly.

NOTE: If you already have an existing Connect instance (common, since
teams often provision it once via console and reuse it), skip instance
creation below and instead import it by ARN using
`aws_connect.CfnInstance.from_instance_arn` equivalents, or simply
reference the instance ARN as a stack parameter/context value.
"""

import json
import os

from aws_cdk import (
    Stack,
    CfnParameter,
    aws_connect as connect,
)
from constructs import Construct


class ConnectStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Set via `cdk deploy -c connect_instance_alias=my-ivr-dev`
        instance_alias = self.node.try_get_context("connect_instance_alias") or "ivr-dev"

        self.instance = connect.CfnInstance(
            self,
            "IvrConnectInstance",
            attributes=connect.CfnInstance.AttributesProperty(
                inbound_calls=True,
                outbound_calls=True,
            ),
            identity_management_type="CONNECT_MANAGED",
            instance_alias=instance_alias,
        )

        # Example: register a contact flow from the exported JSON in
        # /connect-flows. Amazon Connect flow JSON exported from the
        # console needs light adaptation (Cfn expects flow content as a
        # JSON string) -- see /connect-flows/README.md for the export/
        # import workflow using scripts/export_flows.py and import_flows.py.
        #
        # flow_path = os.path.join(
        #     os.path.dirname(__file__), "..", "..", "connect-flows", "main-menu.json"
        # )
        # with open(flow_path) as f:
        #     flow_content = json.load(f)
        #
        # self.main_menu_flow = connect.CfnContactFlow(
        #     self,
        #     "MainMenuFlow",
        #     instance_arn=self.instance.attr_arn,
        #     name="MainMenu",
        #     type="CONTACT_FLOW",
        #     content=json.dumps(flow_content),
        # )
