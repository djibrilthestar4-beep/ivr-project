#!/usr/bin/env python3
"""
export_flows.py
----------------
Pulls contact flow(s) from an Amazon Connect instance and writes them as
formatted JSON files into /connect-flows, so they can be diffed and
version-controlled in Git.

Amazon Connect stores flow content as an escaped JSON *string* (accessible
via the "Show additional flow information" > export in the console, or via
the DescribeContactFlow API). This script un-escapes it and pretty-prints
it so Git diffs are actually readable.

Usage:
    # Export every flow in the instance
    python scripts/export_flows.py --instance-id <INSTANCE_ID>

    # Export a single named flow
    python scripts/export_flows.py --instance-id <INSTANCE_ID> --name "MainMenu"

Requires:
    pip install boto3
    AWS credentials configured (aws configure / env vars / SSO)
    IAM permissions: connect:ListContactFlows, connect:DescribeContactFlow
"""

import argparse
import json
import os
import re
import sys

import boto3

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "connect-flows")


def slugify(name: str) -> str:
    """Turn a flow name into a filesystem-safe filename."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()
    return slug or "unnamed-flow"


def list_flows(client, instance_id: str):
    flows = []
    paginator = client.get_paginator("list_contact_flows")
    for page in paginator.paginate(InstanceId=instance_id):
        flows.extend(page["ContactFlowSummaryList"])
    return flows


def export_flow(client, instance_id: str, contact_flow_id: str, name: str):
    detail = client.describe_contact_flow(
        InstanceId=instance_id,
        ContactFlowId=contact_flow_id,
    )["ContactFlow"]

    # 'Content' comes back as a JSON string -- parse then re-dump with
    # indentation so it diffs cleanly in Git.
    content = json.loads(detail["Content"])

    output = {
        "Name": detail["Name"],
        "Type": detail["Type"],
        "Description": detail.get("Description", ""),
        "ContactFlowId": detail["Id"],
        "Content": content,
    }

    filename = f"{slugify(name)}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(filepath, "w") as f:
        json.dump(output, f, indent=2)
        f.write("\n")

    print(f"Exported '{name}' -> connect-flows/{filename}")


def main():
    parser = argparse.ArgumentParser(description="Export Amazon Connect contact flows to JSON")
    parser.add_argument("--instance-id", required=True, help="Amazon Connect instance ID")
    parser.add_argument("--name", help="Export only the flow with this exact name")
    parser.add_argument("--region", default=None, help="AWS region (defaults to your configured region)")
    args = parser.parse_args()

    client = boto3.client("connect", region_name=args.region)

    flows = list_flows(client, args.instance_id)
    if not flows:
        print("No contact flows found in this instance.", file=sys.stderr)
        sys.exit(1)

    if args.name:
        flows = [f for f in flows if f["Name"] == args.name]
        if not flows:
            print(f"No flow named '{args.name}' found.", file=sys.stderr)
            sys.exit(1)

    for flow in flows:
        export_flow(client, args.instance_id, flow["Id"], flow["Name"])

    print(f"\nDone. Exported {len(flows)} flow(s) to connect-flows/")


if __name__ == "__main__":
    main()
