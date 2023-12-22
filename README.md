# Overview
This repository implements a reading scheduler and tracking application built using AWS serverless services.

## Pre-requisites
Copy `etc/environment.template` to `etc/environment.sh` and update accordingly.
* `PROFILE`: your AWS CLI profile with the appropriate credentials to deploy
* `REGION`: your AWS region
* `BUCKET`: your configuration bucket

For the infrastructure stack, update the following accordingly.
* `P_HOSTEDZONE_ID`: hosted zone id for your public domain
* `P_DOMAINNAME`: new subdomain name to configure in your public domain

For the API Gateway and Lambda stack, update the following accordingly.
* `P_STAGE`: stage name for API Gateway
* `P_FN_MEMORY`: amount of memory in MB for the Lambda function
* `P_FN_TIMEOUT`: timeout in seconds for the Lambda function

## Deployment
Deploy the infrastructure resource: `make infrastructure`

After completing the deployment, update the following outputs:
* `O_CERT_ARN`: output certificate arn

Deploy the API Gateway and Lambda resources: `make apigw`

After completing the deployment, update the following outputs:
* `O_FN`: output Lambda function name
* `O_API_ENDPOINT`: output API Gateway endpoint, e.g. https://<api_id>.execute-api.<region>.amazonaws.com/<stage>

## Testing
Test the function locally: `make sam.local.invoke`

Start a local API endpoint: `make sam.local.api`

To test the local API endpoint: `curl -s -XGET http://127.0.0.1:3000 | jq`

Test the deployed function: `make lambda.invoke.sync`

To test the API endpoint with the default FQDN: `curl -s -XGET ${O_API_ENDPOINT} | jq`

To test the API endpoint with the custom domain name: `curl -s -XGET https://${P_DOMAINNAME}/${P_API_BASEPATH} | jq`
