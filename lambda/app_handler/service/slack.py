"""
Class to post messages to a Slack workspace.
For API usage see https://api.slack.com/messaging/webhooks
"""

import logging
from app_handler.service.http_post_json import HttpPostJsonService

class SlackService(HttpPostJsonService):
    """
    Makes HTTP calls to Slack service
    """

    def __init__(
        self,
        slack_webhook_url:str,
        body:str,
    ) -> None:

        super().__init__(slack_webhook_url, body)

        logging.debug('Slack service configured')
