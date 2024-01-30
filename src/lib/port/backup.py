import datetime
import json
import os
from botocore.exceptions import ClientError
from lib.adapter.dynamodb import DynamoDBAdapter
from lib.adapter.s3 import S3Adapter

class BackupPort:
    def __init__(self):
        self.table = os.environ.get("TABLE")
        self.client_dynamodb = DynamoDBAdapter(self.table)
        self.bucket = os.environ.get("BACKUP_BUCKET")
        self.client_s3 = S3Adapter(self.bucket)

    def backup(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        okey = f"backup_{timestamp}.json"
        response = self.client_dynamodb.scan()
        self.client_s3.put(okey, json.dumps(response["Items"]))
        return response