#!/bin/bash

set -euo pipefail

if [[ $GITHUB_REF_TYPE = 'branch' ]]; then
  # Always copy to
  aws s3 cp lambda.zip "s3://voquis/aws/lambda_functions/contact-form-handler/${GITHUB_REF_NAME}.zip"
fi

if [[ $GITHUB_REF_TYPE = 'tag' ]]; then
  # Copy commit short SHA to tag
  aws s3 cp lambda.zip "s3://voquis/aws/lambda_functions/contact-form-handler/${GITHUB_REF_NAME}.zip"
  aws s3 cp lambda.zip "s3://voquis/aws/lambda_functions/contact-form-handler/latest.zip"
fi
