import boto3
import json
import os
from lib.adapter.dynamodb import DynamoDBAdapter

class ReadingPort:
    def __init__(self):
        self.table = os.environ.get("TABLE")
        self.client = DynamoDBAdapter(self.table)

    def list_readings(self):
        response = self.client.query(
            key_condition = "category = :category",
            expression_values = {
                ":category": {"S": "reading"}
            },
            projection_expression = "category, uid, description, plan_id, sent_date, sent_count"
        )
        return response

    def get_reading(self, uid):
        response = self.client.query(
            key_condition = "category = :category AND uid = :uid",
            expression_values = {
                ":category": {"S": "reading"},
                ":uid": {"S": uid}
            },
            projection_expression = "category, uid, description, body, plan_id, sent_date, sent_count"
        )
        return response

    def get_reading_with_description(self, description):
        self.client.set_lsi("description")
        response = self.client.query(
            key_condition = "category = :category AND description = :description",
            expression_values = {
                ":category": {"S": "reading"},
                ":description": {"S": description}
            },
            projection_expression = "category, uid, description, body, plan_id, sent_date, sent_count"
        )
        self.client.reset_lsi()
        return response

    def create_reading(self, uid, description, body, plan_id, sent_date, sent_count):
        item = {
            "category": {"S": "reading"},
            "uid": {"S": uid},
            "description": {"S": description},
            "body": {"S": body},
            "plan_id": {"S": plan_id},
            "sent_date": {"S": sent_date},
            "sent_count": {"N": sent_count}
        }
        response = self.client.put(item)
        return response

    def update_reading(self, uid, description, body, plan_id, sent_date, sent_count):
        item_key = {
            "category": {"S": "reading"},
            "uid": {"S": uid}
        }
        response = self.client.update(
            item_key,
            update_expression="SET #description = :description, #body = :body, #plan_id = :plan_id, #sent_date = :sent_date, #sent_count = :sent_count",
            expression_names={
                "#description": "description",
                "#body": "body",
                "#plan_id": "plan_id",
                "#sent_date": "sent_date",
                "#sent_count": "sent_count"
            },
            expression_attributes={
                ":description": {"S": description},
                ":body": {"S": body},
                ":plan_id": {"S": plan_id},
                ":sent_date": {"S": sent_date},
                ":sent_count": {"N": sent_count}
            }
        )
        return response

    def delete_reading(self, uid):
        item_key = {
            "category": {"S": "reading"},
            "uid": {"S": uid}
        }
        response = self.client.delete(item_key)
        return response