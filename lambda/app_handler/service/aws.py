"""
Interact with the following AWS services:
  - Simple Email Service to send emails
  - SSM Parameter store to fetch encrypted parameters
"""

import logging
from time import time
import uuid
import boto3
import botocore

class AwsService:
    """
    Fetch parameters and send emails.
    """
    def __init__(self) -> None:
        # Prepare AWS clients
        self.ses = boto3.client('ses')
        self.ssm = boto3.client('ssm')
        self.secretsmanager = boto3.client('secretsmanager')
        # Prepare AWS Service Resources
        self.dynamodb = boto3.resource('dynamodb')

    def get_parameter_value(self, name) -> str:
        """
        Fetch encrypted parameters from Systems Manager (SSM) Parameter Store
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ssm.html
        """

        value = None

        logging.debug('Fetching AWS SSM Parameter Store parameter: %s', name)
        try:
            response = self.ssm.get_parameter(
                Name=name,
                WithDecryption=True
            )
            if 'Parameter' in response:
                if 'Value' in response['Parameter']:
                    value = response['Parameter']['Value']
        except (
            botocore.exceptions.ClientError,
            botocore.exceptions.NoCredentialsError,
            self.ssm.exceptions.InternalServerError,
            self.ssm.exceptions.InvalidKeyId,
            self.ssm.exceptions.ParameterNotFound,
            self.ssm.exceptions.ParameterVersionNotFound,
        ) as exception:
            logging.warning('Unable to retrieve AWS SSM Parameter value for name %s', name)
            logging.warning(exception)

        return value


    def get_secret_value(self, name) -> str:
        """
        Fetch encrypted secret from Secrets Manager
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html
        """

        value = None
        logging.debug('Fetching AWS Secrets Manager secret: %s', name)

        try:
            response = self.secretsmanager.get_secret_value(SecretId=name)
            if 'SecretString' in response:
                value = response['SecretString']
            elif 'SecretBinary' in response:
                value = response['SecretBinary']
                if isinstance(value, bytes):
                    value = value.decode('utf-8')
        except (
            botocore.exceptions.ClientError,
            botocore.exceptions.NoCredentialsError,
            self.secretsmanager.exceptions.ResourceNotFoundException,
            self.secretsmanager.exceptions.InvalidParameterException,
            self.secretsmanager.exceptions.InvalidRequestException,
            self.secretsmanager.exceptions.DecryptionFailure,
            self.secretsmanager.exceptions.InternalServiceError,
        ) as exception:
            logging.warning('Unable to retrieve AWS Secrets Manager value for name %s', name)
            logging.warning(exception)

        return value


    def send_email(self, recipients: str, sender: str, subject: str, text: str):
        """
        Send plain text email using AWS Simple Email Service (SES)
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html
        """

        response = None

        try:
            response = self.ses.send_email(
                Source=sender,
                Destination={
                    'ToAddresses': [
                        recipients
                    ]
                },
                Message={
                    'Subject': {
                        'Data': subject,
                    },
                    'Body': {
                        'Text': {
                            'Data': text
                        }
                    }
                }
            )
        except (
            ValueError,
            botocore.exceptions.ClientError,
            botocore.exceptions.NoCredentialsError,
            self.ses.exceptions.MessageRejected,
            self.ses.exceptions.MailFromDomainNotVerifiedException,
            self.ses.exceptions.ConfigurationSetDoesNotExistException,
            self.ses.exceptions.ConfigurationSetSendingPausedException,
            self.ses.exceptions.AccountSendingPausedException
        ) as exception:
            logging.warning('Unable to send AWS SES Email')
            logging.warning(exception)

        return response


    def put_dynamodb_item(self, table:str, fields:dict):
        """
        Put a dictionary item into a DynamoDB table.
        Put operation uses Service Resource, exceptions
        use the client
        """

        client = boto3.client('dynamodb')

        logging.debug('Writing to table %s', table)

        # Combine new attribute dictionary with partition and sort key dictionary
        item = fields | {
            'id': str(uuid.uuid4()),
            'timestamp': int(time())
        }

        response = None

        try:
            response = self.dynamodb.batch_write_item(
                RequestItems = {
                    table: [
                        {
                            'PutRequest': {
                                'Item': item
                            },
                        },
                    ]
                },
                ReturnItemCollectionMetrics = 'SIZE'
            )
        except (
            botocore.exceptions.ClientError,
            botocore.exceptions.NoCredentialsError,
            client.exceptions.ConditionalCheckFailedException,
            client.exceptions.ProvisionedThroughputExceededException,
            client.exceptions.ResourceNotFoundException,
            client.exceptions.ItemCollectionSizeLimitExceededException,
            client.exceptions.TransactionConflictException,
            client.exceptions.RequestLimitExceeded,
            client.exceptions.InternalServerError,
        ) as exception:
            logging.warning('Unable to put AWS DynamoDB item')
            logging.warning(exception)

        return response
