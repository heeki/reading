import json
import uuid
from lib.port.plan import PlanPort

class Plan:
    def __init__(self):
        self.port = PlanPort()

    def list_plans(self):
        response = self.port.list_plans()
        return response

    def get_plan(self, uid):
        response = self.port.get_plan(uid)
        return response

    def get_plan_with_description(self, description):
        response = self.port.get_plan_with_description(description)
        return response

    def create_plan(self, name):
        uid = str(uuid.uuid4())
        response = self.port.create_plan(uid, name)
        response["Item"] = {
            "uid": uid
        }
        return response

    def delete_plan(self, uid):
        response = self.port.delete_plan(uid)
        return response
