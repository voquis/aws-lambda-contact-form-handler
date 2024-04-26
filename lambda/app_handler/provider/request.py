"""
Parse incoming request to lambda
"""

import base64
import json
from json import JSONDecodeError
import urllib
import logging

class RequestProvider:
    """
    Parse incoming request to lambda
    """
    def __init__(self, payload):
        self.payload = payload
        self.content = payload
        self.has_error = None
        self.matched = False
        self.parse(payload)

    def parse(self, payload):
        """
        Parse incoming payload and retrieve content.
        Handles the following cases:
            - Invocation as a Python function
            - Invocation of Lambda function
            - Invocation behind an AWS HTTP v2 API Gateway
            - Invocation by an SNS topic
        """

        # Check if lambda was invoked as an SNS message
        if self.is_sns_message(payload):
            return

        if 'body' not in payload:
            logging.debug('Body not in payload, returning payload')
            return

        self.content = payload['body']

        if 'isBase64Encoded' in payload and payload['isBase64Encoded'] is True:
            logging.debug('Body is base64 encoded, decoding')
            self.content = str(base64.b64decode(payload['body']), "utf-8")

        if 'headers' not in payload:
            logging.debug('No headers present, using body')
            return

        headers = payload['headers']
        # Ensure headers object is a non-empty dictionary
        if not isinstance(headers, dict) or not headers:
            logging.debug('Unexpected headers object format')
            return

        # Lowercase all headers
        headers_lower = {}
        for key, value in headers.items():
            if isinstance(key, str) and isinstance(value, str):
                headers_lower[key.lower()] = value.lower()

        if 'content-type' not in headers_lower:
            logging.debug('Content-Type header not present, returning body')
            return

        content_type = headers_lower['content-type']

        content_type = content_type.lower()
        logging.debug('Content-Type detected: %s', content_type)

        self.is_form_url_encoded(content_type=content_type)

        self.is_application_json(content_type=content_type)

        if not self.matched:
            logging.critical('Error determining how to load content type.')
            self.has_error = True

    def get_remote_ip(self):
        """
        Extract remote IP address from request, if provided
        """
        remote_ip = None

        try:
            # V2 gateway request
            remote_ip = self.payload['requestContext']['http']['sourceIp']
        except KeyError:
            pass

        try:
            # V1 gateway request
            remote_ip = self.payload['requestContext']['identity']['sourceIp']
        except KeyError:
            pass

        logging.debug('Fetched remote IP from payload: %s', remote_ip)

        return remote_ip


    def is_sns_message(self, payload):
        """
        Determine if payload is an SNS message
        """
        # Handle first SNS message
        if 'Records' in payload and isinstance(payload['Records'], list):
            record = payload['Records'][0]
            if 'Sns' in record and 'Message' in record['Sns'] and 'Subject' in record['Sns']:
                logging.debug('SNS payload extracted')
                self.content = record['Sns']
                return True

        return False


    def is_application_json(self, content_type: str):
        """
        Determine of payload is JSON
        """
        if content_type.startswith('application/json'):
            logging.debug('Loading JSON string')
            try:
                self.content = json.loads(self.content, strict=False)
                logging.debug(self.content)
                self.matched = True
            except (
                JSONDecodeError,
                TypeError
            ) as exception:
                logging.critical('Error loading string as JSON')
                logging.critical(exception)
                self.has_error = True


    def is_form_url_encoded(self, content_type: str):
        """
        Determine if payload is form URL encoded
        """
        if content_type.startswith('application/x-www-form-urlencoded'):
            logging.debug('Decoding URL encoded form')
            try:
                html_decoded = urllib.parse.unquote(self.content)
                # Assume each value should only appear once, drop repeat keys
                self.content = dict(urllib.parse.parse_qsl(html_decoded))
                logging.debug(self.content)
                self.matched = True
            except(
                AttributeError,
                ValueError
            ) as exception:
                logging.critical('Error decoding URL encoded form')
                logging.critical(exception)
                self.has_error = True
