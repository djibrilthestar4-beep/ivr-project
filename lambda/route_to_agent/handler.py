"""
route_to_agent Lambda
----------------------
Invoked after menu selection to decide which queue the caller should be
routed to -- based on IVR input, business hours, and (optionally)
customer tier from get_customer_info. The contact flow branches on this
Lambda's return value using a "Check contact attributes" or the Lambda
block's own condition outputs.
"""

import logging
import os
from datetime import datetime, time
from zoneinfo import ZoneInfo

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

BUSINESS_TZ = ZoneInfo("America/New_York")
BUSINESS_HOURS = (time(9, 0), time(18, 0))  # 9am - 6pm local

# Map of IVR menu selection (DTMF digit or Lex intent) to queue name.
MENU_TO_QUEUE = {
    "1": "BillingQueue",
    "2": "TechSupportQueue",
    "3": "SalesQueue",
}
DEFAULT_QUEUE = "GeneralQueue"
AFTER_HOURS_QUEUE = "VoicemailQueue"


def lambda_handler(event, context):
    logger.info("Received event: %s", event)

    contact_data = event.get("Details", {}).get("ContactData", {})
    attributes = contact_data.get("Attributes", {})

    menu_selection = attributes.get("menuSelection")
    customer_tier = attributes.get("customer_tier")

    if not _is_within_business_hours():
        return {"queue": AFTER_HOURS_QUEUE, "reason": "after_hours"}

    queue = MENU_TO_QUEUE.get(menu_selection, DEFAULT_QUEUE)

    # Example priority routing for VIP customers.
    if customer_tier == "VIP" and queue != AFTER_HOURS_QUEUE:
        queue = f"Priority{queue}"

    logger.info("Routing decision: queue=%s", queue)
    return {"queue": queue, "reason": "menu_selection"}


def _is_within_business_hours(now: datetime | None = None) -> bool:
    now = now or datetime.now(BUSINESS_TZ)
    start, end = BUSINESS_HOURS
    return start <= now.time() <= end
