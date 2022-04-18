"""
Response provider unit tests
"""

from app_handler.provider.response import ResponseProvider

# Direct invocation test
def test_api_v1_json_message():
    """
    Test API Gateway v1 response
    """

    expected = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {
            "content-type": "application/json"
        },
        "multiValueHeaders": {},
        "body": '{"message": "OK"}'
    }

    assert ResponseProvider({'version':'1.0'}).message('OK') == expected
    assert ResponseProvider({'version':'1.1'}).message('OK') == expected
    assert ResponseProvider({'version':'2.0'}).message('OK') == expected
    assert ResponseProvider({'version':'2.1'}).message('OK') == expected
    # Handle unknown version
    assert ResponseProvider({'version':'3.0'}).message('OK') == {'message': 'OK', 'statusCode': 200}
