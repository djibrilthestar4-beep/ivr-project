"""
Shared utilities for IVR Lambda functions.

Copy or package this into each Lambda's deployment artifact as needed
(e.g. via a Lambda Layer, or by symlinking/bundling at build time -- CDK's
`_lambda.Code.from_asset` bundles whatever is in the function's own
folder, so for now this file is meant to be referenced when you set up
a shared Lambda Layer; see README.md in /lambda for the layer approach).
"""

from __future__ import annotations

import logging
import os


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))
    return logger


def get_contact_attributes(event: dict) -> dict:
    """Pull the custom contact attributes dict out of a Connect Lambda event."""
    return event.get("Details", {}).get("ContactData", {}).get("Attributes", {})


def get_caller_number(event: dict) -> str | None:
    """Pull the caller's phone number (ANI) out of a Connect Lambda event."""
    contact_data = event.get("Details", {}).get("ContactData", {})
    return contact_data.get("CustomerEndpoint", {}).get("Address")


def stringify_response(fields: dict) -> dict:
    """
    Amazon Connect expects Lambda response values to be strings so they can
    be stored as contact attributes. Converts all values to strings.
    """
    return {k: str(v) for k, v in fields.items()}
