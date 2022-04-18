
import logging
from urllib.error import HTTPError

from app_handler.service.hcaptcha import HcaptchaService
from app_handler.provider.config import ConfigProvider
from app_handler.provider.response import ResponseProvider

class HcaptchaRunner:
    def __init__(self) -> None:

        # Set default values
        self.error_response = None
        self.enable = None
        self.sitekey = None
        self.secret = None
        self.verify_url = None
        self.response_field = None

    def configure(self):
        """
        Configure builder
        """
        configs = ConfigProvider()
        logging.debug("Initialising hcaptca config")
        self.enable = configs.get('HCAPTCHA_ENABLE').lower() == 'true'
        logging.debug("hCaptch enable: %s", self.enable)

        # If enabled, retrieve additional configs
        if self.enable:
            logging.debug('Configuring additional hCaptch settings')
            self.sitekey = configs.get('HCAPTCHA_SITEKEY')
            self.secret = configs.get('HCAPTCHA_SECRET')
            self.verify_url = configs.get('HCAPTCHA_VERIFY_URL')
            self.response_field = configs.get('HCAPTCHA_RESPONSE_FIELD')


    def run(self, request_provider, response_provider: ResponseProvider):
        """
        Run builder
        """

        if self.enable:
            logging.debug('Fetching user response using field name: %s', self.response_field)
            # 400 error if request did not contain a captcha user response
            try:
                user_response = request_provider.content[self.response_field]
            except (
                KeyError,
                TypeError
            ):
                logging.warning('No user response field in request: %s', self.response_field)
                self.error_response = response_provider.message('Missing captcha user response field', 400)
                return

            hcaptcha_service = HcaptchaService(
                self.secret,
                self.sitekey,
                self.verify_url
            )

            user_ip = request_provider.get_remote_ip()

            # Perform validation
            response = hcaptcha_service.validate(user_response, user_ip)
            # 500 error if service has failed
            if not response or 'status' not in response or response['status'] > 400:
                # 500 error if service runtime error
                logging.critical('hCaptcha HTTP error')
                self.error_response = response_provider.message('Notification service error', 500)
                return

            if not hcaptcha_service.success:
                # 401 unauthorised if captcha validation fails
                message = 'captcha validation failed'
                logging.info(message)
                self.error_response = response_provider.message(message, 401)

            return response
