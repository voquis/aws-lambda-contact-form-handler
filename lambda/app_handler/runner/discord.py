import json
import logging
from string import Template

from app_handler.service.discord import DiscordService
from app_handler.provider.config import ConfigProvider
from app_handler.provider.request import RequestProvider
from app_handler.provider.response import ResponseProvider
from app_handler.utils.functions import string_to_dict

class DiscordRunner:
    def __init__(self) -> None:

        # Set default values
        self.error_response = None
        self.enable = None
        self.webhook_id = None
        self.webhook_token = None
        self.message_template = None
        self.fields = {}

    def configure(self):
        """
        Configure builder
        """
        configs = ConfigProvider()
        logging.debug("Initialising discord config")
        self.enable = configs.get('DISCORD_ENABLE').lower() == 'true'
        logging.debug("Discord enable: %s", self.enable)

        # If enabled, retrieve additional configs
        if self.enable:
            logging.debug('Configuring additional Discord settings')
            self.webhook_id = configs.get('DISCORD_WEBHOOK_ID')
            self.webhook_token = configs.get('DISCORD_WEBHOOK_TOKEN')
            self.json_template = configs.get('DISCORD_JSON_TEMPLATE')

            # Verify json template is valid
            try:
                json.loads(self.json_template, strict=False)
            except json.JSONDecodeError as exception:
                message = 'Error decoding Discord JSON template'
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
            except KeyError as exception:
                logging.critical('Discord template parsing error')
                logging.critical(exception)
                self.error_response = response_provider.message('Notification service error', 500)
                return

            # Set up Discord client
            try:
                discord_client = DiscordService(
                    self.webhook_id,
                    self.webhook_token,
                    body
                )
            except ValueError as exception:
                # 500 error if service initiation error
                logging.critical('Discord service initiation error')
                logging.critical(exception)
                self.error_response = response_provider.message('Notification service error', 500)
                return

            # Attempt to send templated message
            response = discord_client.send()
            if not response or 'status' not in response or response['status'] > 400:
                # 500 error if service runtime error
                logging.critical('Discord HTTP error')
                self.error_response = response_provider.message('Notification service error', 500)
                return

            return response
