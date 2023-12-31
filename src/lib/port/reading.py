import json
import os
from botocore.exceptions import ClientError
from lib.adapter.dynamodb import DynamoDBAdapter

class ReadingPort:
    def __init__(self):
        self.table = os.environ.get("TABLE")
        self.client = DynamoDBAdapter(self.table)

    def _transform(self, item):
        output = {
            "category": item["category"]["S"],
            "uid": item["uid"]["S"],
            "description": item["description"]["S"],
            "plan_id": item["plan_id"]["S"],
            "sent_date": item["sent_date"]["S"],
            "sent_count": item["sent_count"]["N"]
        }
        if "body" in item:
            output["body"] = item["body"]["S"]
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

    def list_readings(self):
        response = self.client.query(
            key_condition = "category = :category",
            expression_values = {
                ":category": {"S": "reading"}
            },
            projection_expression = "category, uid, description, plan_id, sent_date, sent_count"
        )
        output = self.transform(response)
        return output

    def get_reading(self, uid):
        response = self.client.query(
            key_condition = "category = :category AND uid = :uid",
            expression_values = {
                ":category": {"S": "reading"},
                ":uid": {"S": uid}
            },
            projection_expression = "category, uid, description, body, plan_id, sent_date, sent_count"
        )
        transformed = self.transform(response)
        output = transformed[0] if len(transformed) > 0 else {}
        return output

    def get_reading_by_date(self, date):
        response = self.client.query(
            key_condition = "category = :category",
            filter_expression = "begins_with(sent_date, :sent_date)",
            expression_values = {
                ":category": {"S": "reading"},
                ":sent_date": {"S": date}
            },
            projection_expression = "category, uid, description, body, plan_id, sent_date, sent_count"
        )
        transformed = self.transform(response)
        output = transformed[0] if len(transformed) > 0 else {}
        return output

    def get_reading_by_description(self, description):
        self.client.set_index("description")
        response = self.client.query(
            key_condition = "category = :category AND description = :description",
            expression_values = {
                ":category": {"S": "reading"},
                ":description": {"S": description}
            },
            projection_expression = "category, uid, description, body, plan_id, sent_date, sent_count"
        )
        self.client.reset_index()
        transformed = self.transform(response)
        output = transformed[0] if len(transformed) > 0 else {}
        return output

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
        output = {"uid": uid} if response["ResponseMetadata"]["HTTPStatusCode"] == 200 else {}
        return output

    def update_reading(self, uid, description, body, plan_id, sent_date, sent_count):
        item_key = {
            "category": {"S": "reading"},
            "uid": {"S": uid}
        }
        try:
            response = self.client.update(
                item_key,
                update_expression="SET #description = :description, #body = :body, #plan_id = :plan_id, #sent_date = :sent_date, #sent_count = :sent_count",
                condition_expression="#uid = :uid",
                expression_names = {
                    "#uid": "uid",
                    "#description": "description",
                    "#body": "body",
                    "#plan_id": "plan_id",
                    "#sent_date": "sent_date",
                    "#sent_count": "sent_count"
                },
                expression_attributes = {
                    ":uid": {"S": uid},
                    ":description": {"S": description},
                    ":body": {"S": body},
                    ":plan_id": {"S": plan_id},
                    ":sent_date": {"S": sent_date},
                    ":sent_count": {"N": sent_count}
                }
            )
            output = self.transform(response)
        except ClientError as e:
            output = {
                "error": e.response["Error"]["Code"],
                "message": "requested uid not found"
            }
        return output

    def delete_reading(self, uid):
        item_key = {
            "category": {"S": "reading"},
            "uid": {"S": uid}
        }
        response = self.client.delete(item_key)
        output = {"uid": uid} if "Attributes" in response else {}
        return output