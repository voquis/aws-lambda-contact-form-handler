"""
Runner unit tests
"""

import os
import pytest
import httpretty

from app_handler.provider.request import RequestProvider
from app_handler.provider.response import ResponseProvider
from app_handler.runner.hcaptcha import HcaptchaRunner
import tests.unit.service.hcaptcha_utils as utils


def test_runner_not_enabled(monkeypatch):
    """
    Test runner is not enabled.
    Running should not produce any errors
    """

    payload = {'version': '1.0','body': {}}
    request_provider = RequestProvider(payload)
    response_provider = ResponseProvider(payload)

    monkeypatch.setenv('HCAPTCHA_ENABLE', '')

    runner = HcaptchaRunner()
    runner.configure()
    assert runner.enable == False

    runner.run(request_provider, response_provider)
    assert not runner.error_response


def test_runner_enabled_not_configured(monkeypatch):
    """
    Test enabling but not properly configuring runner.
    Configuring should throw an exception.
    """

    monkeypatch.setenv('HCAPTCHA_ENABLE', 'True')
    monkeypatch.setenv('HCAPTCHA_SITEKEY', '')
    runner = HcaptchaRunner()
    with pytest.raises(ValueError) as exception:
        runner.configure()

    assert 'HCAPTCHA_SITEKEY' in str(exception.value)


@httpretty.activate(allow_net_connect=False)
def test_runner_enabled_and_configured_missing_field(monkeypatch):
    """
    Test configured runner catches service exception correctly
    Trying to POST with invalid credentials should be caught
    """

    monkeypatch.setenv('HCAPTCHA_ENABLE', 'True')
    monkeypatch.setenv('HCAPTCHA_SITEKEY', 'abc')
    monkeypatch.setenv('HCAPTCHA_SECRET', '123')
    monkeypatch.setenv('HCAPTCHA_RESPONSE_FIELD', 'test-captcha-field')
    runner = HcaptchaRunner()
    runner.configure()

    assert runner.enable == True
    assert runner.sitekey == 'abc'
    assert runner.secret == '123'
    assert runner.verify_url == 'https://hcaptcha.com/siteverify'
    assert runner.response_field == 'test-captcha-field'

    payload = {'version': '1.0','body': {'not-field': 'abc'}}
    request_provider = RequestProvider(payload)
    response_provider = ResponseProvider(payload)

    response = runner.run(request_provider, response_provider)

    assert runner.error_response['statusCode'] == 400
    assert not response

@httpretty.activate(allow_net_connect=False)
def test_runner_enabled_and_configured_service_error(monkeypatch):
    """
    Test configured runner catches service exception correctly
    Trying to POST with invalid credentials should be caught
    """

    monkeypatch.setenv('HCAPTCHA_ENABLE', 'True')
    monkeypatch.setenv('HCAPTCHA_SITEKEY', 'abc')
    monkeypatch.setenv('HCAPTCHA_SECRET', '123')
    monkeypatch.setenv('HCAPTCHA_RESPONSE_FIELD', 'test-captcha-field')
    runner = HcaptchaRunner()
    runner.configure()

    assert runner.enable == True
    assert runner.sitekey == 'abc'
    assert runner.secret == '123'
    assert runner.verify_url == 'https://hcaptcha.com/siteverify'
    assert runner.response_field == 'test-captcha-field'

    payload = {'version': '1.0','body': {'test-captcha-field': 'abc'}}
    request_provider = RequestProvider(payload)
    response_provider = ResponseProvider(payload)

    # Prepare mocked error call to hCaptcha API
    utils.httpretty_register_hcaptcha_siteverify_error()

    response = runner.run(request_provider, response_provider)
    assert runner.error_response['statusCode'] == 500
    assert not response

@httpretty.activate(allow_net_connect=False)
def test_runner_enabled_and_configured_service_success_validation_fail(monkeypatch):
    """
    Test configured runner catches service exception correctly
    Trying to POST with invalid credentials should be caught
    """

    monkeypatch.setenv('HCAPTCHA_ENABLE', 'True')
    monkeypatch.setenv('HCAPTCHA_SITEKEY', 'abc')
    monkeypatch.setenv('HCAPTCHA_SECRET', '123')
    monkeypatch.setenv('HCAPTCHA_RESPONSE_FIELD', 'test-captcha-field')
    runner = HcaptchaRunner()
    runner.configure()

    assert runner.enable == True
    assert runner.sitekey == 'abc'
    assert runner.secret == '123'
    assert runner.verify_url == 'https://hcaptcha.com/siteverify'
    assert runner.response_field == 'test-captcha-field'

    payload = {'version': '1.0','body': {'test-captcha-field': 'abc'}}
    request_provider = RequestProvider(payload)
    response_provider = ResponseProvider(payload)

    # # Prepare mocked call to Discord API
    utils.httpretty_register_hcaptcha_siteverify_failure()

    response = runner.run(request_provider, response_provider)
    assert runner.error_response['statusCode'] == 401
    assert response['status'] == 200


@httpretty.activate(allow_net_connect=False)
def test_runner_enabled_and_configured_service_success_validation_success(monkeypatch):
    """
    Test configured runner catches service exception correctly
    Trying to POST with invalid credentials should be caught
    """

    monkeypatch.setenv('HCAPTCHA_ENABLE', 'True')
    monkeypatch.setenv('HCAPTCHA_SITEKEY', 'abc')
    monkeypatch.setenv('HCAPTCHA_SECRET', '123')
    monkeypatch.setenv('HCAPTCHA_RESPONSE_FIELD', 'test-captcha-field')
    runner = HcaptchaRunner()
    runner.configure()

    assert runner.enable == True
    assert runner.sitekey == 'abc'
    assert runner.secret == '123'
    assert runner.verify_url == 'https://hcaptcha.com/siteverify'
    assert runner.response_field == 'test-captcha-field'

    payload = {'version': '1.0','body': {'test-captcha-field': 'abc'}}
    request_provider = RequestProvider(payload)
    response_provider = ResponseProvider(payload)

    # # Prepare mocked call to Discord API
    utils.httpretty_register_hcaptcha_siteverify_success()

    response = runner.run(request_provider, response_provider)
    assert not runner.error_response
    assert response['status'] == 200
