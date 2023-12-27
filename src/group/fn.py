import boto3
import json
from aws_xray_sdk.core import patch_all
from lib.util import build_response, get_body, get_param, log_event
from lib.domain.group import Group

# initialization
group = Group()
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
                output = group.get_group(uid)
            else:
                output = group.list_groups()
        case "POST":
            body = get_body(event)
            output = group.create_group(body.get("description"), body.get("is_private", False))
        case "PUT":
            uid = get_param(qsp, "uid")
            if uid is not None:
                body = get_body(event)
                output = group.update_group(uid, body.get("description"), body.get("is_private", False))
        case "DELETE":
            uid = get_param(qsp, "uid")
            if uid is not None:
                output = group.delete_group(uid)
    response = build_response(200, json.dumps(output))
    return response
