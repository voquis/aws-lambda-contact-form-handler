"""
Class to send data over HTTP
"""

import json
import logging
from urllib import request
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request


class HttpService():
    """
    HTTP Service to post json and url encoded data
    Attempts to decode response to JSON
    """

    def __init__(self) -> None:
        self.user_agent = 'python/3'
        self.response = None
        self.request_body = None

    def post_json(self, url, data:dict, encoding:str = 'utf-8'):
        """
        Post JSON data
        """

        json_data = data

        # Attempt to serialise data
        try:
            if isinstance(data, str):
                json_data = json.dumps(json.loads(data))
            else:
                json_data = json.dumps(data)
        except (
            AttributeError,
            json.JSONDecodeError,
            TypeError
        ) as exception:
            message = 'Cannot JSON serialise data'
            logging.warning(message)
            logging.warning(exception)
            raise ValueError(message) from exception

        # Attempt to encode data
        encoded = json_data.encode(encoding)

        try:
            req = Request(url)
        except ValueError as exception:
            message = 'Unable to parse HTTP request URL'
            logging.critical(message)
            logging.critical(exception)
            raise ValueError(message) from exception

        req.add_header('Content-Type', 'application/json')

        return self._post(req, encoded)


    def post_urlencoded(self, url, data:dict, encoding:str = 'utf-8'):
        """
        Post URL Encoded data
        """
        encoded = urlencode(data).encode(encoding)
        req = Request(url)
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')

        return self._post(req, encoded)


    def _post(self, req, data):
        """
        Make HTTP Post request.
        Attempt to decode JSON response
        """
        self.request_body = data

        self.response = None

        req.add_header('User-Agent', self.user_agent)

        status = None
        headers = None
        body = None
        json_body = None

        logging.debug('Sending HTTP request')

        try:
            with request.urlopen(req, data) as res:
                # Extract expected values
                body = res.read().decode()
                status = res.status
                headers = res.getheaders()

                # Attempt to load body as JSON
                try:
                    json_body = json.loads(body)
                except json.JSONDecodeError:
                    pass

        except HTTPError as exception:
            logging.warning('HTTP Error encountered')
            logging.warning(exception)

            # Extract expected values
            body = exception.read().decode()
            status = exception.status
            headers = exception.headers.items()

            try:
                json_body = json.loads(body)
            except json.JSONDecodeError:
                pass

        except URLError as exception:
            logging.warning('Unable to make HTTP Post request')
            logging.warning(exception)

        logging.debug('HTTP Status code %s', status)

        self.response = {
            "status": status,
            "headers": headers,
            "body": body,
            "json": json_body
        }

        return self.response
