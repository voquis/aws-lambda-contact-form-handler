"""
Runner unit tests
"""

import os
import pytest

from app_handler.provider.request import RequestProvider
from app_handler.provider.response import ResponseProvider
from app_handler.runner.dynamodb import DynamodbRunner
from tests.unit.service.aws_utils import create_dynamodb_table
from moto import mock_dynamodb


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

    runner = DynamodbRunner()
    runner.configure()
    assert runner.enable == False

    runner.run(request_provider, response_provider)
    assert not runner.error_response


def test_runner_enabled_not_configured(monkeypatch):
    """
    Test enabling but not properly configuring runner.
    Configuring should throw an exception.
    """

    monkeypatch.setenv('DYNAMODB_ENABLE', 'True')
    runner = DynamodbRunner()
    with pytest.raises(ValueError) as exception:
        runner.configure()

    assert 'DYNAMODB_TABLE' in str(exception.value)


@mock_dynamodb
def test_runner_enabled_and_configured_failure(monkeypatch):
    """
    Test configured runner catches service exception correctly
    Trying to put to a non-existent table should trigger service exception
    """

    monkeypatch.setenv('DYNAMODB_ENABLE', 'True')
    monkeypatch.setenv('DYNAMODB_TABLE', 'non-existent-table')
    runner = DynamodbRunner()
    runner.configure()
    assert runner.enable == True
    assert runner.table == 'non-existent-table'
    assert runner.fields == {}

    payload = {'version': '1.0','body': {}}

    request_provider = RequestProvider(payload)
    response_provider = ResponseProvider(payload)

    runner.run(request_provider, response_provider)
    assert runner.error_response['statusCode'] == 500

def test_runner_enabled_and_missing_fields(monkeypatch):
    """
    Test configured runner catches service configuration exception correctly
    Trying to retrieve values from the payload that do not exist should be caught
    """

    monkeypatch.setenv('REQUIRED_FIELDS', 'name, email')
    monkeypatch.setenv('DYNAMODB_ENABLE', 'True')
    monkeypatch.setenv('DYNAMODB_TABLE', 'new-table')
    runner = DynamodbRunner()
    runner.configure()

    payload = {'version': '1.0','body': {'notName':'a', 'notEmail':'b'}}
    request_provider = RequestProvider(payload)
    response_provider = ResponseProvider(payload)

    response = runner.run(request_provider, response_provider)

    assert not response
    assert runner.error_response['statusCode'] == 500

@mock_dynamodb
def test_runner_enabled_and_configured_success(monkeypatch):
    """
    Test configured runner saves item successfully
    Assert no errors are returned
    """

    monkeypatch.setenv('REQUIRED_FIELDS', 'name, email')
    monkeypatch.setenv('DYNAMODB_ENABLE', 'True')
    monkeypatch.setenv('DYNAMODB_TABLE', 'new-table')
    runner = DynamodbRunner()
    runner.configure()
    assert runner.enable == True
    assert runner.table == 'new-table'

    payload = {
        'version': '1.0',
        'body': {
            'name': 'My Name',
            'email': 'me@example.com'
        }
    }

    request_provider = RequestProvider(payload)
    response_provider = ResponseProvider(payload)

    # Prepare mocked DynamoDB table:
    create_dynamodb_table('new-table')

    result = runner.run(request_provider, response_provider)
    assert runner.fields == {'name': 'My Name', 'email': 'me@example.com'}
    assert not runner.error_response
    assert result['ResponseMetadata']['HTTPStatusCode'] == 200
