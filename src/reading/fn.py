import boto3
import json
import logging
import os
from aws_xray_sdk.core import patch_all
from enum import Enum
from lib.util import build_response, get_body, get_param, log_event
from lib.domain.reading import Reading

# initialization
boto3.set_stream_logger(name="aws_xray_sdk.core.context", level=logging.ERROR)
boto3.set_stream_logger(name="aws_xray_sdk.core.lambda_launcher", level=logging.ERROR)
boto3.set_stream_logger(name="aws_xray_sdk.core.patcher", level=logging.ERROR)
boto3.set_stream_logger(name="botocore.credentials", level=logging.ERROR)
patch_all()
reading = Reading()
redirect_url = os.environ.get("REDIRECT_URL")

# action
class Action(Enum):
    LIST_READINGS = 1
    LIST_READINGS_BY_USER = 2
    LIST_READINGS_BY_GROUP = 3
    GET_READING = 4
    GET_READING_BY_DATE = 5
    GET_SENT_COUNT = 6
    ADD_USER_COMPLETION = 7

def get_action(qsp, uid, date, user_id, group_id, sent_count):
    response = Action.LIST_READINGS
    if qsp is None:
        response = Action.LIST_READINGS
    elif len(qsp) == 1 and user_id is not None:
        response = Action.LIST_READINGS_BY_USER
    elif len(qsp) == 1 and group_id is not None:
        response = Action.LIST_READINGS_BY_GROUP
    elif len(qsp) == 1 and uid is not None:
        response = Action.GET_READING
    elif len(qsp) == 1 and date is not None:
        response = Action.GET_READING_BY_DATE
    elif len(qsp) == 1 and sent_count is not None:
        response = Action.GET_SENT_COUNT
    elif len(qsp) == 2 and uid is not None and user_id is not None:
        response = Action.ADD_USER_COMPLETION
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
            date = get_param(qsp, "date")
            user_id = get_param(qsp, "user_id")
            group_id = get_param(qsp, "group_id")
            sent_count = get_param(qsp, "group_id")
            action = get_action(qsp, uid, date, user_id, group_id, sent_count)
            match action:
                case Action.LIST_READINGS_BY_USER:
                    output = reading.list_readings_by_user(user_id)
                case Action.LIST_READINGS_BY_GROUP:
                    output = reading.list_readings_by_group(group_id)
                case Action.GET_READING:
                    output = reading.get_reading(uid)
                case Action.GET_READING_BY_DATE:
                    output = reading.get_reading_by_date(date)
                case Action.GET_SENT_COUNT:
                    output = reading.get_sent_count(sent_count)
                case Action.ADD_USER_COMPLETION:
                    output = reading.add_user_completion(uid, user_id)
                    if redirect_url is not None:
                        response_code = 302
                        response_headers["Location"] = f"{redirect_url}?uid={user_id}"
                case _:
                    output = reading.list_readings()
        case "POST":
            body = get_body(event)
            output = reading.create_reading(body.get("description"), body.get("body"), body.get("plan_id"), body.get("sent_date"))
        case "PUT":
            uid = get_param(qsp, "uid")
            if uid is not None:
                body = get_body(event)
                results = body.get("results")
                if results is not None:
                    sent_count = {
                        "users": [],
                        "groups": {}
                    }
                    for result in results:
                        user_id = result.get("user_id")
                        sent_count["users"].append(user_id)
                        group_id = result.get("group_id")
                        if group_id in sent_count["groups"]:
                            sent_count["groups"][group_id] += 1
                        else:
                            sent_count["groups"][group_id] = 1
                    output = reading.update_reading_sent_count(uid, sent_count)
                else:
                    output = reading.update_reading(uid, body.get("description"), body.get("body"), body.get("plan_id"), body.get("sent_date"))
        case "DELETE":
            uid = get_param(qsp, "uid")
            if uid is not None:
                output = reading.delete_reading(uid)
    response = build_response(response_code, json.dumps(output), response_headers)
    return response
