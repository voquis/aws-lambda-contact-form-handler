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
The table below lists the available configuration variables.
For example usage and sample values, see the `Environment` section of [template.yaml](./template.yaml).
For all keys except `LOG_LEVEL`, appending `_SOURCE` controls where the value for that key is fetched from.
The available configuration sources are:
- `env` - Environment variables (default)
- `aws_ssm_parameter_store` - AWS Systems Manager (SSM) Parameter Store
- `aws_secrets_manager` - AWS Secrets Manager

When specifying a non-env source, an additional property must be provided specific to that configuration source, appended to the configuration key name.
These are:
- `_PARAMETER_STORE_NAME` - for AWS SSM Parameter Store
- `_SECRETS_MANAGER_NAME` - for AWS Secrets Manager

For example, to fetch the `HCAPTCHA_SITEKEY` from AWS SSM Parameter Store, specify the following:
- `HCAPTCHA_SITEKEY_SOURCE` with `aws_ssm_parameter_store`
- `HCAPTCHA_SITEKEY_PARAMETER_STORE_NAME` with for example `/my/hcaptcha/sitekey`

To instead fetch this value from AWS Secrets Manager, set:
- `HCAPTCHA_SITEKEY_SOURCE` with `aws_secrets_manager`
- `HCAPTCHA_SITEKEY_SECRETS_MANAGER_NAME` with for example `/my/hcaptcha/sitekey`


Key                             | Description                                                   | Values / Default
--------------------------------|---------------------------------------------------------------|-----------------
LOG_LEVEL                       | Logger level, `DEBUG` (most) to `CRITICAL` (least) detail     | <ul><li>`DEBUG`</li><li>`INFO` (default)</li><li>`WARNING`</li><li>`ERROR`</li><li>`CRITICAL`</li></ul>
REQUIRED_FIELDS                 | Comma separated list of fields that must be in the request    |
HCAPTCHA_ENABLE                 | Whether to enable hCaptcha protection                         | <ul><li>`True`</li><li>`False` (default)</li></ul>
HCAPTCHA_SITEKEY                | hCaptch Sitekey value                                         |
HCAPTCHA_SECRET                 | hCaptch Secret value                                          |
HCAPTCHA_RESPONSE_FIELD         | Key to find in payload containing user captcha response       | `captcha-response` (default)
HCAPTCHA_VERIFY_URL             | Base URL for performing hCaptcha validation                   | `https://hcaptcha.com/siteverify` (default)
DYNAMODB_ENABLE                 | Enable logging required fields to DynamoDB                    | <ul><li>`True`</li><li>`False` (default)</li></ul>
DYNAMODB_TABLE                  | DynamoDB table name to store required fields                  |
DYNAMODB_ENDPOINT_URL           | DynamoDB endpoint url                                         |
EMAIL_ENABLE                    | Enable sending emails via AWS Simple Email Service (SES)      | <ul><li>`True`</li><li>`False` (default)</li></ul>
EMAIL_RECIPIENTS                | Comma separated list of destination email addresses           |
EMAIL_SENDER                    | Sender email address                                          |
EMAIL_TEXT_TEMPLATE             | Email text Template string with substitution                  |
EMAIL_SUBJECT_TEMPLATE          | Email subject Template string with substitution               |
DISCORD_ENABLE                  | Whether notifications should be sent to a Discord webhook     | <ul><li>`True`</li><li>`False` (default)</li></ul>
DISCORD_WEBHOOK_ID              | Discord webhook ID                                            |
DISCORD_WEBHOOK_TOKEN           | Discord webhook token                                         |
DISCORD_JSON_TEMPLATE           | JSON Template string with substitution                        |

## Templating

The following variables provide Python [String Templates](https://docs.python.org/3/library/string.html#template-strings).
Placeholders should match fields named defined in `REQUIRED_FIELDS` and should be of the form `${field_name}`.
For example, if `REQUIRED_FIELDS=name,email`, the template string could be `New email from ${name} (${email})` and the result would be `New email from First Last (first.last@example.com)`
- `DISCORD_JSON_TEMPLATE` - See the [Discord webhook JSON] guide](https://birdie0.github.io/discord-webhooks-guide/discord_webhook.html) for a full example.
- `EMAIL_SUBJECT_TEMPLATE` - Plain text string to use in Email subject
- `EMAIL_TEXT_TEMPLATE` - Plain text string to use in Email body

## Local development with Docker
Developing inside a Docker container ensures a consistent experience and more closely matches the final build.

### Network
Create a docker network.
This is to allow the lambda and later the local API gateway to resolve a local dynamodb instance.
```shell
docker network create contact-form-handler
```

### Dynamodb Local
To start DynamoDB Local:
```shell
docker run --rm \
  --network contact-form-handler \
  --name dynamodb \
  -p 10113:8000 \
  amazon/dynamodb-local
```

Create a local table with the expected `id` and `timestamp` indexes.
> Ensure you have exported a default AWS region, as this must be the same between the DynamoDB container and the running Python code. Although the region doesn't matter, consistency is important.
```shell
export AWS_DEFAULT_REGION=us-east-1
```
> Use the following as-is, real credentials and a region are not required for DynamoDB Local.
```shell
AWS_ACCESS_KEY_ID=abc \
AWS_SECRET_ACCESS_KEY=abc \
aws dynamodb create-table \
  --endpoint-url http://127.0.0.1:10113 \
  --table-name website-contact \
  --attribute-definitions AttributeName=id,AttributeType=S AttributeName=timestamp,AttributeType=N \
  --key-schema AttributeName=id,KeyType=HASH AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
```

To list local tables, run the following.
> Use the following as-is, real credentials and a region are not required for DynamoDB Local.
```shell
AWS_ACCESS_KEY_ID=abc \
AWS_SECRET_ACCESS_KEY=abc \
aws dynamodb \
  list-tables \
  --endpoint-url http://127.0.0.1:10113 \
  --region us-east-2
```

### Local development container

To develop inside a container, first build an image that sets up a limited-privilege user with the following.
Note that will run tests and produce builds.
The `dev` target uses the first stage of the multi-stage [Dockerfile](./Dockerfile).

```shell
docker build -t python-lambda/contact-form-handler/dev --target dev .
```

To then develop inside a container using this image, mount the entire project into a container (in addition to the local AWS config directory) with:

```shell
docker run -i -t --rm \
  --network contact-form-handler \
  -v $(pwd):/project \
  -v $HOME/.aws:/home/lambda/.aws:ro \
  python-lambda/contact-form-handler/dev
```


### Local API gateway with Serverless Application Model (SAM)
The AWS Serverless Application Model allows [running an API Gateway locally](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-using-start-api.html).

Once installed and the `sam` command is available, optionally disable telemetry:
```shell
export SAM_CLI_TELEMETRY=0
```

Then start a local SAM API Gateway on arbitrary port `10112` with the following, connected to the existing Docker network.
By specifying a `--profile`, AWS session credentials e.g. AWS SSO can be automatically passed to the lambda.

```shell
sam local start-api \
  --docker-network contact-form-handler \
  --warm-containers EAGER \
  -p 10112 \
  --profile=my-profile
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
  --network contact-form-handler \
  -p 10111:8080 \
  python-lambda/template/lambda
```

Make a HTTP Post request to the lambda with:
```shell
curl -d '{"key":"value"}' -X POST http://127.0.0.1:10111/2015-03-31/functions/function/invocations
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
