import json
import uuid
from lib.port.reading import ReadingPort

class Reading:
    def __init__(self):
        self.port = ReadingPort()

    def list_readings(self):
        response = self.port.list_readings()
        return response

    def get_reading(self, uid):
        response = self.port.get_reading(uid)
        return response

    def get_reading_with_description(self, description):
        response = self.port.get_reading_with_description(description)
        return response

    def create_reading(self, description, body, plan_id, sent_date, sent_count):
        uid = str(uuid.uuid4())
        response = self.port.create_reading(uid, description, body, plan_id, sent_date, sent_count)
        response["Item"] = {
            "uid": uid
        }
        return response

    def update_reading(self, uid, description, body, plan_id, sent_date, sent_count):
        response = self.port.update_reading(uid, description, body, plan_id, sent_date, sent_count)
        return response

    def delete_reading(self, uid):
        response = self.port.delete_reading(uid)
        return response
