import boto3
import json
import os
from aws_xray_sdk.core import patch_all
from lib.util import build_response, get_body, get_param, log_event
from lib.domain.user import User

# initialization
user = User()
patch_all()
redirect_url = os.environ.get("REDIRECT_URL")

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
            group_id = get_param(qsp, "group_id")
            plan_id = get_param(qsp, "plan_id")
            subscribe = get_param(qsp, "subscribe")
            unsubscribe = get_param(qsp, "unsubscribe")
            is_subscribed = get_param(qsp, "is_subscribed")
            if is_subscribed is not None:
                is_subscribed = is_subscribed == "true"
            if uid is not None:
                output = user.get_user(uid)
            elif group_id is not None:
                output = user.list_users_by_group(group_id, is_subscribed)
            elif plan_id is not None:
                output = user.list_users_by_plan(plan_id, is_subscribed)
            elif subscribe is not None:
                output = user.subscribe_user(subscribe)
                if redirect_url is not None:
                    response_code = 302
                    response_headers["Location"] = f"{redirect_url}?uid={subscribe}"
            elif unsubscribe is not None:
                output = user.unsubscribe_user(unsubscribe)
                if redirect_url is not None:
                    response_code = 302
                    response_headers["Location"] = f"{redirect_url}?uid={unsubscribe}"
            else:
                output = user.list_users()
        case "POST":
            body = get_body(event)
            output = user.create_user(body.get("description"), body.get("email"), body.get("is_subscribed"), body.get("group_ids"), body.get("plan_ids"))
        case "PUT":
            uid = get_param(qsp, "uid")
            if uid is not None:
                body = get_body(event)
                output = user.update_user(uid, body.get("description"), body.get("email"), body.get("is_subscribed"), body.get("group_ids"), body.get("plan_ids"))
        case "DELETE":
            uid = get_param(qsp, "uid")
            if uid is not None:
                output = user.delete_user(uid)
    response = build_response(response_code, json.dumps(output), response_headers)
    return response
