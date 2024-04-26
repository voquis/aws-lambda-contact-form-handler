"""
AWS Lambda handler, can be invoked directly or integrated with an AWS API Gateway (v1 or v2)
https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
"""

import logging
from app_handler.provider.app import AppProvider

def handler(event, context):
    """
    Lambda Handler

    event: data for the lambda function to process
    https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html#python-handler-how

    context: info on invocation, function, and execution environment
    https://docs.aws.amazon.com/lambda/latest/dg/python-context.html
    """

    logging.debug(event)
    logging.debug(context)
    app_provider =  AppProvider(event)
    return app_provider.response
