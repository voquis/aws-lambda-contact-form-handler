"""
App provider unit tests
"""

import os
import httpretty
from moto import mock_dynamodb, mock_ses, mock_secretsmanager, mock_ssm

from app_handler.provider.app import AppProvider
from tests.unit.service import aws_utils, discord_utils, hcaptcha_utils

# Set boto/moto client default values
os.environ['AWS_DEFAULT_REGION'] = 'eu-west-2'

def test_string_request():
    """
    Test app provider
    """

    app_provider = AppProvider('test')
    assert app_provider.response == {'message': 'Message received', 'statusCode': 200}


def test_invalid_request():
    """
    Test app provider
    """
    app_provider = AppProvider({'version'})
    assert app_provider.response == {'message': 'Message received', 'statusCode': 200}


def test_service_configurations(monkeypatch):
    """
    Test app provider
    """
    monkeypatch.setenv('HCAPTCHA_ENABLE', 'true')
    monkeypatch.setenv('EMAIL_ENABLE', 'true')
    monkeypatch.setenv('DYNAMODB_ENABLE', 'true')
    monkeypatch.setenv('DISCORD_ENABLE', 'true')
    app_provider = AppProvider({'version'})
    assert app_provider.response['statusCode'] == 500
    assert app_provider.response['message'] == 'Error configuring services'


def test_app_error(monkeypatch):
    """
    Test app provider
    """
    monkeypatch.setenv('REQUIRED_FIELDS', 'a')
    app_provider = AppProvider({'version':'1.0', 'body': {}})
    assert app_provider.response['statusCode'] == 400
    assert app_provider.response['body'] == '{"message": "Missing required field `a`"}'


def test_hcaptcha_error(monkeypatch):
    """
    Test app provider correctly handles hcaptcha errors
    """
    monkeypatch.setenv('HCAPTCHA_ENABLE', 'true')
    monkeypatch.setenv('HCAPTCHA_SITEKEY', 'abc')
    monkeypatch.setenv('HCAPTCHA_SECRET', '123')
    monkeypatch.setenv('HCAPTCHA_RESPONSE_FIELD', 'my-field')
    app_provider = AppProvider({'version'})
    assert app_provider.response['statusCode'] == 400
    assert app_provider.response['message'] == 'Missing captcha user response field'


@mock_dynamodb
def test_dynamodb_error(monkeypatch):
    """
    Test app provider correctly handles dynamodb errors
    """
    monkeypatch.setenv('DYNAMODB_ENABLE', 'true')
    monkeypatch.setenv('DYNAMODB_TABLE', 'my-table')

    app_provider = AppProvider({'version'})
    assert app_provider.response['statusCode'] == 500
    assert app_provider.response['message'] == 'Storage service error'


@mock_ses
def test_email_error(monkeypatch):
    """
    Test app provider correctly handles email sending errors
    """
    monkeypatch.setenv('EMAIL_ENABLE', 'true')
    monkeypatch.setenv('EMAIL_SENDER', 'a@a.com')
    monkeypatch.setenv('EMAIL_RECIPIENTS', 'a@b.com,a@c.com')
    monkeypatch.setenv('EMAIL_SUBJECT_TEMPLATE', 'Subject')
    monkeypatch.setenv('EMAIL_TEXT_TEMPLATE', 'My email message')

    app_provider = AppProvider({'version'})
    assert app_provider.response['statusCode'] == 500
    assert app_provider.response['message'] == 'Notification service error'


@httpretty.activate(allow_net_connect=False)
def test_discord_error(monkeypatch):
    """
    Test app provider correctly handles discord sending errors
    """
    monkeypatch.setenv('DISCORD_ENABLE', 'true')
    monkeypatch.setenv('DISCORD_WEBHOOK_ID', '123')
    monkeypatch.setenv('DISCORD_WEBHOOK_TOKEN', 'abc')
    monkeypatch.setenv('DISCORD_JSON_TEMPLATE', '{"test":"string"}')

    # Mock failing discord response
    discord_utils.httpretty_register_discord_webhook_unauthorised()

    app_provider = AppProvider({'version'})
    assert app_provider.response['statusCode'] == 500
    assert app_provider.response['message'] == 'Notification service error'


@httpretty.activate(allow_net_connect=False)
@mock_dynamodb
@mock_secretsmanager
@mock_ses
@mock_ssm
def test_all_success(monkeypatch):
    """
    Test app provider correctly handles when all cases are successful
    """
    # Configure environment variables
    monkeypatch.setenv('REQUIRED_FIELDS', 'name, subject, message')
    monkeypatch.setenv('HCAPTCHA_ENABLE', 'true')
    monkeypatch.setenv('DYNAMODB_ENABLE', 'true')
    monkeypatch.setenv('EMAIL_ENABLE', 'true')
    monkeypatch.setenv('DISCORD_ENABLE', 'true')
    # hCaptcha configs
    monkeypatch.setenv('HCAPTCHA_SITEKEY_SOURCE', 'aws_ssm_parameter_store')
    monkeypatch.setenv('HCAPTCHA_SITEKEY_PARAMETER_STORE_NAME', '/a/hcaptcha/sitekey')
    monkeypatch.setenv('HCAPTCHA_SECRET_SOURCE', 'aws_secrets_manager')
    monkeypatch.setenv('HCAPTCHA_SECRET_SECRETS_MANAGER_NAME', '/a/hcaptcha/secret')
    monkeypatch.setenv('HCAPTCHA_RESPONSE_FIELD_SOURCE', 'aws_ssm_parameter_store')
    monkeypatch.setenv('HCAPTCHA_RESPONSE_FIELD_PARAMETER_STORE_NAME', '/a/hcaptcha/response_field')
    # Dynamodb configs
    monkeypatch.setenv('DYNAMODB_TABLE_SOURCE', 'aws_ssm_parameter_store')
    monkeypatch.setenv('DYNAMODB_TABLE_PARAMETER_STORE_NAME', '/a/dynamodb/table')
    # Email configs
    monkeypatch.setenv('EMAIL_SENDER_SOURCE', 'aws_ssm_parameter_store')
    monkeypatch.setenv('EMAIL_SENDER_PARAMETER_STORE_NAME', '/a/email/sender')
    monkeypatch.setenv('EMAIL_RECIPIENTS_SOURCE', 'aws_ssm_parameter_store')
    monkeypatch.setenv('EMAIL_RECIPIENTS_PARAMETER_STORE_NAME', '/a/email/recipients')
    monkeypatch.setenv('EMAIL_SUBJECT_TEMPLATE_SOURCE', 'aws_ssm_parameter_store')
    monkeypatch.setenv('EMAIL_SUBJECT_TEMPLATE_PARAMETER_STORE_NAME', '/a/email/template/subject')
    monkeypatch.setenv('EMAIL_TEXT_TEMPLATE_SOURCE', 'aws_ssm_parameter_store')
    monkeypatch.setenv('EMAIL_TEXT_TEMPLATE_PARAMETER_STORE_NAME', '/a/email/template/text')
    # Discord configs
    monkeypatch.setenv('DISCORD_WEBHOOK_ID_SOURCE', 'aws_ssm_parameter_store')
    monkeypatch.setenv('DISCORD_WEBHOOK_ID_PARAMETER_STORE_NAME', '/a/discord/webhook/id')
    monkeypatch.setenv('DISCORD_WEBHOOK_TOKEN_SOURCE', 'aws_secrets_manager')
    monkeypatch.setenv('DISCORD_WEBHOOK_TOKEN_SECRETS_MANAGER_NAME', '/a/discord/webhook/token')
    monkeypatch.setenv('DISCORD_JSON_TEMPLATE_SOURCE', 'aws_ssm_parameter_store')
    monkeypatch.setenv('DISCORD_JSON_TEMPLATE_PARAMETER_STORE_NAME', '/a/discord/template/json')

    # Create Mocked AWS resources
    aws_utils.ssm_put_parameter_securestring('/a/hcaptcha/sitekey', 'abc')
    aws_utils.put_secretsmanager_secret('/a/hcaptcha/secret', '123')
    aws_utils.ssm_put_parameter_securestring('/a/hcaptcha/response_field', 'captcha-response')
    # Dynamodb configs
    aws_utils.ssm_put_parameter_securestring('/a/dynamodb/table', 'table-e4d3s5')
    aws_utils.create_dynamodb_table('table-e4d3s5')
    # Email configs
    aws_utils.ssm_put_parameter_securestring('/a/email/sender', 'from-123@example.com')
    aws_utils.ssm_put_parameter_securestring('/a/email/recipients', '123@a.ab,456@b.yz,')
    aws_utils.ssm_put_parameter_securestring('/a/email/template/subject', '${name} ${subject}')
    aws_utils.ssm_put_parameter_securestring('/a/email/template/text', 'Message: ${message}')
    aws_utils.ses_verify_email_identity('from-123@example.com')
    # Discord configs
    aws_utils.ssm_put_parameter_securestring('/a/discord/webhook/id', '123')
    aws_utils.put_secretsmanager_secret('/a/discord/webhook/token', 'abc')
    aws_utils.ssm_put_parameter_securestring('/a/discord/template/json', '{"content":"${message}"}')

    # Mock API calls
    hcaptcha_utils.httpretty_register_hcaptcha_siteverify_success()
    discord_utils.httpretty_register_discord_webhook_success()

    payload = {
        'version': '2.0',
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': """
            {
                "name": "My Name",
                "subject": "My subject",
                "message": "This\nis\amultiline\nMessage",
                "captcha-response": "xyz"
            }
        """
    }

    app_provider = AppProvider(payload)
    assert app_provider.response['statusCode'] == 200
    assert app_provider.response['body'] == '{"message": "Message received"}'
