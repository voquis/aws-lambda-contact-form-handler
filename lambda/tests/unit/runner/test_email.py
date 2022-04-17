"""
Runner unit tests
"""

import os
import pytest

from app_handler.provider.request import RequestProvider
from app_handler.provider.response import ResponseProvider
from app_handler.runner.email import EmailRunner
from tests.unit.service.aws_utils import ses_verify_email_identity
from moto import mock_ses


# Set boto/moto client default values
os.environ['AWS_DEFAULT_REGION'] = 'eu-west-2'

def test_runner_not_enabled():
    """
    Test runner is not enabled.
    Running should not produce any errors
    """

    payload = {'version': '1.0','body': {}}
    request_provider = RequestProvider(payload)
    response_provider = ResponseProvider(payload)

    runner = EmailRunner()
    runner.configure()
    assert runner.enable == False
    assert runner.fields == None

    runner.run(request_provider, response_provider)
    assert not runner.error_response


def test_runner_enabled_not_configured(monkeypatch):
    """
    Test enabling but not properly configuring runner.
    Configuring should throw an exception.
    """
    monkeypatch.setenv('EMAIL_ENABLE', 'True')
    runner = EmailRunner()
    with pytest.raises(ValueError) as exception:
        runner.configure()

    assert 'EMAIL_SENDER' in str(exception.value)


def test_runner_enabled_and_configuration_template_failure(monkeypatch):
    """
    Test configured runner catches service configuration exception correctly
    Trying to retrieve values from the payload that do not exist should be caught
    """

    monkeypatch.setenv('REQUIRED_FIELDS', 'name, email')
    monkeypatch.setenv('EMAIL_ENABLE', 'True')
    monkeypatch.setenv('EMAIL_SENDER', 'from@example.com')
    monkeypatch.setenv('EMAIL_RECIPIENTS', 'to1@example.com,to2@example.com')
    monkeypatch.setenv('EMAIL_TEXT_TEMPLATE', '{"test":"${missing}"}')
    monkeypatch.setenv('EMAIL_SUBJECT_TEMPLATE', 'My email subject')
    runner = EmailRunner()
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

    monkeypatch.setenv('REQUIRED_FIELDS', 'name, email')
    monkeypatch.setenv('EMAIL_ENABLE', 'True')
    monkeypatch.setenv('EMAIL_SENDER', 'from@example.com')
    monkeypatch.setenv('EMAIL_RECIPIENTS', 'to1@example.com,to2@example.com')
    monkeypatch.setenv('EMAIL_SUBJECT_TEMPLATE', 'Message from ${name} - ${subject}')
    monkeypatch.setenv('EMAIL_TEXT_TEMPLATE', '{"test":"${name}"}')
    runner = EmailRunner()
    runner.configure()

    payload = {'version': '1.0','body': {'notName':'a', 'notEmail':'b'}}
    request_provider = RequestProvider(payload)
    response_provider = ResponseProvider(payload)

    response = runner.run(request_provider, response_provider)

    assert not response
    assert runner.error_response['statusCode'] == 500


@mock_ses
def test_runner_enabled_and_configured_failure(monkeypatch):
    """
    Test configured runner catches service exception correctly
    Use bad email address to trigger service exception
    """

    monkeypatch.setenv('EMAIL_ENABLE', 'True')
    monkeypatch.setenv('EMAIL_SENDER', '@bad*email.address')
    monkeypatch.setenv('EMAIL_RECIPIENTS', 'to1@example.com,to2@example.com')
    monkeypatch.setenv('EMAIL_SUBJECT_TEMPLATE', 'plain subject')
    monkeypatch.setenv('EMAIL_TEXT_TEMPLATE', 'plain text')
    runner = EmailRunner()
    runner.configure()
    assert runner.enable == True
    assert runner.sender == '@bad*email.address'
    assert runner.fields == {}

    payload = {'version': '1.0','body': {}}
    request_provider = RequestProvider(payload)
    response_provider = ResponseProvider(payload)

    response = runner.run(request_provider, response_provider)
    assert not response
    assert runner.error_response['statusCode'] == 500

@mock_ses
def test_runner_enabled_and_configured_success(monkeypatch):
    """
    Test configured runner saves item successfully
    Assert no errors are returned
    """

    monkeypatch.setenv('REQUIRED_FIELDS', 'name, email, subject, message')
    monkeypatch.setenv('EMAIL_ENABLE', 'True')
    monkeypatch.setenv('EMAIL_SENDER', 'from@example.com')
    monkeypatch.setenv('EMAIL_RECIPIENTS', 'to1@example.com,to2@example.com')
    monkeypatch.setenv('EMAIL_SUBJECT_TEMPLATE', 'Message from ${name} - ${subject}')
    monkeypatch.setenv('EMAIL_TEXT_TEMPLATE', 'Message Contents\n${message}')
    runner = EmailRunner()
    runner.configure()
    assert runner.enable == True
    assert runner.sender == 'from@example.com'

    payload = {
        'version': '1.0',
        'body': {
            'name': 'My Name',
            'email': 'me@example.com',
            'subject': 'Test subject',
            'message': 'This is a test message'
        }
    }

    request_provider = RequestProvider(payload)
    response_provider = ResponseProvider(payload)

    # Verify test email with the mocked SES service to allow mocked sending
    ses_verify_email_identity()

    result = runner.run(request_provider, response_provider)
    assert not runner.error_response
    assert runner.fields == {
        'name': 'My Name',
        'email': 'me@example.com',
        'subject': 'Test subject',
        'message': 'This is a test message'
    }
    assert result['ResponseMetadata']['HTTPStatusCode'] == 200
