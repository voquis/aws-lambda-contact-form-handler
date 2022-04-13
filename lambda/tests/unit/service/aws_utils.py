"""
AWS test utils
"""

import boto3

def ses_verify_email_identity(email_address='from@example.com'):
    """
    Verify email address to allow sending using moto
    """

    ses = boto3.client('ses')
    ses.verify_email_identity(
        EmailAddress=email_address
    )


def ssm_put_parameter_securestring(name='test', value='abc'):
    """
    Create mocked SSM parameter to later fetch using moto
    """
    ssm = boto3.client('ssm')
    ssm.put_parameter(
        Name=name,
        Value=value,
        Type='SecureString',
    )


def put_secretsmanager_secret(name='test', value=None, binary=None):
    """
    Create mocked Secrets Manager secret to later fetch using moto
    """
    ssm = boto3.client('secretsmanager')
    if value is not None:
        ssm.create_secret(Name=name, SecretString=value)

    if binary is not None:
        ssm.create_secret(Name=name, SecretBinary=binary)


def create_dynamodb_table(name='test'):
    """
    Create dynamodb table
    """
    dynamodb = boto3.client("dynamodb")
    dynamodb.create_table(
        TableName=name,
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'timestamp',
                'AttributeType': 'N'
            },
        ],
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'timestamp',
                'KeyType': 'RANGE'
            },
        ],
        BillingMode='PAY_PER_REQUEST',
        SSESpecification={
            'Enabled': True,
            'SSEType': 'AES256',
        },
        TableClass='STANDARD'
    )
