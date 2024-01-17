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
            "is_subscribed": item["is_subscribed"]["BOOL"]
        }
        if "group_ids" in item:
            output["group_ids"] = json.loads(item["group_ids"]["S"])
        if "plan_ids" in item:
            output["plan_ids"] = json.loads(item["plan_ids"]["S"])
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
            projection_expression = "category, uid, description, email, is_subscribed, group_ids, plan_ids"
        )
        output = self.transform(response)
        return output

    def list_users_by_group(self, group_id, is_subscribed):
        filter_expression = "contains(group_ids, :group_id)"
        expression_values = {
            ":category": {"S": "user"},
            ":group_id": {"S": group_id}
        }
        if is_subscribed is not None:
            filter_expression += " and is_subscribed = :is_subscribed"
            expression_values[":is_subscribed"] = {"BOOL": is_subscribed}
        response = self.client.query(
            key_condition = "category = :category",
            filter_expression = filter_expression,
            expression_values = expression_values,
            projection_expression = "category, uid, description, email, is_subscribed, group_ids, plan_ids"
        )
        output = self.transform(response)
        return output

    def list_users_by_plan(self, plan_id, is_subscribed):
        filter_expression = "contains(plan_ids, :plan_id)"
        expression_values = {
            ":category": {"S": "user"},
            ":plan_id": {"S": plan_id}
        }
        if is_subscribed is not None:
            filter_expression += " and is_subscribed = :is_subscribed"
            expression_values[":is_subscribed"] = {"BOOL": is_subscribed}
        print(filter_expression)
        print(json.dumps(expression_values))
        response = self.client.query(
            key_condition = "category = :category",
            filter_expression = filter_expression,
            expression_values = expression_values,
            projection_expression = "category, uid, description, email, is_subscribed, group_ids, plan_ids"
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
            projection_expression = "category, uid, description, email, is_subscribed, group_ids, plan_ids"
        )
        transformed = self.transform(response)
        output = transformed[0] if len(transformed) > 0 else {}
        return output

    def get_user_by_description(self, description):
        self.client.set_index("description")
        response = self.client.query(
            key_condition = "category = :category AND description = :description",
            expression_values = {
                ":category": {"S": "user"},
                ":description": {"S": description}
            },
            projection_expression = "category, uid, description, email, is_subscribed, group_ids, plan_ids"
        )
        self.client.reset_index()
        transformed = self.transform(response)
        output = transformed[0] if len(transformed) > 0 else {}
        return output

    def create_user(self, uid, description, email, is_subscribed, group_ids, plan_ids):
        item = {
            "category": {"S": "user"},
            "uid": {"S": uid},
            "description": {"S": description},
            "email": {"S": email},
            "is_subscribed": {"BOOL": is_subscribed},
            "group_ids": {"S": json.dumps(group_ids)},
            "plan_ids": {"S": json.dumps(plan_ids)}
        }
        response = self.client.put(item)
        output = {"uid": uid} if response["ResponseMetadata"]["HTTPStatusCode"] == 200 else {}
        return output

    def update_user(self, uid, description, email, is_subscribed, group_ids, plan_ids):
        item_key = {
            "category": {"S": "user"},
            "uid": {"S": uid}
        }
        output = {"message": "uid not found"}
        try:
            response = self.client.update(
                item_key,
                update_expression="SET #description = :description, #email = :email, #is_subscribed = :is_subscribed, #group_ids = :group_ids, #plan_ids = :plan_ids",
                condition_expression="uid = :uid",
                expression_names={
                    "#description": "description",
                    "#email": "email",
                    "#is_subscribed": "is_subscribed",
                    "#group_ids": "group_ids",
                    "#plan_ids": "plan_ids"
                },
                expression_attributes={
                    ":uid": {"S": uid},
                    ":description": {"S": description},
                    ":email": {"S": email},
                    ":is_subscribed": {"BOOL": is_subscribed},
                    ":group_ids": {"S": json.dumps(group_ids)},
                    ":plan_ids": {"S": json.dumps(plan_ids)}
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