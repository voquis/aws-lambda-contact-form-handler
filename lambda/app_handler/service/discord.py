"""
Class to post messages to a Discord server.
For API usage see https://discord.com/developers/docs/resources/webhook#execute-webhook
"""

import json
import logging
from app_handler.service.http import HttpService

class DiscordService:
    """
    Makes HTTP calls to Discord service
    """

    def __init__(
        self,
        webhook_id:str,
        webhook_token:str,
        body:str,
        base_url:str = 'https://discord.com/api/webhooks'
    ) -> None:

        if body is None:
            message = 'Missing Discord body'
            logging.critical(message)
            raise ValueError(message)

        if webhook_id is None or webhook_token is None:
            message = 'Missing Discord webhook id or token'
            logging.critical(message)
            raise ValueError(message)

        self.parse_body(body)

        # Set up inputs
        self.url = f'{base_url}/{webhook_id}/{webhook_token}'
        self.response = None

        logging.debug('Discord service configured')


    def parse_body(self, body):
        """
        Parse string JSON to JSON dictionary and back to validate
        """
        # Attempt to validate template
        try:
            self.body = json.dumps(json.loads(body))
        except json.JSONDecodeError as exception:
            message = 'Error parsing Discord JSON template'
            logging.critical(message)
            raise ValueError(message) from exception


    def send(self):
        """
        Send Discord message
        """

        http_service = HttpService()
        self.response = http_service.post_json(self.url, self.body)
        return self.response
