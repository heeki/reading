import boto3
import json
from aws_xray_sdk.core import patch_all
from lib.domain.group import Group

# initialization
group = Group()
patch_all()

# helper functions
def build_response(code, body):
    headers = {
        "Content-Type": "application/json"
    }
    response = {
        "isBase64Encoded": False,
        "statusCode": code,
        "headers": headers,
        "body": body
    }
    return response

def get_body(event):
    body = json.loads(event.get("body", "{}"))
    return body

def handler(event, context):
    print(json.dumps(event))
    response = {}
    method = event.get("httpMethod", "GET")
    resource = event.get("resource")
    path = event.get("path")
    output = {}
    match method:
        case "GET":
            if resource == "/group/{proxy+}":
                uid = path.split("/")[3]
                output = group.get_group(uid)
            else:
                output = group.list_groups()
        case "POST":
            body = get_body(event)
            output = group.create_group(body.get("description"), body.get("is_private", False))
        case "PUT":
            if resource == "/group/{proxy+}":
                uid = path.split("/")[3]
                body = get_body(event)
                output = group.update_group(uid, body.get("description"), body.get("is_private", False))
        case "DELETE":
            if resource == "/group/{proxy+}":
                uid = path.split("/")[3]
                output = group.delete_group(uid)
    response = build_response(200, json.dumps(output))
    return response
