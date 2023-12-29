import json

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

def get_param(params, param):
    response = None
    if params is not None and param in params:
        response = params[param]
    return response

def log_event(event):
    output = event
    if "multiValueHeaders" in output:
        del output["multiValueHeaders"]
    print(json.dumps(output))
