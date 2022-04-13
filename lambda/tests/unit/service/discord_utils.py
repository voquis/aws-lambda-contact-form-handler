"""
Utility functions and constants for unit tests and integration tests
"""

import json
import httpretty

# -----------------------------------------------
# Utils
# -----------------------------------------------

def httpretty_register_discord_webhook_success():
    """
    Mock Discord webhook endpoint returning successful response
    """

    # Set up HTTP client mock to prevent communication with real backend
    httpretty.register_uri(
        httpretty.POST,
        "https://discord.com/api/webhooks/123/abc",
        status=204
    )

def httpretty_register_discord_webhook_failure():
    """
    Mock Discord webhook endpoint returning failed response
    """
    # Prepare mocked  response
    body = {
        "message": "Cannot send an empty message",
        "code": 50006
    }

    # Set up HTTP client mock to prevent communication with real backend
    httpretty.register_uri(
        httpretty.POST,
        "https://discord.com/api/webhooks/123/abc",
        status=400,
        body=json.dumps(body)
    )

def httpretty_register_discord_webhook_failure_bad_json():
    """
    Mock Discord webhook endpoint returning failed response
    """
    # Set up HTTP client mock to prevent communication with real backend
    httpretty.register_uri(
        httpretty.POST,
        "https://discord.com/api/webhooks/123/abc",
        status=400,
        body='{bad"{json'
    )

def httpretty_register_discord_webhook_unauthorised():
    """
    Mock Discord webhook endpoint returning server or client error
    """

    body = {
        "message": "Invalid Webhook Token",
        "code": 50027
    }

    # Set up HTTP client mock to prevent communication with real backend
    httpretty.register_uri(
        httpretty.POST,
        "https://discord.com/api/webhooks/123/abc",
        status=401,
        body=json.dumps(body)
    )
