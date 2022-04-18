import logging
from string import Template
from app_handler.provider.config import ConfigProvider
from app_handler.provider.request import RequestProvider
from app_handler.provider.response import ResponseProvider
from app_handler.service.aws import AwsService
from app_handler.utils.functions import string_to_dict

class EmailRunner:
    def __init__(self) -> None:

        # Set default values
        self.error_response = None
        self.sender = None
        self.subject = None
        self.recipients = None
        self.subject_template = None
        self.text_template = None
        self.fields = None

    def configure(self):
        """
        Configure app builder
        """
        logging.debug('Configuring %s', __class__.__name__ )
        configs = ConfigProvider()

        self.enable = configs.get('EMAIL_ENABLE').lower() == 'true'
        logging.debug("Email sending enable: %s", self.enable)

        if self.enable:
            # If email sending is enabled, retrieve additional settings
            self.sender = configs.get('EMAIL_SENDER')
            self.recipients = configs.get('EMAIL_RECIPIENTS')
            self.subject_template = configs.get('EMAIL_SUBJECT_TEMPLATE')
            self.text_template = configs.get('EMAIL_TEXT_TEMPLATE')

            # Extract required field names into config object
            self.fields = string_to_dict(configs.get('REQUIRED_FIELDS'))

    def run(self, request_provider:RequestProvider, response_provider:ResponseProvider):
        """
        Run app
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

            # Build string body from text template
            # Build subject from template
            text_template = Template(self.text_template)
            subject_template = Template(self.subject_template)
            try:
                body = text_template.substitute(self.fields)
                subject = subject_template.substitute(self.fields)
            except KeyError as exception:
                logging.critical('Discord template parsing error')
                logging.critical(exception)
                self.error_response = response_provider.message('Notification service error', 500)
                return

            aws = AwsService()
            result = aws.send_email(
                self.recipients,
                self.sender,
                subject,
                body
            )

            if not result:
                # 500 error if service error
                logging.critical('Email sending error HTTP error')
                self.error_response = response_provider.message('Notification service error', 500)

            return result
