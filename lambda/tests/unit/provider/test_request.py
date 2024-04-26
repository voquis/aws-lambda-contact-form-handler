"""
Payload parsing unit tests
"""

import json
import pathlib
from app_handler.provider.request import RequestProvider

json_data = {'key': 'test value'}

def get_json_fixture_file(filename):
    """
    Return JSON fixture from local file
    """
    path = pathlib.Path(__file__).parent.parent / f"fixtures/{filename}"
    content = pathlib.Path(path).read_text('UTF-8')
    return json.loads(content)

# Direct invocation test

def test_payload_parse_invoke_direct():
    """
    Test directly invoked lambda function returns original payload
    """

    assert RequestProvider(json_data).content == json_data

# Poorly formatted payload direct invocation tests

def test_payload_parse_no_headers():
    """
    Test invoked lambda without appropriate headers
    """
    data = {'body': 'no headers'}
    assert RequestProvider(data).content == 'no headers'


def test_payload_parse_bad_headers():
    """
    Test invoked lambda with bad headers
    """
    data = {'body': 'bad headers', 'headers': {}}
    assert RequestProvider(data).content == 'bad headers'


def test_payload_parse_bad_header_type():
    """
    Test invoked lambda with bad headers
    """
    data = {'body': 'bad header type', 'headers': {'Content-Type': {}}}
    assert RequestProvider(data).content == 'bad header type'

def test_payload_parse_unknown_header_type():
    """
    Test invoked lambda with unknown content type header
    """
    data = {'body': 'unknown header type', 'headers': {'Content-Type': 'abc'}}
    assert RequestProvider(data).content == 'unknown header type'

# JSON body tests without base64 encoding

def test_payload_parse_api_gateway_no_base64_json():
    """
    Test invoked lambda non-base64 json payload from API Gateway (v1) is correctly parsed
    """

    event = get_json_fixture_file('api_gateway_request_json_no_base64.json')
    assert RequestProvider(event).content == json_data


def test_payload_parse_httpapiv2_gateway_no_base64_json():
    """
    Test invoked lambda non-base64 payload from API Gateway (v2) is correctly parsed
    """

    event = get_json_fixture_file('httpapiv2_gateway_request_json_no_base64.json')
    assert RequestProvider(event).content == json_data

# JSON body tests with base64 encoding

def test_payload_parse_api_gateway_base64_json():
    """
    Test invoked lambda base64 json payload from API Gateway (v1) is correctly parsed
    """

    event = get_json_fixture_file('api_gateway_request_json_base64.json')
    assert RequestProvider(event).content == json_data


def test_payload_parse_httpapiv2_gateway_base64_json():
    """
    Test invoked lambda base64 payload from API Gateway (v2) is correctly parsed
    """

    event = get_json_fixture_file('httpapiv2_gateway_request_json_base64.json')
    assert RequestProvider(event).content == json_data

# URL encoded body tests without base64 encoding

def test_payload_parse_api_gateway_no_base64_urlencoded():
    """
    Test invoked lambda non-base64 urlencoded payload from API Gateway (v1) is correctly parsed.
    Note that an array of values are returned
    """

    event = get_json_fixture_file('api_gateway_request_urlencoded_no_base64.json')
    assert RequestProvider(event).content == json_data


def test_payload_parse_httpapiv2_gateway_no_base64_urlencoded():
    """
    Test invoked lambda non-base64 payload from API Gateway (v2) is correctly parsed
    Note that an array of values are returned
    """

    event = get_json_fixture_file('httpapiv2_gateway_request_urlencoded_no_base64.json')
    assert RequestProvider(event).content == json_data

# URL encoded body tests with base64 encoding

def test_payload_parse_api_gateway_base64_urlencoded():
    """
    Test invoked lambda base64 urlencoded payload from API Gateway (v1) is correctly parsed.
    Note that an array of values are returned
    """

    event = get_json_fixture_file('api_gateway_request_urlencoded_base64.json')
    assert RequestProvider(event).content == json_data


def test_payload_parse_httpapiv2_gateway_base64_urlencoded():
    """
    Test invoked lambda base64 payload from API Gateway (v2) is correctly parsed
    Note that an array of values are returned
    """

    event = get_json_fixture_file('httpapiv2_gateway_request_urlencoded_base64.json')
    assert RequestProvider(event).content == json_data

def test_get_remote_ip():
    """
    Ensure remote IPs are returned for all gateway types
    """

    eventv1 = get_json_fixture_file('api_gateway_request_urlencoded_base64.json')
    eventv2 = get_json_fixture_file('httpapiv2_gateway_request_urlencoded_base64.json')
    assert RequestProvider(eventv1).get_remote_ip() == '127.0.0.1'
    assert RequestProvider(eventv2).get_remote_ip() == '127.0.0.1'

# SNS topic

def test_payload_parse_sns_message():
    """
    Ensure that an SNS message is correctly parsed
    """

    sns_request = get_json_fixture_file('sns_message_v1.json')
    assert RequestProvider(sns_request).content['Message'] == 'Hello from SNS!'
    assert RequestProvider(sns_request).content['Subject'] == 'TestInvoke'
