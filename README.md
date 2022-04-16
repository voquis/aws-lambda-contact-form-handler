# Contact form handler Python AWS Lambda function
Lambda function to receive input from a simple web form.
Optionally perform hCaptcha validation and send/store notifications to different services.

Supported frontend integrations:
- AWS HTTP API Gateway (v2)
- AWS API Gateway (v1)

Supported backend integrations:
- AWS Simple Email Service (SES)
- Discord
- DynamoDB

Application configuration is through any combination of:
- Environment variables
- AWS Systems Manager Parameter Store
- AWS Secrets Manager

## Environment variables
Key                                        | Description                                                                                                        | Default                           | Values          | Notes
-------------------------------------------|--------------------------------------------------------------------------------------------------------------------|-----------------------------------|-----------------|-------
LOG_LEVEL                                  | Logger level, set to `DEBUG` for the most detail, `CRITICAL` for only the highest severity                         | `INFO`                            | <ul><li>`DEBUG`</li><li>`INFO`</li><li>`WARNING`</li><li>`ERROR`</li><li>`CRITICAL`</li></ul> |
REQUIRED_FIELDS                            | Comma separated list of fields that must be in the request. Returns `400 Bad Request` if any fields are missing    |                                   |                 |
HCAPTCHA_ENABLE                            | Whether to enable hCaptcha protection                                                                              | `False`                           | <ul><li>`True`</li><li>`False`</li></ul> |
HCAPTCHA_SITEKEY                           | hCaptch Sitekey value                                                                                              | `null`                            |                 |
HCAPTCHA_SITEKEY_SOURCE                    | Where hCaptcha sitekey should be retrieved from                                                                    | `env`                             | <ul><li>`aws_ssm_parameter_store`</li><li>`aws_secrets_manager`</li><li>`env`</li></ul> |
HCAPTCHA_SITEKEY_PARAMETER_STORE_NAME      | Parameter name for hCaptcha Sitekey if using AWS SSM Parameter Store                                               | `/hcaptcha/sitekey`               |                 |
HCAPTCHA_SITEKEY_SECRETS_MANAGER_NAME      | Secrets name for hCaptcha Sitekey if using AWS Secrets Manager                                                     | `/hcaptcha/sitekey`               |                 |
HCAPTCHA_SECRET                            | hCaptch Secret value                                                                                               | `null`                            |                 |
HCAPTCHA_SECRET_SOURCE                     | Where hCaptcha sitekey should be retrieved from                                                                    | `env`                             | <ul><li>`aws_ssm_parameter_store`</li><li>`aws_secrets_manager`</li><li>`env`</li></ul> |
HCAPTCHA_SECRET_PARAMETER_STORE_NAME       | Parameter name for hCaptcha Secret if using AWS SSM Parameter Store                                                | `/hcaptcha/secret`                |                 |
HCAPTCHA_SECRET_SECRETS_MANAGER_NAME       | Secret name for hCaptcha Secret if using AWS Secrets Manager                                                       | `/hcaptcha/secret`                |                 |
HCAPTCHA_RESPONSE_FIELD                    | Key to find in payload containing the user captcha response                                                        | `captcha-response`                |                 |
HCAPTCHA_VERIFY_URL                        | Base URL for performing hCaptcha validation                                                                        | `https://hcaptcha.com/siteverify` |                 |
DATABASE_ENABLE                            | Whether requests to the lambda should store required fields in a DynamoDB database table                           | `False`                           |                 |
DATABASE_TABLE                             | DynamoDB database table name to store required fields                                                              |                                   |                 |
DATABASE_TABLE_SOURCE                      | DynamoDB database table name to store required fields                                                              |                                   |                 |
EMAIL_ENABLE                               | Whether sending emails via AWS Simple Email Service (SES) is enabled                                               | `False`                           | <ul><li>`True`</li><li>`False`</li></ul> |
EMAIL_RECIPIENTS                           | Comma separated list of destination email addresses                                                                |                                   |                 |
EMAIL_SENDER                               | Sender email address                                                                                               |                                   |                 |
EMAIL_TEXT_TEMPLATE                        | Email text [Template string](https://docs.python.org/3/library/string.html#template-strings) with substitution     |                                   |                 |
EMAIL_SUBJECT_TEMPLATE                     | Email subject [Template string](https://docs.python.org/3/library/string.html#template-strings) with substitution  |                                   |                 |
DISCORD_ENABLE                             | Whether notifications should be sent to a Discord webhook                                                          | `False`                           |                 |
DISCORD_WEBHOOK_ID                         | Discord webhook ID                                                                                                 |                                   |                 |
DISCORD_WEBHOOK_ID_SOURCE                  | Where Discord webhook ID should be retrieved from                                                                  | `env`                             | <ul><li>`aws_ssm_parameter_store`</li><li>`aws_secrets_manager`</li><li>`env`</li></ul> |
DISCORD_WEBHOOK_ID_PARAMETER_STORE_NAME    | Parameter name for Discord webhook ID if using AWS SSM Parameter Store                                             | `/discord/webhook/id`             |                 |
DISCORD_WEBHOOK_ID_SECRETS_MANAGER_NAME    | Secret name for hCaptcha Secret if using AWS Secrets Manager                                                       | `/discord/webhook/token`          |                 |
DISCORD_WEBHOOK_TOKEN                      | Discord webhook token                                                                                              |                                   |                 |
DISCORD_WEBHOOK_TOKEN_SOURCE               | Where Discord webhook ID should be retrieved from                                                                  | `env`                             | <ul><li>`aws_ssm_parameter_store`</li><li>`aws_secrets_manager`</li><li>`env`</li></ul> |
DISCORD_WEBHOOK_TOKEN_PARAMETER_STORE_NAME | Parameter name for Discord webhook ID if using AWS SSM Parameter Store                                             | `/discord/webhook/id`             |                 |
DISCORD_WEBHOOK_TOKEN_SECRETS_MANAGER_NAME | Secret name for hCaptcha Secret if using AWS Secrets Manager                                                       | `/discord/webhook/token`          |                 |
DISCORD_USERNAME                           | Username to display in message instead of the default                                                              | `Contact`                         |                 |
DISCORD_JSON_TEMPLATE                      | JSON [Template string](https://docs.python.org/3/library/string.html#template-strings) with substitution           | `New message received`            | `{"username": "Contact Handler", "message": "Message received"}`                | E.g. `Message from ${name}` will use the `name` field in the payload
## Local development
### Docker
Developing inside a Docker container ensures a consistent experience and more closely matches the final build.

To develop inside a container, first build an image that sets up a limited-privilege user with the following.
Note that will run tests and produce builds.
The `dev` target uses the first stage of the multi-stage [Dockerfile](./Dockerfile).

```shell
docker build -t python-lambda/contact-form-handler/dev --target dev .
```

To then develop inside a container using this image, mount the entire project into a container (in addition to the local AWS config directory) with:

```shell
docker run -i -t --rm \
  -v $(pwd):/project \
  -v $HOME/.aws:/home/lambda/.aws:ro \
  python-lambda/contact-form-handler/dev
```

### Run tests

Change to the lambda directory with:
```shell
cd lambda
```

Install dependencies (including development) and run tests with:
```
../scripts/validate.sh
```

## Build and run Lambda Docker image
AWS [provides a Docker image](https://gallery.ecr.aws/lambda/python) containing the python Lambda runtime.
Build a local image using this AWS image with the following.
Note this uses the same Dockerfile as above without stage targeting.

```
docker build -t python-lambda/template/lambda .
```

Then start the Lambda function locally on arbitrary port `10111` with:
```
docker run --rm \
  -p 10111:8080 \
  python-lambda/template/lambda
```

Make a HTTP Post request to the lambda with:
```shell
curl -d '{"key":"value"}' -X POST http://127.0.0.1:10111/2015-03-31/functions/function/invocations
```

## Run a Local API gateway with Serverless Application Model (SAM)
Locally, the AWS Serverless Application Model allows [running an AWS API Gateway locally](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-start-api.html).

Once installed and the `sam` command is available, optionally disable telemetry:
```shell
export SAM_CLI_TELEMETRY=0
```

Start a local SAM API Gateway on arbitrary port 10112 with the following.
By specifying a `--profile`, AWS session credentials e.g. AWS SSO can be automatically passed to the lambda.

```shell
sam local start-api -p 10112 --profile=my-profile
```


Send sample requests to API Gateway (v1) with:
```shell
curl http://127.0.0.1:10112/api -X POST --data '{"key": "test value"}' -H 'content-type:application/json'
curl http://127.0.0.1:10112/api -X POST --data-binary @./lambda/tests/unit/fixtures/request.json -H 'content-type:application/json'
curl http://127.0.0.1:10112/api --data-urlencode "key=test value"
```

Send sample requests to HTTP API Gateway (v2) with:
```shell
curl http://127.0.0.1:10112/httpapiv2 -X POST --data '{"key": "test value"}' -H 'content-type:application/json'
curl http://127.0.0.1:10112/httpapiv2 --data-urlencode "key=test value"
```
