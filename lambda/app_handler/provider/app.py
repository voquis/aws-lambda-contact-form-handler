"""
Module to configure application based on environment variables
"""
import logging

from app_handler.provider.response import ResponseProvider
from app_handler.runner.app import AppRunner
from app_handler.runner.discord import DiscordRunner
from app_handler.runner.dynamodb import DynamodbRunner
from app_handler.runner.email import EmailRunner
from app_handler.runner.hcaptcha import HcaptchaRunner
from app_handler.runner.slack import SlackRunner

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
        self.hcaptcha_runner = HcaptchaRunner()
        self.runners = {}
        # Process event
        self.process(event)


    def process(self, event) -> None:
        """
        Process event payload sent to lambda
        """
        # Prepare request and response providers
        self.response_provider = ResponseProvider(event)

        self.runners['discord'] = DiscordRunner()
        self.runners['dynamodb'] = DynamodbRunner()
        self.runners['email'] = EmailRunner()
        self.runners['slack'] = SlackRunner()

        # Attempt to initialise configs
        try:
            self.app_runner.configure()
            self.hcaptcha_runner.configure()
            self.runners['discord'].configure()
            self.runners['dynamodb'].configure()
            self.runners['email'].configure()
            self.runners['slack'].configure()
        except ValueError as exception:
            # 500 error if any configs fail
            logging.critical('Error configuring services')
            logging.critical(exception)
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
            logging.critical(self.app_runner.error_response)
            return self.app_runner.error_response

        request_provider = self.app_runner.request_provider

        # hCapture runner that should prevent further runners if validation fails
        logging.debug('Executing hCaptcha runner')
        self.hcaptcha_runner.run(request_provider, self.response_provider)
        if self.hcaptcha_runner.error_response is not None:
            logging.critical('Error executing hCaptcha runner')
            logging.critical(self.hcaptcha_runner.error_response)
            return self.hcaptcha_runner.error_response

        # Iterate through all remaining runners and handle any failures
        for runner_name, runner in self.runners.items():
            logging.debug('Executing %s runner', runner_name)
            runner.run(request_provider, self.response_provider)
            if runner.error_response is not None:
                logging.critical('Error executing %s runner', runner_name)
                logging.critical(runner.error_response)
                return runner.error_response


        # Successful result
        return self.response_provider.message('Message received')
