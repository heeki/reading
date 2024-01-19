import datetime
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
            "description": item["description"]["S"]
        }
        if "body" in item:
            output["body"] = item["body"]["S"]
        if "plan_id" in item:
            output["plan_id"] = item["plan_id"]["S"]
        if "sent_date" in item:
            output["sent_date"] = item["sent_date"]["S"]
        if "sent_count" in item:
            output["sent_count"] = item["sent_count"]["N"]
        if "read_by" in item:
            output["read_by"] = item["read_by"]["S"]
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
            }
        )
        output = self.transform(response)
        return output

    def list_readings_by_user(self, user_id):
        response = self.client.query(
            key_condition = "category = :category",
            filter_expression="contains(read_by, :read_by)",
            expression_values = {
                ":category": {"S": "reading"},
                ":read_by": {"S": user_id}
            },
            projection_expression="category, uid, description, plan_id, sent_date, date_count, read_by"
        )
        output = self.transform(response)
        return output

    def get_reading(self, uid):
        response = self.client.query(
            key_condition = "category = :category AND uid = :uid",
            expression_values = {
                ":category": {"S": "reading"},
                ":uid": {"S": uid}
            }
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
            }
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
            }
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

    def add_user_completion(self, uid, user_id):
        reading = self.get_reading(uid)
        read_by = json.loads(reading.get("read_by", "[]"))
        already_complete = False
        for completion in read_by:
            if completion["user_id"] == user_id:
                already_complete = True
        if not already_complete:
            read_by.append({
                "user_id": user_id,
                "timestamp": datetime.datetime.now().isoformat()
            })
            item_key = {
                "category": {"S": "reading"},
                "uid": {"S": uid}
            }
            try:
                response = self.client.update(
                    item_key,
                    update_expression="SET #read_by = :read_by",
                    condition_expression="#uid = :uid",
                    expression_names = {
                        "#uid": "uid",
                        "#read_by": "read_by"
                    },
                    expression_attributes = {
                        ":uid": {"S": uid},
                        ":read_by": {"S": json.dumps(read_by)}
                    }
                )
                output = self.transform(response)
            except ClientError as e:
                output = {
                    "error": e.response["Error"]["Code"],
                    "message": "requested uid not found"
                }
        else:
            output = reading
        return output

    def update_reading_sent_count(self, uid, sent_count):
        item_key = {
            "category": {"S": "reading"},
            "uid": {"S": uid}
        }
        try:
            response = self.client.update(
                item_key,
                update_expression="SET #sent_count = :sent_count",
                condition_expression="#uid = :uid",
                expression_names = {
                    "#uid": "uid",
                    "#sent_count": "sent_count"
                },
                expression_attributes = {
                    ":uid": {"S": uid},
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