"""
Utility functions and constants for unit tests and integration tests
"""

import json
import httpretty

# -----------------------------------------------
# Constants
# -----------------------------------------------

# Valid values
HCAPTCHA_VALID_SITEKEY = '10000000-ffff-ffff-ffff-000000000001'
HCAPTCHA_VALID_SECRET = '0x0000000000000000000000000000000000000000'
HCAPTCHA_VALID_RESPONSE = '10000000-aaaa-bbbb-cccc-000000000001'
# Invalid values
HCAPTCHA_INVALID_SITEKEY = '1-f-f-f-0'
HCAPTCHA_INVALID_SECRET = '0x1'
HCAPTCHA_INVALID_RESPONSE = '1-a-b-c-0'

# -----------------------------------------------
# hCaptcha utils
# -----------------------------------------------

def httpretty_register_hcaptcha_siteverify_success():
    """
    Mock hCaptcha verify endpoint returning successful response
    """
    # Prepare mocked hcaptcha response
    body = {
        'success': True,
        'credit': False,
        'hostname': 'dummy-key-pass',
        'challenge_ts': '2021-12-30T12:21:36.000Z'
    }

    # Set up HTTP client mock to prevent communication with real backend
    httpretty.register_uri(
        httpretty.POST,
        "https://hcaptcha.com/siteverify",
        status=200,
        body=json.dumps(body)
    )

def httpretty_register_hcaptcha_siteverify_failure():
    """
    Mock hCaptcha verify endpoint returning failed response
    """
    # Prepare mocked hcaptcha response
    body = {
        'success': False,
        'credit': False,
        'hostname': 'dummy-key-pass',
        'challenge_ts': '2021-12-30T12:21:36.000Z',
        'error-codes': [
            'invalid-input-response'
        ]
    }

    # Set up HTTP client mock to prevent communication with real backend
    httpretty.register_uri(
        httpretty.POST,
        "https://hcaptcha.com/siteverify",
        status=200,
        body=json.dumps(body)
    )

def httpretty_register_hcaptcha_siteverify_error():
    """
    Mock hCaptcha verify endpoint returning server or client error
    """

    # Set up HTTP client mock to prevent communication with real backend
    httpretty.register_uri(
        httpretty.POST,
        "https://hcaptcha.com/siteverify",
        status=429,
    )
