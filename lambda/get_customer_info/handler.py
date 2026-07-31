"""
get_customer_info Lambda
-------------------------
Invoked early in the Connect contact flow (via an "Invoke AWS Lambda
function" block) to look up the caller's info -- e.g. by matching their
ANI (phone number) against a customer database -- so the flow can
personalize greetings, skip redundant menu options, or route VIPs faster.

Connect passes the full contact + queue + system attributes as the event.
The most commonly used fields are under event["Details"]["ContactData"].
"""

import logging
import os

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


def lambda_handler(event, context):
    logger.info("Received event: %s", event)

    contact_data = event.get("Details", {}).get("ContactData", {})
    caller_number = contact_data.get("CustomerEndpoint", {}).get("Address")

    if not caller_number:
        logger.warning("No caller number found in event")
        return _response(found=False)

    customer = _lookup_customer(caller_number)

    if customer is None:
        return _response(found=False)

    return _response(
        found=True,
        customer_id=customer["id"],
        customer_name=customer["name"],
        customer_tier=customer["tier"],
    )


def _lookup_customer(phone_number: str):
    """
    Replace with a real lookup (DynamoDB, RDS, external CRM API, etc).
    Returning a stub here so the flow can be wired up and tested end-to-end
    before the real data source is connected.
    """
    # TODO: implement real lookup, e.g.:
    # table = boto3.resource("dynamodb").Table("CustomerLookup")
    # result = table.get_item(Key={"phone_number": phone_number})
    # return result.get("Item")
    return None


def _response(found: bool, **fields):
    """
    Amazon Connect Lambda blocks expect a flat dict of string values in
    the response -- these become available in the contact flow as
    $.External attributes. Keep values JSON-serializable strings/numbers.
    """
    response = {"found": str(found)}
    response.update({k: str(v) for k, v in fields.items()})
    return response
