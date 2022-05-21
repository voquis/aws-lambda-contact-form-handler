"""
Pytest unit tests for discord service
"""

import pytest
import httpretty
from app_handler.service.discord import DiscordService
import tests.unit.service.discord_utils as utils

DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/123/abc'

def test_missing_args():
    """
    Check class throws exception when initialised with incorrect parameters.
    """

    with pytest.raises(ValueError) as exception:
        DiscordService(None, None)
        assert 'body' in str(exception.value)

    with pytest.raises(ValueError) as exception:
        DiscordService(None, 'body')
        assert 'url' in str(exception.value)

    with pytest.raises(ValueError) as exception:
        DiscordService('abc', '{bad-json"')
        assert 'JSON' in str(exception.value)


@httpretty.activate(allow_net_connect=False)
def test_unauthenticated():
    """
    Check class throws exception when mocked remote returns auth error
    """

    # Set up HTTP client mock to prevent communication with real backend
    utils.httpretty_register_discord_webhook_unauthorised()

    # Initialise client
    discord = DiscordService(DISCORD_WEBHOOK_URL, '{}')

    # Call remote method (intercepted by httpretty) and except exception
    response = discord.send()
    assert response['status'] == 401


@httpretty.activate(allow_net_connect=False)
def test_error():
    """
    Verify a mocked failure is processed correctly
    """

    utils.httpretty_register_discord_webhook_failure()

    # Initialise client
    discord = DiscordService(DISCORD_WEBHOOK_URL, '{}')

    # Call remote method (intercepted by httpretty) and except exception
    response = discord.send()

    assert response['status'] == 400


@httpretty.activate(allow_net_connect=False)
def test_error_bad_json():
    """
    Verify a mocked failure is processed correctly
    """

    utils.httpretty_register_discord_webhook_failure_bad_json()

    # Initialise client
    discord = DiscordService(DISCORD_WEBHOOK_URL, '{}')

    # Call remote method (intercepted by httpretty) and except exception
    response = discord.send()

    assert response['status'] == 400


@httpretty.activate(allow_net_connect=False)
def test_success():
    """
    Verify a mocked success is processed correctly
    """

    utils.httpretty_register_discord_webhook_success()

    # Initialise client
    discord = DiscordService(DISCORD_WEBHOOK_URL, '{}')

    # Perform validation check
    response = discord.send()
    assert response['status'] == 204
