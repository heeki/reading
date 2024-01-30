import boto3
import json
import logging
import os
from aws_xray_sdk.core import patch_all
from enum import Enum
from lib.util import build_response, get_body, get_param, log_event
from lib.domain.plan import Plan

# initialization
boto3.set_stream_logger(name="aws_xray_sdk.core.context", level=logging.ERROR)
boto3.set_stream_logger(name="aws_xray_sdk.core.lambda_launcher", level=logging.ERROR)
boto3.set_stream_logger(name="aws_xray_sdk.core.patcher", level=logging.ERROR)
boto3.set_stream_logger(name="botocore.credentials", level=logging.ERROR)
patch_all()
plan = Plan()
redirect_url = os.environ.get("REDIRECT_URL")

# action
class Action(Enum):
    LIST_PLANS = 1
    GET_PLAN = 2

def get_action(qsp, uid):
    response = Action.LIST_PLANS
    if qsp is None:
        response = Action.LIST_PLANS
    elif len(qsp) == 1 and uid is not None:
        response = Action.GET_PLAN
    return response

def handler(event, context):
    log_event(event)
    method = event.get("httpMethod", "GET")
    qsp = event.get("queryStringParameters")
    response_code = 200
    response_headers = {}
    output = {}
    match method:
        case "GET":
            uid = get_param(qsp, "uid")
            action = get_action(qsp, uid)
            match action:
                case Action.GET_PLAN:
                    output = plan.get_plan(uid)
                case _:
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
    response = build_response(response_code, json.dumps(output), response_headers)
    return response
