import boto3
import json
import os
from lib.adapter.dynamodb import AdptDynamoDB

class GroupPort:
    def __init__(self):
        self.table = os.environ.get("TABLE")
        self.client = AdptDynamoDB(self.table)

    def list_groups(self):
        response = self.client.query(
            key_condition = "category = :category",
            expression_values = {
                ":category": {"S": "group"}
            },
            projection_expression = "category, uid, is_private"
        )
        return response

    def get_group(self, uid):
        response = self.client.query(
            key_condition = "category = :category AND uid = :uid",
            expression_values = {
                ":category": {"S": "group"},
                ":uid": {"S": uid}
            },
            projection_expression = "category, uid, description, is_private"
        )
        return response

    def get_group_with_description(self, description):
        self.client.set_lsi("description")
        response = self.client.query(
            key_condition = "category = :category AND description = :description",
            expression_values = {
                ":category": {"S": "group"},
                ":description": {"S": description}
            },
            projection_expression = "category, uid, description"
        )
        self.client.reset_lsi()
        return response

    def create_group(self, uid, description, is_private=False):
        item = {
            "category": {"S": "group"},
            "uid": {"S": uid},
            "description": {"S": description},
            "is_private": {"BOOL": is_private}
        }
        response = self.client.put(item)
        return response

    def delete_group(self, uid):
        item_key = {
            "category": {"S": "group"},
            "uid": {"S": uid}
        }
        response = self.client.delete(item_key)
        return response