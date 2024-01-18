# Overview
This repository implements a reading scheduler and tracking application built using AWS serverless services.

## Pre-requisites
Copy `etc/environment.template` to `etc/environment.sh` and update accordingly.
* `PROFILE`: your AWS CLI profile with the appropriate credentials to deploy
* `REGION`: your AWS region
* `BUCKET`: your configuration bucket

For the infrastructure stack, update the following accordingly.
* `P_HOSTEDZONE_ID`: hosted zone id for your public domain
* `P_DOMAINNAME_ROOT`: root domain name
* `P_DOMAINNAME_EMAIL`: subdomain for email
* `P_DOMAINNAME_API`: subdomain for api
* `P_EMAIL_SUBJECT`: custom subject line for daily reading emails

For the API Gateway and Lambda stack, update the following accordingly.
* `P_API_BASEPATH`: base path for API Gateway
* `P_API_STAGE`: stage name for API Gateway
* `P_FN_MEMORY`: amount of memory in MB for the Lambda function
* `P_FN_TIMEOUT`: timeout in seconds for the Lambda function

For the Scheduler stack, update the following accordingly.
* `P_ENDPOINT`: base endpoint url, e.g. https://api.example.com/reading
* `P_PLAN_ID`: plan uuid for the scheduler to query
* `P_API_KEY`: pending feature implementation for api keys

## Deployment
Deploy the infrastructure resource: `make infrastructure`

After completing the deployment, update the following outputs:
* `O_CERT_ARN`: output certificate arn
* `O_EMAIL_TEMPLATE`: output email template name

Deploy the API Gateway and Lambda resources: `make apigw`

After completing the deployment, update the following outputs:
* `O_FN`: output Lambda function name
* `O_API_ENDPOINT`: output API Gateway endpoint, e.g. https://<api_id>.execute-api.<region>.amazonaws.com/<stage>
* `O_CUSTOM_ENDPOINT`: output endpoint url, e.g. https://api.example.com/reading
* `O_TABLE_ARN`: output table arn

Deploy the Scheduler resources: `make scheduler`

After completing the deployment, update the following outputs:
* `O_SF_ARN`: output Step Function workflow arn

## Testing
Test the function locally: `make sam.local.invoke`

Start a local API endpoint: `make sam.local.api`

To test the local API endpoint: `curl -s -XGET http://127.0.0.1:3000 | jq`

Test the deployed function: `make lambda.invoke.sync`

To test the API endpoint with the default FQDN: `curl -s -XGET ${O_API_ENDPOINT} | jq`

To test the API endpoint with the custom domain name: `curl -s -XGET https://${P_DOMAINNAME}/${P_API_BASEPATH} | jq`

## Observability
With Lambda logging set to JSON, you can filter events, removing the platform events, with the following filter:
```
{($.type = "platform.initStart") || ($.type = "platform.start") || ($.type = "platform.report") || ($.type = "platform.extension")}
{($.level = "INFO" || $.level = "WARN" || $.level = "ERROR")}
{($.httpMethod = "GET") || ($.httpMethod = "POST") || ($.httpMethod = "PUT") || ($.httpMethod = "DELETE")}
```

## Request Validation
Note when doing request validation, the API client needs to ensure that the `content-type: application/json` header is also passed along with the request. Otherwise, request validation will not work properly.
