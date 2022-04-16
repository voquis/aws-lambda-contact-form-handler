import logging
from app_handler.provider.config import ConfigProvider
from app_handler.provider.request import RequestProvider
from app_handler.provider.response import ResponseProvider
from app_handler.service.aws import AwsService
from app_handler.utils.functions import string_to_dict

class DatabaseRunner:
    def __init__(self) -> None:

        # Set default values
        self.error_response = None
        self.table = None
        self.enable = None
        self.fields = {}

    def configure(self):
        """
        Configure runner
        """
        logging.debug('Configuring %s', __class__.__name__ )
        configs = ConfigProvider()

        self.enable = configs.get('DATABASE_ENABLE').lower() == 'true'
        logging.debug("Store to database enable: %s", self.enable)

        if self.enable:
            # If email sending is enabled, retrieve additional settings
            self.table = configs.get('DATABASE_TABLE')
            # Extract required field names into config object
            self.fields = string_to_dict(configs.get('REQUIRED_FIELDS'))

    def run(self, request_provider:RequestProvider, response_provider:ResponseProvider):
        """
        Run app
        """

        if self.enable:

            # Extract fields from request body for template
            fields = {}
            for field in self.fields:
                try:
                    fields[field] = request_provider.content[field]
                except KeyError:
                    logging.critical('Field extraction error for key: %s', field)
                    self.error_response = response_provider.message('Notification service error', 500)
                    return
            self.fields = fields

            aws = AwsService()
            result = aws.put_dynamodb_item(
                self.table,
                self.fields
            )
            if not result:
                # 500 error if service result was not successful
                logging.critical('Database saving error')
                self.error_response = response_provider.message('Storage service error', 500)

            return result
