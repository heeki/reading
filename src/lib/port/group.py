import boto3
import json
import os
from lib.adapter.dynamodb import DynamoDBAdapter

class GroupPort:
    def __init__(self):
        self.table = os.environ.get("TABLE")
        self.client = DynamoDBAdapter(self.table)

    def transform(self, item):
        output = {
            "category": item["category"]["S"],
            "uid": item["uid"]["S"],
            "description": item["description"]["S"],
            "is_private": item["is_private"]["BOOL"]
        }
        return output

    def list_groups(self):
        response = self.client.query(
            key_condition = "category = :category",
            expression_values = {
                ":category": {"S": "group"}
            },
            projection_expression = "category, uid, description, is_private"
        )
        output = []
        for item in response:
            output.append(self.transform(item))
        return output

    def get_group(self, uid):
        response = self.client.query(
            key_condition = "category = :category AND uid = :uid",
            expression_values = {
                ":category": {"S": "group"},
                ":uid": {"S": uid}
            },
            projection_expression = "category, uid, description, is_private"
        )
        output = self.transform(response[0])
        return output

    def get_group_with_description(self, description):
        self.client.set_lsi("description")
        response = self.client.query(
            key_condition = "category = :category AND description = :description",
            expression_values = {
                ":category": {"S": "group"},
                ":description": {"S": description}
            },
            projection_expression = "category, uid, description, is_private"
        )
        self.client.reset_lsi()
        output = self.transform(response[0])
        return output

    def create_group(self, uid, description, is_private=False):
        item = {
            "category": {"S": "group"},
            "uid": {"S": uid},
            "description": {"S": description},
            "is_private": {"BOOL": is_private}
        }
        response = self.client.put(item)
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            output = {"uid": uid}
        else:
            output = {"uid": "00000000-0000-0000-0000-000000000000"}
        return output

    def update_group(self, uid, description, is_private=False):
        item_key = {
            "category": {"S": "group"},
            "uid": {"S": uid}
        }
        response = self.client.update(
            item_key,
            update_expression="SET #description = :description, #is_private = :is_private",
            expression_names={
                "#description": "description",
                "#is_private": "is_private"
            },
            expression_attributes={
                ":description": {"S": description},
                ":is_private": {"BOOL": is_private}
            }
        )
        output = self.transform(response["Attributes"])
        return output

    def delete_group(self, uid):
        item_key = {
            "category": {"S": "group"},
            "uid": {"S": uid}
        }
        response = self.client.delete(item_key)
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            output = self.transform(response["Attributes"])
        else:
            output = {"uid": "00000000-0000-0000-0000-000000000000"}
        return output