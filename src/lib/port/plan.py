import boto3
import json
import os
from lib.adapter.dynamodb import DynamoDBAdapter

class PlanPort:
    def __init__(self):
        self.table = os.environ.get("TABLE")
        self.client = DynamoDBAdapter(self.table)

    def list_plans(self):
        response = self.client.query(
            key_condition = "category = :category",
            expression_values = {
                ":category": {"S": "plan"}
            },
            projection_expression = "category, uid, is_private"
        )
        return response

    def get_plan(self, uid):
        response = self.client.query(
            key_condition = "category = :category AND uid = :uid",
            expression_values = {
                ":category": {"S": "plan"},
                ":uid": {"S": uid}
            },
            projection_expression = "category, uid, description, is_private"
        )
        return response

    def get_plan_with_description(self, description):
        self.client.set_lsi("description")
        response = self.client.query(
            key_condition = "category = :category AND description = :description",
            expression_values = {
                ":category": {"S": "plan"},
                ":description": {"S": description}
            },
            projection_expression = "category, uid, description"
        )
        self.client.reset_lsi()
        return response

    def create_plan(self, uid, description, is_private=False):
        item = {
            "category": {"S": "plan"},
            "uid": {"S": uid},
            "description": {"S": description},
            "is_private": {"BOOL": is_private}
        }
        response = self.client.put(item)
        return response

    def update_plan(self, uid, description, is_private=False):
        item_key = {
            "category": {"S": "plan"},
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
        return response

    def delete_plan(self, uid):
        item_key = {
            "category": {"S": "plan"},
            "uid": {"S": uid}
        }
        response = self.client.delete(item_key)
        return response