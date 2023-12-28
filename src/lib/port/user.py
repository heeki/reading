import json
import os
from botocore.exceptions import ClientError
from lib.adapter.dynamodb import DynamoDBAdapter

class UserPort:
    def __init__(self):
        self.table = os.environ.get("TABLE")
        self.client = DynamoDBAdapter(self.table)

    def _transform(self, item):
        output = {
            "category": item["category"]["S"],
            "uid": item["uid"]["S"],
            "description": item["description"]["S"],
            "email": item["email"]["S"],
            "group_ids": json.loads(item["group_ids"]["S"])
        }
        return output

    def transform(self, item):
        match item:
            case list():
                output = [self._transform(i) for i in item]
            case _:
                if "Attributes" in item:
                    output = self._transform(item["Attributes"])
                elif "ResponseMetadata" in item:
                    output = {
                        "ResponseMetadata": {
                            "HTTPStatusCode": item["ResponseMetadata"]["HTTPStatusCode"]
                        }
                    }
                else:
                    output = self._transform(item)
        return output

    def list_users(self):
        response = self.client.query(
            key_condition = "category = :category",
            expression_values = {
                ":category": {"S": "user"}
            },
            projection_expression = "category, uid, description, email, group_ids"
        )
        output = self.transform(response)
        return output

    def get_user(self, uid):
        response = self.client.query(
            key_condition = "category = :category AND uid = :uid",
            expression_values = {
                ":category": {"S": "user"},
                ":uid": {"S": uid}
            },
            projection_expression = "category, uid, description, email, group_ids"
        )
        transformed = self.transform(response)
        output = transformed[0] if len(transformed) > 0 else {}
        return output

    def get_user_with_description(self, description):
        self.client.set_lsi("description")
        response = self.client.query(
            key_condition = "category = :category AND description = :description",
            expression_values = {
                ":category": {"S": "user"},
                ":description": {"S": description}
            },
            projection_expression = "category, uid, description, email, group_ids"
        )
        self.client.reset_lsi()
        transformed = self.transform(response)
        output = transformed[0] if len(transformed) > 0 else {}
        return output

    def create_user(self, uid, description, email, group_ids):
        item = {
            "category": {"S": "user"},
            "uid": {"S": uid},
            "description": {"S": description},
            "email": {"S": email},
            "group_ids": {"S": json.dumps(group_ids)}
        }
        response = self.client.put(item)
        output = {"uid": uid} if response["ResponseMetadata"]["HTTPStatusCode"] == 200 else {}
        return output

    def update_user(self, uid, description, email, group_ids):
        item_key = {
            "category": {"S": "user"},
            "uid": {"S": uid}
        }
        output = {"message": "uid not found"}
        try:
            response = self.client.update(
                item_key,
                update_expression="SET #description = :description, #email = :email, #group_ids = :group_ids",
                condition_expression="uid = :uid",
                expression_names={
                    "#description": "description",
                    "#email": "email",
                    "#group_ids": "group_ids"
                },
                expression_attributes={
                    ":uid": {"S": uid},
                    ":description": {"S": description},
                    ":email": {"S": email},
                    ":group_ids": {"S": json.dumps(group_ids)}
                }
            )
            output = self.transform(response)
        except ClientError as e:
            output = {
                "error": e.response["Error"]["Code"],
                "message": "requested uid not found"
            }
        return output

    def delete_user(self, uid):
        item_key = {
            "category": {"S": "user"},
            "uid": {"S": uid}
        }
        response = self.client.delete(item_key)
        output = {"uid": uid} if "Attributes" in response else {}
        return output