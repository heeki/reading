import json
import os
from botocore.exceptions import ClientError
from lib.adapter.dynamodb import DynamoDBAdapter

class PlanPort:
    def __init__(self):
        self.table = os.environ.get("TABLE")
        self.client = DynamoDBAdapter(self.table)

    def _transform(self, item):
        output = {
            "category": item["category"]["S"],
            "uid": item["uid"]["S"],
            "description": item["description"]["S"],
            "is_private": item["is_private"]["BOOL"]
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

    def list_plans(self):
        response = self.client.query(
            key_condition = "category = :category",
            expression_values = {
                ":category": {"S": "plan"}
            },
            projection_expression = "category, uid, description, is_private"
        )
        output = self.transform(response)
        return output

    def get_plan(self, uid):
        response = self.client.query(
            key_condition = "category = :category AND uid = :uid",
            expression_values = {
                ":category": {"S": "plan"},
                ":uid": {"S": uid}
            },
            projection_expression = "category, uid, description, is_private"
        )
        transformed = self.transform(response)
        output = transformed[0] if len(transformed) > 0 else {}
        return output

    def get_plan_with_description(self, description):
        self.client.set_lsi("description")
        response = self.client.query(
            key_condition = "category = :category AND description = :description",
            expression_values = {
                ":category": {"S": "plan"},
                ":description": {"S": description}
            },
            projection_expression = "category, uid, description, is_private"
        )
        self.client.reset_lsi()
        transformed = self.transform(response)
        output = transformed[0] if len(transformed) > 0 else {}
        return output

    def create_plan(self, uid, description, is_private=False):
        item = {
            "category": {"S": "plan"},
            "uid": {"S": uid},
            "description": {"S": description},
            "is_private": {"BOOL": is_private}
        }
        response = self.client.put(item)
        output = {"uid": uid} if response["ResponseMetadata"]["HTTPStatusCode"] == 200 else {}
        return output

    def update_plan(self, uid, description, is_private=False):
        item_key = {
            "category": {"S": "plan"},
            "uid": {"S": uid}
        }
        output = {"message": "uid not found"}
        try:
            response = self.client.update(
                item_key,
                update_expression="SET #description = :description, #is_private = :is_private",
                condition_expression="#uid = :uid",
                expression_names = {
                    "#uid": "uid",
                    "#description": "description",
                    "#is_private": "is_private"
                },
                expression_attributes = {
                    ":uid": {"S": uid},
                    ":description": {"S": description},
                    ":is_private": {"BOOL": is_private}
                }
            )
            output = self.transform(response)
        except ClientError as e:
            output = {
                "error": e.response["Error"]["Code"],
                "message": "requested uid not found"
            }
        return output

    def delete_plan(self, uid):
        item_key = {
            "category": {"S": "plan"},
            "uid": {"S": uid}
        }
        response = self.client.delete(item_key)
        output = {"uid": uid} if "Attributes" in response else {}
        return output