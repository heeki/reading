import boto3
import json
import logging
from aws_xray_sdk.core import patch_all
from lib.util import log_event
from lib.domain.backup import Backup

# initialization
boto3.set_stream_logger(name="aws_xray_sdk.core.context", level=logging.ERROR)
boto3.set_stream_logger(name="aws_xray_sdk.core.lambda_launcher", level=logging.ERROR)
boto3.set_stream_logger(name="aws_xray_sdk.core.patcher", level=logging.ERROR)
boto3.set_stream_logger(name="botocore.credentials", level=logging.ERROR)
patch_all()
backup = Backup()

def handler(event, context):
    log_event(event)
    response = backup.backup()
    response.pop("Items", None)
    print(json.dumps(response))
    return response
