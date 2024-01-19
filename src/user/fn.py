import json
import os
from aws_xray_sdk.core import patch_all
from enum import Enum
from lib.util import build_response, get_body, get_param, log_event
from lib.domain.user import User

# initialization
patch_all()
user = User()
redirect_url = os.environ.get("REDIRECT_URL")

# action
class Action(Enum):
    LIST_USERS = 1
    LIST_USERS_BY_GROUP = 2
    LIST_USERS_BY_PLAN = 3
    GET_USER = 4
    GET_USER_STATS = 5
    SUBSCRIBE_USER = 6
    UNSUBSCRIBE_USER = 7

def get_action(qsp, uid, group_id, plan_id, stats, subscribe, unsubscribe):
    response = Action.LIST_USERS
    if qsp is None:
        response = Action.LIST_USERS
    elif (len(qsp) == 1 or len(qsp) == 2) and group_id is not None:
        response = Action.LIST_USERS_BY_GROUP
    elif (len(qsp) == 1 or len(qsp) == 2) and plan_id is not None:
        response = Action.LIST_USERS_BY_PLAN
    elif len(qsp) == 1 and uid is not None:
        response = Action.GET_USER
    elif len(qsp) == 1 and stats is not None:
        response = Action.GET_USER_STATS
    elif len(qsp) == 1 and subscribe is not None:
        response = Action.SUBSCRIBE_USER
    elif len(qsp) == 1 and unsubscribe is not None:
        response = Action.UNSUBSCRIBE_USER
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
            group_id = get_param(qsp, "group_id")
            plan_id = get_param(qsp, "plan_id")
            stats = get_param(qsp, "stats")
            subscribe = get_param(qsp, "subscribe")
            unsubscribe = get_param(qsp, "unsubscribe")
            is_subscribed = get_param(qsp, "is_subscribed") == "true"
            action = get_action(qsp, uid, group_id, plan_id, stats, subscribe, unsubscribe)
            match action:
                case Action.LIST_USERS_BY_GROUP:
                    output = user.list_users_by_group(group_id, is_subscribed)
                case Action.LIST_USERS_BY_PLAN:
                    output = user.list_users_by_plan(plan_id, is_subscribed)
                case Action.GET_USER:
                    output = user.get_user(uid)
                case Action.GET_USER_STATS:
                    output = user.get_user_stats(stats)
                case Action.SUBSCRIBE_USER:
                    output = user.subscribe_user(subscribe)
                    if redirect_url is not None:
                        response_code = 302
                        response_headers["Location"] = f"{redirect_url}?uid={subscribe}"
                case Action.UNSUBSCRIBE_USER:
                    output = user.unsubscribe_user(unsubscribe)
                    if redirect_url is not None:
                        response_code = 302
                        response_headers["Location"] = f"{redirect_url}?uid={unsubscribe}"
                case _:
                    output = user.list_users()
        case "POST":
            body = get_body(event)
            output = user.create_user(body.get("description"), body.get("email"), body.get("is_subscribed"), body.get("group_ids"), body.get("plan_ids"))
            uid = output["uid"]
            if redirect_url is not None:
                response_code = 302
                response_headers["Location"] = f"{redirect_url}?uid={uid}"
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
    print(json.dumps(response))
    return response
