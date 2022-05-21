"""
Class to post messages to a Discord server.
For API usage see https://discord.com/developers/docs/resources/webhook#execute-webhook
"""

import logging
from app_handler.service.http_post_json import HttpPostJsonService

class DiscordService(HttpPostJsonService):
    """
    Makes HTTP calls to Discord service
    """

    def __init__(
        self,
        discord_webhook_url:str,
        body:str,
    ) -> None:

        super().__init__(discord_webhook_url, body)

        logging.debug('Discord service configured')
