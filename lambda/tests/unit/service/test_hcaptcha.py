"""
Pytest unit tests for hcaptcha client
"""

import pytest
import httpretty
from app_handler.service.hcaptcha import HcaptchaService
import tests.unit.service.hcaptcha_utils as utils

def test_missing_args():
    """
    Check class throws exception when initialised with incorrect parameters.
    """

    with pytest.raises(ValueError) as exception:
        HcaptchaService(None, None)

    assert 'Missing' in str(exception.value)


@httpretty.activate(allow_net_connect=False)
def test_service_error():
    """
    Check class throws exception when mocked remote returns error
    """

    # Set up HTTP client mock to prevent communication with real backend
    utils.httpretty_register_hcaptcha_siteverify_error()

    # Initialise client
    hcaptcha = HcaptchaService('abc', '123')

    # Call remote method (intercepted by httpretty) and except exception

    response = hcaptcha.validate('abc', '123')
    assert not hcaptcha.success
    assert response['status'] == 429

@httpretty.activate(allow_net_connect=False)
def test_validation_success():
    """
    Verify a mocked success is processed correctly
    """

    utils.httpretty_register_hcaptcha_siteverify_success()

    # Initialise client
    hcaptcha = HcaptchaService('abc', '123')

    # Perform validation check
    response = hcaptcha.validate('abc', '127.0.0.1')
    errors = hcaptcha.error_codes
    assert response['status'] == 200
    assert hcaptcha.success is True
    assert len(errors) == 0

@httpretty.activate(allow_net_connect=False)
def test_validation_failure():
    """
    Verify a mocked captcha verification failure is processed correctly
    Note that the service still returns a 200 OK.
    """

    utils.httpretty_register_hcaptcha_siteverify_failure()

    # Initialise client
    hcaptcha = HcaptchaService('abc', '123')

    # Perform validation check
    response = hcaptcha.validate('abc', '127.0.0.1')
    errors = hcaptcha.error_codes
    assert response['status'] == 200
    assert hcaptcha.success is False
    assert len(errors) > 0
