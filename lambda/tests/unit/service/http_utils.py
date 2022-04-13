"""
Utility functions and constants for unit tests and integration tests
"""

import json
import httpretty

# -----------------------------------------------
# hCaptcha utils
# -----------------------------------------------

def httpretty_register_http_success_json_response():
    """
    Mock hCaptcha verify endpoint returning successful response
    """
    # Prepare mocked hcaptcha response
    body = {
        'title': 'test',
        'items': [
            1,
            2
        ],
    }

    # Set up HTTP client mock to prevent communication with real backend
    httpretty.register_uri(
        httpretty.POST,
        "https://example.com/json",
        status=200,
        body=json.dumps(body)
    )
