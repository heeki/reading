import os
from lib.adapter.dynamodb import DynamoDBAdapter
import json

table = os.environ.get("RESTORE_TABLE")
client_dynamodb = DynamoDBAdapter(table)
# response = client_dynamodb.scan()
# print(json.dumps(response))

with open("tmp/backup_20241216_190758.json") as f:
    data = json.load(f)
    for item in data:
        client_dynamodb.put(item)

response = client_dynamodb.scan()
print(json.dumps(response))