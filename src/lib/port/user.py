import boto3
import json
import os
from lib.adapter.dynamodb import DynamoDBAdapter

class UserPort:
    def __init__(self):
        self.table = os.environ.get("TABLE")
        self.client = DynamoDBAdapter(self.table)

    def list_users(self):
        response = self.client.query(
            key_condition = "category = :category",
            expression_values = {
                ":category": {"S": "user"}
            },
            projection_expression = "category, uid, description, email"
        )
        return response

    def get_user(self, uid):
        response = self.client.query(
            key_condition = "category = :category AND uid = :uid",
            expression_values = {
                ":category": {"S": "user"},
                ":uid": {"S": uid}
            },
            projection_expression = "category, uid, description, email"
        )
        return response

    def get_user_with_description(self, description):
        self.client.set_lsi("description")
        response = self.client.query(
            key_condition = "category = :category AND description = :description",
            expression_values = {
                ":category": {"S": "user"},
                ":description": {"S": description}
            },
            projection_expression = "category, uid, description, email"
        )
        self.client.reset_lsi()
        return response

    def create_user(self, uid, description, email):
        item = {
            "category": {"S": "user"},
            "uid": {"S": uid},
            "description": {"S": description},
            "email": {"S": email}
        }
        response = self.client.put(item)
        return response

    def update_user(self, uid, description, email):
        item_key = {
            "category": {"S": "user"},
            "uid": {"S": uid}
        }
        response = self.client.update(
            item_key,
            update_expression="SET #description = :description, #email = :email",
            expression_names={
                "#description": "description",
                "#email": "email"
            },
            expression_attributes={
                ":description": {"S": description},
                ":email": {"S": email}
            }
        )
        return response

    def delete_user(self, uid):
        item_key = {
            "category": {"S": "user"},
            "uid": {"S": uid}
        }
        response = self.client.delete(item_key)
        return response