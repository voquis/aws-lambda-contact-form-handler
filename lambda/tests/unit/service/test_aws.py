"""
Pytest unit tests for aws client for calls to SES and SSM Parameter Store
"""

import os
from moto import mock_ssm, mock_ses, mock_secretsmanager, mock_dynamodb
from app_handler.service.aws import AwsService
import tests.unit.service.aws_utils as utils

# Set boto client default values
os.environ['AWS_DEFAULT_REGION'] = 'eu-west-2'

@mock_ssm
def test_getting_parameter():
    """
    Check an SSM parameter is returned
    """

    # Create test parameter to later fetch using moto
    utils.ssm_put_parameter_securestring()

    # Fetch and verify parameter
    aws = AwsService()
    param = aws.get_parameter_value('test')
    assert param == 'abc'

    # Assert missing parameter returns nothing
    assert not aws.get_parameter_value('doesnotexist')

@mock_ses
def test_sending_email():
    """
    Check an SES email is sent successfully
    """

    # Verify email address to allow sending using moto
    utils.ses_verify_email_identity()

    # Send email
    aws = AwsService()
    response = aws.send_email(
        'to1@example.com,to2@example.com',
        'from@example.com',
        'Subject',
        'Body'
    )
    assert response['ResponseMetadata']['HTTPStatusCode'] == 200
    assert len(response['MessageId']) > 0

    # Assert unverified email exceptions are caught
    assert not aws.send_email('a@b.com','unverifed@a.com','Subj','Body')


@mock_secretsmanager
def test_getting_secret():
    """
    Check string and binary secrets may be retrieved
    """

    # Create mocked secrets to later fetch using moto
    secret_string = 'my secret value'
    secret_binary = bytes(secret_string, 'utf-8')
    utils.put_secretsmanager_secret('/secret/string', secret_string)
    utils.put_secretsmanager_secret('/secret/binary', None, secret_binary)

    # Fetch secrets
    aws = AwsService()
    assert aws.get_secret_value('/secret/string') == secret_string
    assert aws.get_secret_value('/secret/binary') == secret_string
    assert not aws.get_secret_value('/does/not/exist')


@mock_dynamodb
def test_putting_item():
    """
    Check putting a DynamoDB item
    """

    # Create mocked table
    utils.create_dynamodb_table('contact')

    # Put item
    aws = AwsService()
    response = aws.put_dynamodb_item('contact', {'a':'b'})
    assert response['ConsumedCapacity'][0]['CapacityUnits'] == 1.0
    assert response['ConsumedCapacity'][0]['TableName'] == 'contact'
    assert response['ResponseMetadata']['HTTPStatusCode'] == 200

    # Assert putting to missing table exception is caught
    assert not aws.put_dynamodb_item('non-existent-table', {})
