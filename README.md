# AWS Lambda function python template
Opinionated starter repository for creating python Lambda functions that use AWS services.

## Assumptions
This starter repository makes the following assumptions.

### Dependency management
- Poetry is used to manage dependencies and run tasks

This project was initiated with:
```shell
poetry new example --src
```

### Development environment
- A shell-capable environment is available
- Docker is used as the local development environment

### Testing
- pytest is used to run tests with coverage via GitHub Actions

### Build
- GitHub Actions are used to test and produce build artifacts
- A zip bundle is created
- A wheel package is created

## Local development
### Docker
Developing inside a Docker container ensures a consistent experience and more closely matches the final build.

To develop inside a container, first build an image that sets up a limited-privilege user with the following.
Note that will run tests and produce builds.
The `dev` target uses the first stage of the multi-stage [Dockerfile](./Dockerfile).

```shell
docker build -t python-lambda/template/dev --target dev .
```

To then develop inside a container using this image, mount the entire project into a container (in addition to the local AWS config directory) with:

```shell
docker run -i -t --rm \
  -v $(pwd):/project \
  -v $HOME/.aws:/home/lambda/.aws:ro \
  python-lambda/template/dev
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

Start a local SAM API Gateway on arbitrary port 10112 with:
```shell
sam local start-api -p 10112
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
