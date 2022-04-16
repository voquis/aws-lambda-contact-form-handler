"""
Runner unit tests
"""
import os

from app_handler.runner.app import AppRunner

def test_empty_runner(monkeypatch):
    """
    Test runner
    """

    monkeypatch.setenv('REQUIRED_FIELDS', '')
    runner = AppRunner()
    runner.configure()

    assert not runner.request_provider
    assert not runner.required_fields

def test_required_fields(monkeypatch):
    """
    Test required fields are correctly extracted
    """
    monkeypatch.setenv('REQUIRED_FIELDS', 'a, ,b,c,,')
    runner = AppRunner()
    runner.configure()

    assert runner.required_fields == {'a':'', 'b':'', 'c':''}


def test_invalid_json(monkeypatch):
    """
    Test invalid json event is handled correctly
    """
    monkeypatch.setenv('REQUIRED_FIELDS', 'a, ,b,c,,')
    runner = AppRunner()
    runner.configure()
    payload = {'version'}
    response = runner.run(payload)
    assert not response
    assert runner.error_response['statusCode'] == 400

def test_invalid_json_body(monkeypatch):
    """
    Test invalid json event is handled correctly
    """
    monkeypatch.setenv('REQUIRED_FIELDS', 'a, ,b,c,,')
    runner = AppRunner()
    runner.configure()
    payload = {'version':'2.0', 'headers': {'content-type': 'application/json'}, 'body': '"{'}
    response = runner.run(payload)
    assert not response
    assert runner.error_response['statusCode'] == 400


def test_missing_fields(monkeypatch):
    """
    Test invalid json event is handled correctly
    """
    monkeypatch.setenv('REQUIRED_FIELDS', 'a, ,b,c,,')
    runner = AppRunner()
    runner.configure()
    payload = {'version': '1.0','body': {'notNa{me':'a', 'notEmail':'b'}}
    response = runner.run(payload)
    assert not response
    assert runner.error_response['statusCode'] == 400


def test_empty_body(monkeypatch):
    """
    Test empty event is handled correctly
    """
    monkeypatch.setenv('REQUIRED_FIELDS', 'a')
    runner = AppRunner()
    runner.configure()
    payload = {'version': '1.0','body': {'a': ''}}
    response = runner.run(payload)
    assert not response
    assert runner.error_response['statusCode'] == 400
