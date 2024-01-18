import boto3
import json
import os
from aws_xray_sdk.core import patch_all
from lib.util import build_response, get_body, get_param, log_event
from lib.domain.reading import Reading

# initialization
reading = Reading()
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
            date = get_param(qsp, "date")
            user_id = get_param(qsp, "user_id")
            group_id = get_param(qsp, "group_id")
            if uid is not None and user_id is not None:
                output = reading.add_user_completion(uid, user_id)
                if redirect_url is not None:
                    response_code = 302
                    response_headers["Location"] = f"{redirect_url}?uid={user_id}"
            elif uid is not None and user_id is None:
                output = reading.get_reading(uid)
            elif uid is None and user_id is not None:
                output = reading.list_readings_by_user(user_id)
            elif group_id is not None:
                output = reading.list_readings_by_group(group_id)
            elif date is not None:
                output = reading.get_reading_by_date(date)
            else:
                output = reading.list_readings()
        case "POST":
            body = get_body(event)
            output = reading.create_reading(body.get("description"), body.get("body"), body.get("plan_id"), body.get("sent_date"), str(body.get("sent_count")))
        case "PUT":
            uid = get_param(qsp, "uid")
            if uid is not None:
                body = get_body(event)
                output = reading.update_reading(uid, body.get("description"), body.get("body"), body.get("plan_id"), body.get("sent_date"), str(body.get("sent_count")))
        case "DELETE":
            uid = get_param(qsp, "uid")
            if uid is not None:
                output = reading.delete_reading(uid)
    response = build_response(response_code, json.dumps(output), response_headers)
    return response
