# IVR Project — Amazon Connect + Python + CDK

## Structure

```
connect-flows/       Exported Contact Flow JSON (for reference/diffing)
lambda/               Python Lambda functions invoked by Connect flows
  get_customer_info/  Looks up caller info to personalize the call
  route_to_agent/      Decides which queue to route the caller to
  shared/               Utilities shared across Lambda functions
infrastructure/        CDK app (Python) provisioning Connect + Lambda + IAM
  stacks/
    iam_stack.py         Execution roles / policies
    lambda_stack.py       Lambda function definitions
    connect_stack.py       Connect instance + contact flow association
scripts/               Helper scripts (export/import Connect flows)
tests/                  Unit tests (Lambda) and infra tests (CDK)
config/                 Environment variable templates
```

## Prerequisites

- Python 3.12
- AWS CLI configured with credentials (`aws configure`)
- AWS CDK CLI: `npm install -g aws-cdk`
- An AWS account bootstrapped for CDK: `cdk bootstrap`

## Setup

```bash
# Infra dependencies
cd infrastructure
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Top-level dev dependencies (from repo root)
cd ..
pip install -r requirements.txt
```

## Deploying

```bash
cd infrastructure
cdk synth                  # sanity-check the generated CloudFormation
cdk deploy --all -c connect_instance_alias=ivr-dev -c region=us-east-1
```

This provisions, in order:
1. `IvrIamStack` — Lambda execution role
2. `IvrLambdaStack` — the two Lambda functions, with permission for Connect to invoke them
3. `IvrConnectStack` — the Connect instance (contact flow association is commented out until you've exported a real flow — see `connect-flows/README.md`)

## Wiring Lambdas into a contact flow

After `cdk deploy`, note the deployed function ARNs (CDK prints them, or check the Lambda console). In the Amazon Connect admin console's contact flow designer:

1. Add an **"Invoke AWS Lambda function"** block
2. Select `ivr-get-customer-info` or `ivr-route-to-agent`
3. Reference the returned attributes downstream using `$.External.<key>`

## Local testing

```bash
pytest tests/
```

Lambda handlers take a raw `event`/`context` pair, so you can invoke them directly in tests with a sample Connect event (see `tests/unit/` — add sample event fixtures as you build out flows).

## Next steps

- [ ] Implement real customer lookup in `get_customer_info/handler.py` (swap out the stub)
- [ ] Export your first real contact flow from the Connect console into `connect-flows/`
- [ ] Uncomment and wire up the `CfnContactFlow` resource in `connect_stack.py`
- [ ] Add DynamoDB/RDS permissions to `iam_stack.py` once you pick a data store
- [ ] Fill in `tests/unit/` with handler tests using sample Connect event payloads
