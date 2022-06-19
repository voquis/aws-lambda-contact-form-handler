import logging
from json import JSONDecodeError

from app_handler.provider.config import ConfigProvider
from app_handler.provider.request import RequestProvider
from app_handler.provider.response import ResponseProvider
from app_handler.utils.functions import string_to_dict

class AppRunner:
    """
    Runner to configure and execute main application
    Configures request and respones providers.
    Ensures required fields are present in incoming event payload.
    """
    def __init__(self) -> None:

        # Set default values
        self.required_fields = {}
        self.request_provider = {}
        self.error_response = None


    def configure(self):
        """
        Configure app builder using Config provider
        """
        configs = ConfigProvider()

        # Extract required field names into config object
        self.required_fields = string_to_dict(configs.get('REQUIRED_FIELDS'))


    def run(self, event):
        """
        Run app and capture any errors
        """

        response_provider = ResponseProvider(event)
        self.request_provider = RequestProvider(event)
        if self.request_provider.has_error:
            # 400 error if provided bad JSON
            self.error_response = response_provider.message('Error parsing request', 400)
            return

        self.request_body = self.request_provider.content

        for field in self.required_fields:
            if field not in self.request_body:
                # 400 error if request did not contain a required field
                message = f'Missing required field `{field}`'
                logging.warning(message)
                self.error_response = response_provider.message(message, 400)
                return

            if len(self.request_body[field]) == 0:
                # 400 error if required field exists but is empty
                message = f'Required field empty `{field}`'
                logging.warning(message)
                self.error_response = response_provider.message(message, 400)
                return
