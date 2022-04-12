"""
AWS Lambda handler, can be invoked directly or integrated with an AWS HTTP API Gateway (v2)
https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
"""

import logging
from example import payload

def handler(event, context):
    """
    Lambda Handler

    event: data for the lambda function to process
    https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html#python-handler-how

    context: info on invocation, function, and execution environment
    https://docs.aws.amazon.com/lambda/latest/dg/python-context.html
    """

    logging.debug(context)
    content = payload.get_content(event)
    return content
