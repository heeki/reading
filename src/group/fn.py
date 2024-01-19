import json
import os
from aws_xray_sdk.core import patch_all
from enum import Enum
from lib.util import build_response, get_body, get_param, log_event
from lib.domain.group import Group

# initialization
patch_all()
group = Group()
redirect_url = os.environ.get("REDIRECT_URL")

# action
class Action(Enum):
    LIST_GROUPS = 1
    GET_GROUP = 2
    GET_GROUP_STATS = 3

def get_action(qsp, uid, stats):
    response = Action.LIST_GROUPS
    if qsp is None:
        response = Action.LIST_GROUPS
    elif len(qsp) == 1 and uid is not None:
        response = Action.GET_GROUP
    elif len(qsp) == 1 and stats is not None:
        response = Action.GET_GROUP_STATS
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
            stats = get_param(qsp, "stats")
            action = get_action(qsp, uid, stats)
            match action:
                case Action.GET_GROUP:
                    output = group.get_group(uid)
                case Action.GET_GROUP_STATS:
                    output = group.get_group_stats(stats)
                case _:
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
    response = build_response(response_code, json.dumps(output), response_headers)
    return response
