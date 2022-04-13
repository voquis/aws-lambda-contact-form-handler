"""
Runner unit tests
"""

import os
import pytest
import httpretty

from app_handler.provider.request import RequestProvider
from app_handler.provider.response import ResponseProvider
from app_handler.runner.discord import DiscordRunner
import tests.unit.service.discord_utils as utils


def test_runner_not_enabled(monkeypatch):
    """
    Test runner is not enabled.
    Running should not produce any errors
    """

    payload = {'version': '1.0','body': {}}
    request_provider = RequestProvider(payload)
    response_provider = ResponseProvider(payload)

    runner = DiscordRunner()
    runner.configure()
    assert runner.enable == False

    runner.run(request_provider, response_provider)
    assert not runner.error_response


def test_runner_enabled_not_configured(monkeypatch):
    """
    Test enabling but not properly configuring runner.
    Configuring should throw an exception.
    """

    monkeypatch.setenv('DISCORD_ENABLE', 'True')
    runner = DiscordRunner()
    with pytest.raises(ValueError) as exception:
        runner.configure()

    assert 'DISCORD_WEBHOOK_ID' in str(exception.value)

def test_runner_enabled_and_configuration_failure(monkeypatch):
    """
    Test configured runner catches service configuration exception correctly
    Trying to parse a broken JSON template should trigger config exception
    """

    monkeypatch.setenv('DISCORD_ENABLE', 'True')
    monkeypatch.setenv('DISCORD_WEBHOOK_ID', 'abc')
    monkeypatch.setenv('DISCORD_WEBHOOK_TOKEN', '123')
    monkeypatch.setenv('DISCORD_JSON_TEMPLATE', '{"":*bad}json${template}}')
    runner = DiscordRunner()
    with pytest.raises(ValueError) as exception:
        runner.configure()

    assert 'JSON template' in str(exception.value)


def test_runner_enabled_and_configuration_template_failure(monkeypatch):
    """
    Test configured runner catches service configuration exception correctly
    Trying to substitute a missing value into valid JSON template should be caught
    """

    monkeypatch.setenv('DISCORD_ENABLE', 'True')
    monkeypatch.setenv('REQUIRED_FIELDS', 'name, email')
    monkeypatch.setenv('DISCORD_WEBHOOK_ID', 'abc')
    monkeypatch.setenv('DISCORD_WEBHOOK_TOKEN', '123')
    monkeypatch.setenv('DISCORD_JSON_TEMPLATE', '{"test":"${missing}"}')
    runner = DiscordRunner()
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

    monkeypatch.setenv('DISCORD_ENABLE', 'True')
    monkeypatch.setenv('REQUIRED_FIELDS', 'name, email')
    monkeypatch.setenv('DISCORD_WEBHOOK_ID', 'abc')
    monkeypatch.setenv('DISCORD_WEBHOOK_TOKEN', '123')
    monkeypatch.setenv('DISCORD_JSON_TEMPLATE', '{"test":"${missing}"}')
    runner = DiscordRunner()
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
    Trying to POST with invalid credentials should be caught
    """

    monkeypatch.setenv('DISCORD_ENABLE', 'True')
    monkeypatch.setenv('DISCORD_WEBHOOK_ID', '123')
    monkeypatch.setenv('DISCORD_WEBHOOK_TOKEN', 'abc')
    monkeypatch.setenv('DISCORD_JSON_TEMPLATE', '[]')
    runner = DiscordRunner()
    runner.configure()

    assert runner.enable == True
    assert runner.webhook_id == '123'
    assert runner.webhook_token == 'abc'
    assert runner.fields == {}

    payload = {'version': '1.0','body': {}}
    request_provider = RequestProvider(payload)
    response_provider = ResponseProvider(payload)

    # Prepare mocked call to Discord API
    utils.httpretty_register_discord_webhook_unauthorised()

    runner.run(request_provider, response_provider)
    assert runner.error_response['statusCode'] == 500


@httpretty.activate(allow_net_connect=False)
def test_runner_enabled_and_configured_success(monkeypatch):
    """
    Test configured runner submits message successfully
    Assert no errors are returned
    """

    monkeypatch.setenv('REQUIRED_FIELDS', 'name, email')
    monkeypatch.setenv('DISCORD_ENABLE', 'True')
    monkeypatch.setenv('DISCORD_WEBHOOK_ID', '123')
    monkeypatch.setenv('DISCORD_WEBHOOK_TOKEN', 'abc')
    monkeypatch.setenv('DISCORD_JSON_TEMPLATE', '{"content":"${name} - ${email}"}')
    runner = DiscordRunner()
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

    # Prepare mocked call to Discord API
    utils.httpretty_register_discord_webhook_success()

    result = runner.run(request_provider, response_provider)
    assert runner.fields == {'name': 'My Name', 'email': 'me@example.com'}
    assert not runner.error_response
    assert result['status'] == 204


def test_runner_enabled_and_configured_bad_json(monkeypatch):
    """
    Test configured runner submits message successfully
    Assert no errors are returned
    """

    monkeypatch.setenv('REQUIRED_FIELDS', 'name')
    monkeypatch.setenv('DISCORD_ENABLE', 'True')
    monkeypatch.setenv('DISCORD_WEBHOOK_ID', '123')
    monkeypatch.setenv('DISCORD_WEBHOOK_TOKEN', 'abc')
    monkeypatch.setenv('DISCORD_JSON_TEMPLATE', '{"content":"${name}"}')
    runner = DiscordRunner()
    runner.configure()
    assert runner.enable == True

    payload = {'version': '1.0', 'body': {'name': 'My"{Name'}}

    request_provider = RequestProvider(payload)
    response_provider = ResponseProvider(payload)

    runner.run(request_provider, response_provider)
    assert runner.error_response['statusCode'] == 500
