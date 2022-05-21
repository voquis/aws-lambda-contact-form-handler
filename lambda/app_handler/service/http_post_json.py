"""
Class to send a HTTP POST JSON body to a URL
"""

import json
import logging
from app_handler.service.http import HttpService

class HttpPostJsonService:
    """
    Post a JSON payload to a HTTP service
    """

    def __init__(
        self,
        url:str,
        body:str,
    ) -> None:

        if body is None:
            message = 'Missing body for HTTP POST JSON'
            logging.critical(message)
            raise ValueError(message)

        if url is None :
            message = 'Missing url for HTTP POST JSON'
            logging.critical(message)
            raise ValueError(message)

        self.parse_body(body)

        # Set up inputs
        self.url = url
        self.response = None

        logging.debug('HTTP POST JSON service configured')


    def parse_body(self, body):
        """
        Parse string JSON to JSON dictionary and back to validate
        """
        # Attempt to validate template
        try:
            self.body = json.dumps(json.loads(body,strict=False))
        except json.JSONDecodeError as exception:
            message = 'Error parsing HTTP POST JSON template'
            logging.critical(message)
            logging.critical(exception)
            raise ValueError(message) from exception


    def send(self):
        """
        Send HTTP message
        """

        http_service = HttpService()
        self.response = http_service.post_json(self.url, self.body)
        return self.response
