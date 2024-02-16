import datetime
import json
import uuid
from lib.port.reading import ReadingPort
from lib.port.user import UserPort

class Reading:
    def __init__(self):
        self.port = ReadingPort()
        self.user = UserPort()

    def list_readings(self):
        response = self.port.list_readings()
        return response

    def list_readings_by_user(self, user_id):
        response = self.port.list_readings_by_user(user_id)
        return response

    def list_readings_by_group(self, group_id):
        users = self.user.list_users_by_group(group_id)
        response = []
        for user in users:
            user_id = user["uid"]
            user_readings = self.list_readings_by_user(user_id)
            response += user_readings
        return response

    def list_readings_until_today(self):
        response = self.port.list_readings_until_today()
        return response

    def get_reading(self, uid):
        response = self.port.get_reading(uid)
        return response

    def get_reading_by_description(self, description):
        response = self.port.get_reading_by_description(description)
        return response

    def get_reading_by_date(self, date):
        response = self.port.get_reading_by_date(date)
        return response

    def create_reading(self, description, body, plan_id, sent_date):
        uid = str(uuid.uuid4())
        response = self.port.create_reading(uid, description, body, plan_id, sent_date)
        return response

    def update_reading(self, uid, description, body, plan_id, sent_date):
        response = self.port.update_reading(uid, description, body, plan_id, sent_date)
        return response

    def delete_reading(self, uid):
        response = self.port.delete_reading(uid)
        return response

    def add_user_completion(self, uid, user_id):
        response = self.port.add_user_completion(uid, user_id)
        return response

    def update_reading_sent_count(self, uid, sent_count):
        response = self.port.update_reading_sent_count(uid, sent_count)
        return response

    def get_sent_count(self, uid):
        reading = self.get_reading(uid)
        today = datetime.datetime.now().date()
        response = {}
        reading_date = datetime.datetime.fromisoformat(reading["sent_date"]).date()
        if reading_date <= today and "sent_count" in reading:
            date_key = str(reading_date)
            sent_count = json.loads(reading["sent_count"])
            for group_id in sent_count.keys():
                if group_id in response:
                    if date_key in response[group_id]:
                        response[group_id][date_key] += sent_count[group_id]
                    else:
                        response[group_id][date_key] = sent_count[group_id]
                else:
                    response[group_id] = {date_key: sent_count[group_id]}
        return response
