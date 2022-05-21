"""
Runner unit tests
"""

import os
import pytest
import httpretty

from app_handler.provider.request import RequestProvider
from app_handler.provider.response import ResponseProvider
from app_handler.runner.slack import SlackRunner
import tests.unit.service.slack_utils as utils

# Define constants
SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/abc/xyz/123'


def test_runner_not_enabled(monkeypatch):
    """
    Test runner is not enabled.
    Running should not produce any errors
    """

    payload = {'version': '1.0','body': {}}
    request_provider = RequestProvider(payload)
    response_provider = ResponseProvider(payload)

    runner = SlackRunner()
    runner.configure()
    assert runner.enable == False

    runner.run(request_provider, response_provider)
    assert not runner.error_response


def test_runner_enabled_not_configured(monkeypatch):
    """
    Test enabling but not properly configuring runner.
    Configuring should throw an exception.
    """

    monkeypatch.setenv('SLACK_ENABLE', 'True')
    runner = SlackRunner()
    with pytest.raises(ValueError) as exception:
        runner.configure()

    assert 'SLACK_WEBHOOK_URL' in str(exception.value)

def test_runner_enabled_and_configuration_failure(monkeypatch):
    """
    Test configured runner catches service configuration exception correctly
    Trying to parse a broken JSON template should trigger config exception
    """

    monkeypatch.setenv('SLACK_ENABLE', 'True')
    monkeypatch.setenv('SLACK_WEBHOOK_URL', 'abc')
    monkeypatch.setenv('SLACK_JSON_TEMPLATE', '{"":*bad}json${template}}')
    runner = SlackRunner()
    with pytest.raises(ValueError) as exception:
        runner.configure()

    assert 'JSON template' in str(exception.value)


def test_runner_enabled_and_configuration_template_failure(monkeypatch):
    """
    Test configured runner catches service configuration exception correctly
    Trying to substitute a missing value into valid JSON template should be caught
    """

    monkeypatch.setenv('SLACK_ENABLE', 'True')
    monkeypatch.setenv('REQUIRED_FIELDS', 'name, email')
    monkeypatch.setenv('SLACK_WEBHOOK_URL', 'abc')
    monkeypatch.setenv('SLACK_JSON_TEMPLATE', '{"test":"${missing}"}')
    runner = SlackRunner()
    runner.configure()

    payload = {'version': '1.0','body': {'name':'a', 'email':'b'}}
    request_provider = RequestProvider(payload)
    response_provider = ResponseProvider(payload)

    response = runner.run(request_provider, response_provider)

    assert not response
    assert runner.error_response['statusCode'] == 500


def test_runner_enabled_and_configuration_missing_fields(monkeypatch):
    """
    Test configured runner catches service configuration exception correctly
    Trying to retrieve values from the payload that do not exist should be caught
    """

    monkeypatch.setenv('SLACK_ENABLE', 'True')
    monkeypatch.setenv('REQUIRED_FIELDS', 'name, email')
    monkeypatch.setenv('SLACK_WEBHOOK_URL', 'abc')
    monkeypatch.setenv('SLACK_JSON_TEMPLATE', '{"test":"${missing}"}')
    runner = SlackRunner()
    runner.configure()

    payload = {'version': '1.0','body': {'notName':'a', 'notEmail':'b'}}
    request_provider = RequestProvider(payload)
    response_provider = ResponseProvider(payload)

    response = runner.run(request_provider, response_provider)

    assert not response
    assert runner.error_response['statusCode'] == 500


@httpretty.activate(allow_net_connect=False)
def test_runner_enabled_and_configured_service_failure(monkeypatch):
    """
    Test configured runner catches service exception correctly
    Trying to POST with invalid token should be caught
    """

    monkeypatch.setenv('SLACK_ENABLE', 'True')
    monkeypatch.setenv('SLACK_WEBHOOK_URL', SLACK_WEBHOOK_URL)
    monkeypatch.setenv('SLACK_JSON_TEMPLATE', '[]')
    runner = SlackRunner()
    runner.configure()

    assert runner.enable == True
    assert runner.webhook_url == SLACK_WEBHOOK_URL
    assert runner.fields == {}

    payload = {'version': '1.0','body': {}}
    request_provider = RequestProvider(payload)
    response_provider = ResponseProvider(payload)

    # Prepare mocked call to Slack API
    utils.httpretty_register_slack_webhook_bad_token()

    runner.run(request_provider, response_provider)
    assert runner.error_response['statusCode'] == 500


@httpretty.activate(allow_net_connect=False)
def test_runner_enabled_and_configured_success(monkeypatch):
    """
    Test configured runner submits message successfully
    Assert no errors are returned
    """

    monkeypatch.setenv('REQUIRED_FIELDS', 'name, email')
    monkeypatch.setenv('SLACK_ENABLE', 'True')
    monkeypatch.setenv('SLACK_WEBHOOK_URL', SLACK_WEBHOOK_URL)
    monkeypatch.setenv('SLACK_JSON_TEMPLATE', '{"content":"${name} - ${email}"}')
    runner = SlackRunner()
    runner.configure()
    assert runner.enable == True

    payload = {
        'version': '1.0',
        'body': {
            'name': 'My Name',
            'email': 'me@example.com'
        }
    }

    request_provider = RequestProvider(payload)
    response_provider = ResponseProvider(payload)

    # Prepare mocked call to Slack API
    utils.httpretty_register_slack_webhook_success()

    result = runner.run(request_provider, response_provider)
    assert runner.fields == {'name': 'My Name', 'email': 'me@example.com'}
    assert not runner.error_response
    assert result['status'] == 200


def test_runner_enabled_and_configured_bad_json(monkeypatch):
    """
    Test configured runner submits message successfully
    Assert no errors are returned
    """

    monkeypatch.setenv('REQUIRED_FIELDS', 'name')
    monkeypatch.setenv('SLACK_ENABLE', 'True')
    monkeypatch.setenv('SLACK_WEBHOOK_URL', SLACK_WEBHOOK_URL)
    monkeypatch.setenv('SLACK_JSON_TEMPLATE', '{"content":"${name}"}')
    runner = SlackRunner()
    runner.configure()
    assert runner.enable == True

    payload = {'version': '1.0', 'body': {'name': 'My"{Name'}}

    request_provider = RequestProvider(payload)
    response_provider = ResponseProvider(payload)

    runner.run(request_provider, response_provider)
    assert runner.error_response['statusCode'] == 500
