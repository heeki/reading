import boto3
import json
from aws_xray_sdk.core import patch_all
from lib.util import build_response, get_body, get_param, log_event
from lib.domain.user import User

# initialization
user = User()
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
                output = user.get_user(uid)
            else:
                output = user.list_users()
        case "POST":
            body = get_body(event)
            output = user.create_user(body.get("description"), body.get("email"), body.get("group_id"))
        case "PUT":
            uid = get_param(qsp, "uid")
            if uid is not None:
                body = get_body(event)
                output = user.update_user(uid, body.get("description"), body.get("email"), body.get("group_id"))
        case "DELETE":
            uid = get_param(qsp, "uid")
            if uid is not None:
                output = user.delete_user(uid)
    response = build_response(200, json.dumps(output))
    return response
