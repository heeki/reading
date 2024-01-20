include etc/environment.sh

# infrastructure for api gateway
infrastructure: infrastructure.package infrastructure.deploy
infrastructure.package:
	sam package --profile ${PROFILE} -t ${INFRASTRUCTURE_TEMPLATE} --output-template-file ${INFRASTRUCTURE_OUTPUT} --s3-bucket ${BUCKET} --s3-prefix ${INFRASTRUCTURE_STACK}
infrastructure.deploy:
	sam deploy --profile ${PROFILE} -t ${INFRASTRUCTURE_OUTPUT} --stack-name ${INFRASTRUCTURE_STACK} --parameter-overrides ${INFRASTRUCTURE_PARAMS} --capabilities CAPABILITY_NAMED_IAM

# libraries as layer
layer:
	mkdir -p tmp/libraries/python && rsync -av --delete src/lib --exclude __pycache__ tmp/libraries/python

# api gateway
apigw: layer apigw.package apigw.deploy
apigw.package:
	sam package -t ${APIGW_TEMPLATE} --output-template-file ${APIGW_OUTPUT} --s3-bucket ${BUCKET} --s3-prefix ${APIGW_STACK}
apigw.deploy:
	sam deploy -t ${APIGW_OUTPUT} --stack-name ${APIGW_STACK} --parameter-overrides ${APIGW_PARAMS} --capabilities CAPABILITY_NAMED_IAM
apigw.delete:
	sam delete --stack-name ${APIGW_STACK}

# local lambda testing
sam.local.api:
	sam local start-api -t ${APIGW_TEMPLATE} --parameter-overrides ${APIGW_PARAMS} --env-vars etc/envvars.json
sam.local.api.build:
	sam build --profile ${PROFILE} --template ${APIGW_TEMPLATE} --parameter-overrides ${APIGW_PARAMS} --build-dir build --manifest requirements.txt --use-container
	sam local start-api -t build/template.yaml --parameter-overrides ${APIGW_PARAMS} --env-vars etc/envvars.json
sam.local.invoke:
	sam local invoke -t ${APIGW_TEMPLATE} --parameter-overrides ${APIGW_PARAMS} --env-vars etc/envvars.json -e etc/event.json ${P_FN_LOCAL} | jq -r '.body' | jq

# testing deployed resources
lambda.invoke.sync:
	aws --profile ${PROFILE} lambda invoke --function-name ${O_FN} --invocation-type RequestResponse --payload file://etc/event.json --cli-binary-format raw-in-base64-out --log-type Tail tmp/fn.json | jq "." > tmp/response.json
	cat tmp/response.json | jq -r ".LogResult" | base64 --decode
	cat tmp/fn.json | jq
lambda.invoke.async:
	aws --profile ${PROFILE} lambda invoke --function-name ${O_FN} --invocation-type Event --payload file://etc/event.json --cli-binary-format raw-in-base64-out --log-type Tail tmp/fn.json | jq "."

# local unit tests
validation:
	PYTHONPATH=src python3 test/validation.py

# scheduler
scheduler: scheduler.package scheduler.deploy
scheduler.package:
	sam package -t ${SCHEDULER_TEMPLATE} --output-template-file ${SCHEDULER_OUTPUT} --s3-bucket ${BUCKET} --s3-prefix ${SCHEDULER_STACK}
scheduler.deploy:
	sam deploy -t ${SCHEDULER_OUTPUT} --stack-name ${SCHEDULER_STACK} --parameter-overrides ${SCHEDULER_PARAMS} --capabilities CAPABILITY_NAMED_IAM
scheduler.delete:
	sam delete --stack-name ${SCHEDULER_STACK}

# testing deployed resources
sf.invoke:
	aws --profile ${PROFILE} stepfunctions start-execution --state-machine-arn ${O_SF_ARN} --input file://etc/scheduler.json | jq
sf.list-executions:
	aws --profile ${PROFILE} stepfunctions list-executions --state-machine-arn ${O_SF_ARN} | jq

# testing endpoints
test: test.group test.group_stats test.user test.user_by_group test.user_by_plan test.user_subscribe test.user_stats test.plan test.reading test.reading_by_date test.reading_by_user test.reading_by_group
test.valid: test.group test.user test.plan test.reading
test.invalid: test.group_invalid test.user_invalid test.plan_invalid test.reading_invalid
test.by: test.user_by_group test.user_by_plan test.reading_by_date test.reading_by_user test.reading_by_group

# testing groups
test.group:
	$(eval UID=$(shell curl -s -XPOST -H "content-type: application/json" -d @etc/group_post.json ${O_CUSTOM_ENDPOINT}/group | jq -r .uid))
	curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/group | jq '.[]' -c
	curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/group?uid=${UID} | jq
	curl -s -XPUT -H "content-type: application/json" -d @etc/group_put.json ${O_CUSTOM_ENDPOINT}/group?uid=${UID} | jq
	curl -s -XDELETE -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/group?uid=${UID} | jq
	curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/group | jq '.[]' -c
test.group_invalid:
	curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/group?uid=invalid | jq
	curl -s -XPOST -H "content-type: application/json" -d @etc/group_invalid.json ${O_CUSTOM_ENDPOINT}/group | jq
	curl -s -XPUT -H "content-type: application/json" -d @etc/group_put.json ${O_CUSTOM_ENDPOINT}/group?uid=invalid | jq
	curl -s -XDELETE -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/group?uid=invalid | jq
test.group_stats:
	$(eval GROUP_IDS=$(shell curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/group | jq -r '.[].uid'))
	for uid in ${GROUP_IDS}; do echo $$uid; curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/group?stats=$$uid | jq -c; done

# testing user
test.user:
	$(eval UID=$(shell curl -s -XPOST -H "content-type: application/json" -d @etc/user_post.json ${O_CUSTOM_ENDPOINT}/user | jq -r .uid))
	curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/user | jq '.[]' -c
	curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/user?uid=${UID} | jq
	curl -s -XPUT -H "content-type: application/json" -d @etc/user_put.json ${O_CUSTOM_ENDPOINT}/user?uid=${UID} | jq
	curl -s -XDELETE -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/user?uid=${UID} | jq
	curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/user | jq '.[]' -c
test.user_invalid:
	curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/user?uid=invalid | jq
	curl -s -XPOST -H "content-type: application/json" -d @etc/user_invalid.json ${O_CUSTOM_ENDPOINT}/user | jq
	curl -s -XPUT -H "content-type: application/json" -d @etc/user_put.json ${O_CUSTOM_ENDPOINT}/user?uid=invalid | jq
	curl -s -XDELETE -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/user?uid=invalid | jq
test.user_by_group:
	$(eval GROUP_IDS=$(shell curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/group | jq -r '.[].uid'))
	for uid in ${GROUP_IDS}; do echo $$uid; curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/user?group_id=$$uid | jq -c 'map(del(.group_ids, .plan_ids)) | .[]'; done
	for uid in ${GROUP_IDS}; do echo $$uid; curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/user?group_id=$$uid\&is_subscribed=true | jq -c 'map(del(.group_ids, .plan_ids)) | .[]'; done
test.user_by_plan:
	$(eval PLAN_IDS=$(shell curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/plan | jq -r '.[].uid'))
	for uid in ${PLAN_IDS}; do echo $$uid; curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/user?plan_id=$$uid | jq -c 'map(del(.group_ids, .plan_ids)) | .[]'; done
	for uid in ${PLAN_IDS}; do echo $$uid; curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/user?plan_id=$$uid\&is_subscribed=true | jq -c 'map(del(.group_ids, .plan_ids)) | .[]'; done
	for uid in ${PLAN_IDS}; do echo $$uid; curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/user?plan_id=$$uid\&is_subscribed=false | jq -c 'map(del(.group_ids, .plan_ids)) | .[]'; done
test.user_subscribe:
	$(eval UID=$(shell curl -s -XPOST -H "content-type: application/json" -d @etc/user_post.json ${O_CUSTOM_ENDPOINT}/user | jq -r .uid))
	curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/user?uid=${UID} | jq -c 'del(.group_ids, .plan_ids)'
	curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/user?unsubscribe=${UID} | jq -c 'del(.group_ids, .plan_ids)'
	curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/user?subscribe=${UID} | jq -c 'del(.group_ids, .plan_ids)'
	curl -s -XDELETE -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/user?uid=${UID} | jq -c
test.user_stats:
	$(eval USER_IDS=$(shell curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/user | jq -r '.[].uid'))
	for uid in ${USER_IDS}; do echo $$uid; curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/user?stats=$$uid | jq -c; done

# testing plan
test.plan:
	$(eval UID=$(shell curl -s -XPOST -H "content-type: application/json" -d @etc/plan_post.json ${O_CUSTOM_ENDPOINT}/plan | jq -r .uid))
	curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/plan | jq '.[]' -c
	curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/plan?uid=${UID} | jq
	curl -s -XPUT -H "content-type: application/json" -d @etc/plan_put.json ${O_CUSTOM_ENDPOINT}/plan?uid=${UID} | jq
	curl -s -XDELETE -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/plan?uid=${UID} | jq
	curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/plan | jq '.[]' -c
test.plan_invalid:
	curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/plan?uid=invalid | jq
	curl -s -XPOST -H "content-type: application/json" -d @etc/plan_invalid.json ${O_CUSTOM_ENDPOINT}/plan | jq
	curl -s -XPUT -H "content-type: application/json" -d @etc/plan_put.json ${O_CUSTOM_ENDPOINT}/plan?uid=invalid | jq
	curl -s -XDELETE -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/plan?uid=invalid | jq

# testing reading
test.reading:
	$(eval UID=$(shell curl -s -XPOST -H "content-type: application/json" -d @etc/reading_post.json ${O_CUSTOM_ENDPOINT}/reading | jq -r .uid))
	curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/reading | jq '.[]' -c
	curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/reading?uid=${UID} | jq
	curl -s -XPUT -H "content-type: application/json" -d @etc/reading_put.json ${O_CUSTOM_ENDPOINT}/reading?uid=${UID} | jq
	curl -s -XDELETE -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/reading?uid=${UID} | jq
	curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/reading | jq '.[]' -c
test.reading_invalid:
	curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/reading?uid=invalid | jq
	curl -s -XPOST -H "content-type: application/json" -d @etc/reading_invalid.json ${O_CUSTOM_ENDPOINT}/reading | jq
	curl -s -XPUT -H "content-type: application/json" -d @etc/reading_put.json ${O_CUSTOM_ENDPOINT}/reading?uid=invalid | jq
	curl -s -XDELETE -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/reading?uid=invalid | jq
test.reading_by_date:
	curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/reading?date=2024-01-19 | jq
test.reading_by_user:
	$(eval USER_IDS=$(shell curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/user | jq -r '.[].uid'))
	for uid in ${USER_IDS}; do echo $$uid; curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/reading?user_id=$$uid | jq -c '.[]'; done
test.reading_by_group:
	$(eval GROUP_IDS=$(shell curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/group | jq -r '.[].uid'))
	for uid in ${GROUP_IDS}; do echo $$uid; curl -s -XGET -H "content-type: application/json" ${O_CUSTOM_ENDPOINT}/reading?group_id=$$uid | jq -c '.[]'; done

# cdk alternate
cdk.synth:
	cd iac/cdk && cdk synth ${CDK_PARAMS}
cdk.deploy:
	cd iac/cdk && cdk deploy --context stackName=${CDK_STACK} ${CDK_PARAMS}
cdk.destroy:
	cd iac/cdk && cdk destroy --context stackName=${CDK_STACK} ${CDK_PARAMS}
