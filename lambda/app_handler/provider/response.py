"""
Response provider
"""

import logging

class ResponseProvider:
    """
    Response provider class
    """

    def __init__(self, event) -> None:
        """
        Initialise response based on request format
        """

        self.is_v1 = False
        self.is_v2 = False

        # Use the request object to determine API type (if any)
        if isinstance(event, dict) and 'version' in event:
            version = event['version']
            logging.debug("API version: %s", version)

            if version.startswith('1.'):
                self.is_v1 = True
            elif version.startswith('2.'):
                self.is_v2 = True
            else:
                logging.warning("Unknown API version %s", version)
        else:
            logging.warning("Unknown API version %s")

    def message(self, message, status_code=200):
        """
        Prepare json message output
        """
        return self.build(
            body={'message': message},
            status_code=status_code,
        )


    def build(self, body, status_code=200, **kwargs):
        """
        Prepare output for API integration
        https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
        """

        # If request came from a non-API integration, append status code to body
        if not self.is_v1 and not self.is_v2:
            body['statusCode'] = status_code
            return body

        # Prepare a v1 or v2 API integration response
        output = {
            "isBase64Encoded": kwargs.get('is_base64_encoded', False),
            "statusCode": status_code,
            "headers":  kwargs.get('headers', {'content-type':'application/json'}),
            "multiValueHeaders": kwargs.get('multi_value_headers', {}),
            "body": body,
        }

        return output
