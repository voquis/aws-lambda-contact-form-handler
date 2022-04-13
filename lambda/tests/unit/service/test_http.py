"""
Pytest unit tests for http client
"""

import httpretty
import pytest
from app_handler.service.http import HttpService
import tests.unit.service.http_utils as utils

http = HttpService()

@httpretty.activate(allow_net_connect=False)
def test_http_ok_json():
    """
    Test HTTP OK 200 with JSON is parsed correctly
    """
    utils.httpretty_register_http_success_json_response()
    response = http.post_json('https://example.com/json', {'test': 'a'})
    assert response['status'] == 200
    assert response['json']['title'] == 'test'
    assert response['json']['items'] == [1, 2]


@httpretty.activate(allow_net_connect=False)
def test_http_ok_urlencoded():
    """
    Test HTTP OK 200 with URL encoding is parsed correctly
    """
    utils.httpretty_register_http_success_json_response()
    response = http.post_urlencoded('https://example.com/json', {'test': 'a'})
    assert response['status'] == 200
    assert response['json']['title'] == 'test'
    assert response['json']['items'] == [1, 2]


@httpretty.activate(allow_net_connect=False)
def test_http_not_json():
    """
    Test HTTP OK 200 with JSON is parsed correctly
    """
    utils.httpretty_register_http_success_json_response()
    with pytest.raises(ValueError):
        http.post_json('https://example.com/json', {'set'})
