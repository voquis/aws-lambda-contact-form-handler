"""
Utility functions and constants for unit tests and integration tests
"""

import httpretty

# -----------------------------------------------
# Utils
# -----------------------------------------------

def httpretty_register_slack_webhook_success():
    """
    Mock Slack webhook endpoint returning successful response
    """

    # Set up HTTP client mock to prevent communication with real backend
    httpretty.register_uri(
        httpretty.POST,
        "https://hooks.slack.com/services/abc/xyz/123",
        status=200
    )

def httpretty_register_slack_webhook_bad_token():
    """
    Mock webhook endpoint returning failed response
    """
    # Prepare mocked  response
    body = 'invalid_token'

    # Set up HTTP client mock to prevent communication with real backend
    httpretty.register_uri(
        httpretty.POST,
        "https://hooks.slack.com/services/abc/xyz/123",
        status=401,
        body=body
    )

def httpretty_register_slack_webhook_failure_bad_json():
    """
    Mock Slack webhook endpoint returning failed response
    """
    # Set up HTTP client mock to prevent communication with real backend
    httpretty.register_uri(
        httpretty.POST,
        "https://hooks.slack.com/services/abc/xyz/123",
        status=400,
        body='{bad"{json'
    )

def httpretty_register_slack_webhook_unknown_service():
    """
    Mock Slack webhook endpoint returning client error
    """

    body = 'no_service'

    # Set up HTTP client mock to prevent communication with real backend
    httpretty.register_uri(
        httpretty.POST,
        "https://hooks.slack.com/services/abc/xyz/123",
        status=404,
        body=body
    )
