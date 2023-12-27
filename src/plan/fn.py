import boto3
import json
from aws_xray_sdk.core import patch_all
from lib.util import build_response, get_body, get_param, log_event
from lib.domain.plan import Plan

# initialization
plan = Plan()
patch_all()

def handler(event, context):
    log_event(event)
    response = {}
    method = event.get("httpMethod", "GET")
    qsp = event.get("queryStringParameters")
    output = {}
    match method:
        case "GET":
            uid = get_param(qsp, "uid")
            if uid is not None:
                output = plan.get_plan(uid)
            else:
                output = plan.list_plans()
        case "POST":
            body = get_body(event)
            output = plan.create_plan(body.get("description"), body.get("is_private", False))
        case "PUT":
            uid = get_param(qsp, "uid")
            if uid is not None:
                body = get_body(event)
                output = plan.update_plan(uid, body.get("description"), body.get("is_private", False))
        case "DELETE":
            uid = get_param(qsp, "uid")
            if uid is not None:
                output = plan.delete_plan(uid)
    response = build_response(200, json.dumps(output))
    return response
