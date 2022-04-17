"""
Module to configure application based on environment variables
"""
import logging

from app_handler.provider.response import ResponseProvider
from app_handler.runner.app import AppRunner
from app_handler.runner.discord import DiscordRunner
from app_handler.runner.email import EmailRunner
from app_handler.runner.hcaptcha import HcaptchaRunner
from app_handler.runner.dynamodb import DynamodbRunner

class AppProvider:
    """
    Main App handler
    """
    def __init__(self, event) -> None:
        """
        Configure application using supplied environment variables
        """
        # Prepare providers
        self.response_provider = None
        # Prepare runners
        self.app_runner = AppRunner()
        self.dynamodb_runner = DynamodbRunner()
        self.hcaptcha_runner = HcaptchaRunner()
        self.email_runner = EmailRunner()
        self.discord_runner = DiscordRunner()

        # Process event
        self.process(event)


    def process(self, event) -> None:
        """
        Process event payload sent to lambda
        """
        # Prepare request and respones providers
        self.response_provider = ResponseProvider(event)

        # Attempt to initialise configs
        try:
            self.app_runner.configure()
            self.hcaptcha_runner.configure()
            self.dynamodb_runner.configure()
            self.email_runner.configure()
            self.discord_runner.configure()
        except ValueError:
            # 500 error if any configs fail
            logging.critical('Error configuring services')
            self.response = self.response_provider.message('Error configuring services', 500)
            return

        # Process remaining logic
        self.response = self.get_response(event)


    def get_response(self, event):
        """
        Assuming all initialisations are complete, calculate the response
        """

        # Core application runner that processes request
        logging.debug('Executing app runner')
        self.app_runner.run(event)
        if self.app_runner.error_response is not None:
            logging.critical('Error executing app runner')
            return self.app_runner.error_response

        request_provider = self.app_runner.request_provider

        # Optionally perform hCaptcha validation
        logging.debug('Executing hCaptcha runner')
        self.hcaptcha_runner.run(request_provider, self.response_provider)
        if self.hcaptcha_runner.error_response is not None:
            logging.critical('Error executing hcaptcha runner')
            return self.hcaptcha_runner.error_response

        # Optionally log to DynamoDB
        logging.debug('Executing dynamodb runner')
        self.dynamodb_runner.run(request_provider, self.response_provider)
        if self.dynamodb_runner.error_response is not None:
            logging.critical('Error executing dynamodb runner')
            return self.dynamodb_runner.error_response

        # Optionally send email message
        logging.debug('Executing Email runner')
        self.email_runner.run(request_provider, self.response_provider)
        if self.email_runner.error_response is not None:
            logging.critical('Error executing email runner')
            return self.email_runner.error_response

        # Optionally send Discord message
        logging.debug('Executing Discord runner')
        self.discord_runner.run(request_provider, self.response_provider)
        if self.discord_runner.error_response is not None:
            logging.critical('Error executing Discord runner')
            return self.discord_runner.error_response

        # Successful result
        return self.response_provider.message('Message received')
