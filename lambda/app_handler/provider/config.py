"""
Configuration provider to fetch values from the following sources:
- Environment variables
- AWS Systems manager (SSM) Parameter store
"""
import os
import logging
from app_handler.service.aws import AwsService


class ConfigProvider:
    """
    Configuration provider class
    """
    def __init__(self) -> None:
        self.env_defaults = {
            "REQUIRED_FIELDS": None,
            "HCAPTCHA_ENABLE": "False",
            "HCAPTCHA_RESPONSE_FIELD": "captcha-response",
            "HCAPTCHA_VERIFY_URL": "https://hcaptcha.com/siteverify",
            "DATABASE_ENABLE": "False",
            "EMAIL_ENABLE": "False",
            "EMAIL_SUBJECT_TEMPLATE": "Contact received",
            "EMAIL_TEXT_TEMPLATE": "A contact message was received",
            "DISCORD_ENABLE": "False",
            "DISCORD_JSON_TEMPLATE": '{"username": "Handler", "content": "Message received"}',
        }

        self.parameter_store_defaults = {
            "HCAPTCHA_SITEKEY_PARAMETER_STORE_NAME": "/hcaptcha/sitekey",
            "HCAPTCHA_SECRET_PARAMETER_STORE_NAME": "/hcaptcha/secret",
            "DISCORD_WEBHOOK_ID_PARAMETER_STORE_NAME": "/discord/webhook/id",
            "DISCORD_WEBHOOK_TOKEN_PARAMETER_STORE_NAME": "/discord/webhook/token",
        }

        self.secrets_manager_defaults = {
            "HCAPTCHA_SITEKEY_SECRETS_MANAGER_NAME": "/hcaptcha/sitekey",
            "HCAPTCHA_SECRET_SECRETS_MANAGER_NAME": "/hcaptcha/secret",
            "DISCORD_WEBHOOK_ID_SECRETS_MANAGER_NAME": "/discord/webhook/id",
            "DISCORD_WEBHOOK_TOKEN_SECRETS_MANAGER_NAME": "/discord/webhook/token",
        }

    def get(self, value_name: str) -> str:
        """
        Given a key name SOME_VALUE, check for a source env var e.g. SOME_VALUE_SOURCE
        """
        # Make the provided name all-uppercase
        value_name = value_name.upper()

        logging.debug('Retrieving value for %s', value_name)
        source = os.environ.get(f'{value_name}_SOURCE', 'env').lower()
        logging.debug('%s source: %s', value_name, source)
        # Get value from environment variable
        if source == 'env':
            return self.get_from_env(value_name)

        # Get value from AWS SSM parameter store
        if source == 'aws_ssm_parameter_store':
            return self.get_from_aws_ssm_parameter_store(value_name)

        if source == 'aws_secrets_manager':
            return self.get_from_aws_secrets_manager(value_name)

        message = f'Unknown source {source}'
        logging.critical(message)
        raise ValueError(message)


    def get_from_env(self, value_name: str) -> str:
        """
        Fetch a value from environment variables, using a default if available.
        """
        logging.debug('Checking environment for variable: %s', value_name)
        value = os.environ.get(value_name, '').strip()
        if value == '':
            if value_name not in self.env_defaults:
                message = f'Missing or empty environment value for {value_name}'
                logging.critical(message)
                raise ValueError(message)

            logging.debug('Using default value for environment variable: %s', value_name)
            value = self.env_defaults[value_name]

        return value


    def get_from_aws_ssm_parameter_store(self, value_name: str) -> str:
        """
        Fetch a value from AWS SSM Parameter store
        """
        parameter_name_var = f'{value_name}_PARAMETER_STORE_NAME'
        logging.debug('Checking environment for AWS SSM Parameter name: %s', parameter_name_var)

        parameter_name = None

        try:
            parameter_name = self.parameter_store_defaults[parameter_name_var]
        except KeyError:
            logging.debug('No default parameter name for: %s', value_name)

        custom_parameter_name = os.environ.get(parameter_name_var, '').strip()

        if custom_parameter_name != '':
            parameter_name = custom_parameter_name

        if not parameter_name and not custom_parameter_name:
            message = f'No Default or provided parameter name for {value_name}'
            logging.warning(message)
            raise ValueError(message)

        logging.debug('Using parameter name %s', parameter_name)
        aws = AwsService()
        value = aws.get_parameter_value(parameter_name)
        if value is None or value == '':
            message = f'Missing or empty AWS SSM Parameter Store value for {value_name}'
            logging.critical(message)
            raise ValueError(message)

        return value


    def get_from_aws_secrets_manager(self, secret_name: str) -> str:
        """
        Fetch a secret from AWS Secrets Manager
        """
        secret_name_var = f'{secret_name}_SECRETS_MANAGER_NAME'
        logging.debug('Checking environment for AWS Secret Manager name: %s', secret_name_var)

        secret_name = None

        try:
            secret_name = self.secrets_manager_defaults[secret_name_var]
        except KeyError:
            logging.debug('No default secret name for: %s', secret_name)

        custom_secret_name = os.environ.get(secret_name_var, '').strip()

        if custom_secret_name != '':
            secret_name = custom_secret_name

        if not secret_name and not custom_secret_name:
            message = f'No Default or provided secret name for {secret_name}'
            logging.warning(message)
            raise ValueError(message)

        logging.debug('Using secret name %s', secret_name)
        aws = AwsService()
        value = aws.get_secret_value(secret_name)
        if value is None or value == '':
            message = f'Missing or empty AWS Secrets Manager value for {secret_name}'
            logging.critical(message)
            raise ValueError(message)

        return value
