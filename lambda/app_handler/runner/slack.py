import json
import logging
from string import Template

from app_handler.service.slack import SlackService
from app_handler.provider.config import ConfigProvider
from app_handler.provider.request import RequestProvider
from app_handler.provider.response import ResponseProvider
from app_handler.utils.functions import string_to_dict

class SlackRunner:
    def __init__(self) -> None:

        # Set default values
        self.error_response = None
        self.enable = None
        self.webhook_url = None
        self.message_template = None
        self.fields = {}

    def configure(self):
        """
        Configure builder
        """
        configs = ConfigProvider()
        logging.debug("Initialising Slack config")
        self.enable = configs.get('SLACK_ENABLE').lower() == 'true'
        logging.debug("Slack enable: %s", self.enable)

        # If enabled, retrieve additional configs
        if self.enable:
            logging.debug('Configuring additional Skacj settings')
            self.webhook_url = configs.get('SLACK_WEBHOOK_URL')
            self.json_template = configs.get('SLACK_JSON_TEMPLATE')

            # Verify json template is valid
            try:
                json.loads(self.json_template, strict=False)
            except json.JSONDecodeError as exception:
                message = 'Error decoding Slack JSON template'
                logging.critical(message)
                logging.critical(exception)
                raise ValueError(message) from exception

            # Extract required field names into config object
            self.fields = string_to_dict(configs.get('REQUIRED_FIELDS'))


    def run(self, request_provider:RequestProvider, response_provider:ResponseProvider):
        """
        Run builder
        """

        if self.enable:

            # Extract required fields from request body for template
            fields = {}
            for field in self.fields:
                try:
                    fields[field] = request_provider.content[field]
                except KeyError as exception:
                    logging.critical('Field extraction error for key: %s', field)
                    logging.critical(exception)
                    self.error_response = response_provider.message('Notification service error', 500)
                    return

            self.fields = fields

            # Attempt to build string body from template
            string_template = Template(self.json_template)
            try:
                body = string_template.substitute(fields)
            except (
                KeyError,
                ValueError
            ) as exception:
                logging.critical('Slack template parsing error')
                logging.critical(exception)
                self.error_response = response_provider.message('Notification service error', 500)
                return

            # Set up Slack client
            try:
                slack_client = SlackService(
                    self.webhook_url,
                    body
                )
            except ValueError as exception:
                # 500 error if service initiation error
                logging.critical('Slack service initiation error')
                logging.critical(exception)
                self.error_response = response_provider.message('Notification service error', 500)
                return

            # Attempt to send templated message
            response = slack_client.send()
            if not response or 'status' not in response or response['status'] > 400:
                # 500 error if service runtime error
                logging.critical('Slack HTTP error')
                self.error_response = response_provider.message('Notification service error', 500)
                return

            return response
