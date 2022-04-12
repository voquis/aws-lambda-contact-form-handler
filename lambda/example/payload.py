"""
Lambda payload handling
"""
import base64
import json
import urllib

def get_content(payload):
    """
    Parse incoming payload and retrieve content.
    Handles the following cases:
        - Invocation as a Python function
        - Invocation of Lambda function
        - Invocation behind an AWS HTTP v2 API Gateway
    """

    if 'body' not in payload:
        return payload

    content = payload['body']

    if 'isBase64Encoded' in payload and payload['isBase64Encoded'] is True:
        content = str(base64.b64decode(payload['body']), "utf-8")

    if 'headers' not in payload:
        return content

    headers = payload['headers']

    if 'Content-Type' not in headers:
        return content

    content_type = headers['Content-Type']

    if not isinstance(content_type, str):
        return content

    content_type = content_type.lower()

    if content_type == 'application/x-www-form-urlencoded':
        html_decoded = urllib.parse.unquote(content)
        content = urllib.parse.parse_qs(html_decoded)

    if  content_type == 'application/json':
        content = json.loads(content)

    return content
