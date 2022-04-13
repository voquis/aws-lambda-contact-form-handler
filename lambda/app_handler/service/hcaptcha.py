"""
Class to validate user challenges against hCAPTCHA web service.
For API usage see https://docs.hcaptcha.com
"""

import logging
from app_handler.service.http import HttpService

class HcaptchaService:
    """
    Makes HTTP calls to hCAPTCHA service
    """

    def __init__(self, secret, sitekey, url='https://hcaptcha.com/siteverify') -> None:
        # Set up inputs
        self.secret = secret
        self.sitekey = sitekey
        self.url = url
        self.response = None
        self.success = None
        self.error_codes = []

        if self.secret is None or self.sitekey is None:
            message = 'Missing hCaptcha secret or sitekey'
            logging.critical(message)
            raise ValueError(message)

        logging.debug('hCaptcha client configured with url %s', self.url)


    def validate(self, user_response, remote_ip=None):
        """
        Perform validation of user supplied response to challenge
        https://docs.hcaptcha.com/#verify-the-user-response-server-side
        """

        data = {
            'secret': self.secret,
            'response': user_response,
            'remoteip': '127.0.0.1' if remote_ip is None else remote_ip,
            'sitekey': self.sitekey,
        }

        logging.debug('Checking if hCaptcha request is valid')

        http_service = HttpService()
        self.response = http_service.post_urlencoded(self.url, data)
        self.process_response()
        return self.response

    def process_response(self) -> None:
        """
        Process validation response result, check for error codes
        https://docs.hcaptcha.com/#siteverify-error-codes-table
        """

        status = self.response['status']
        # Ensure a 200 or 300 status code is returned, otherwise throw exception
        if status < 400:
            json_result = self.response['json']

            self.success = json_result['success']

            self.error_codes = []

            if not self.success:
                logging.warning('hCaptcha verification failed with errors')
                if 'error-codes' in json_result:
                    logging.warning(json_result['error-codes'])
                    self.error_codes = json_result['error-codes']
