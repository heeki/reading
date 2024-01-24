import datetime
import json
from lib.domain.group import Group
from lib.domain.reading import Reading
from lib.domain.user import User

class Analysis:
    def __init__(self):
        self.user = User()
        self.group = Group()
        self.reading = Reading()

    # user
    def get_user_stats(self, uid):
        readings = self.reading.list_readings_by_user(uid)
        completions = {}
        for reading in readings:
            sent_date = str(datetime.datetime.fromisoformat(reading["sent_date"]).date())
            if "read_by" in reading:
                read_by = json.loads(reading["read_by"])
                if uid in read_by:
                    completions[sent_date] = read_by[uid]
        sent_count = self.get_sent_count_all()
        sent_dates = []
        for sent_date in sent_count["users"].keys():
            if uid in sent_count["users"][sent_date]:
                sent_dates.append(sent_date)
        response = {
            "user_id": uid,
            "user_completion_count": len(readings),
            "user_completion_per_reading": completions,
            "sent_count": len(sent_dates),
            "sent_dates": sent_dates
        }
        return response

    # group
    def _get_group_stats(self, uid):
        response = {
            "group_id": uid,
            "group_completion_count": 0,
            "group_completion_count_per_reading": {}
        }
        users = self.user.list_users_by_group(uid)
        for user in users:
            user_id = user["uid"]
            user_stats = self.get_user_stats(user_id)
            response["group_completion_count"] += user_stats["user_completion_count"]
            for sent_date in user_stats["user_completion_per_reading"].keys():
                if sent_date in response["group_completion_count_per_reading"]:
                    response["group_completion_count_per_reading"][sent_date] += 1
                else:
                    response["group_completion_count_per_reading"][sent_date] = 1
        return response

    def get_group_stats(self):
        response = {}
        groups = self.group.list_groups()
        for group in groups:
            group_id = group["uid"]
            group_stats = self._get_group_stats(group_id)
            response[group_id] = {
                "group_completion_count": group_stats["group_completion_count"],
                "group_completion_count_per_reading": group_stats["group_completion_count_per_reading"],
                "sent_count": 0,
                "sent_count_per_reading": {}
            }
        sent_count = self.get_sent_count_all()
        for sent_date in sent_count["groups"].keys():
            for group_id in sent_count["groups"][sent_date].keys():
                current_count = sent_count["groups"][sent_date][group_id]
                response[group_id]["sent_count"] += current_count
                response[group_id]["sent_count_per_reading"][sent_date] = current_count
        return response

    # reading
    def get_sent_count_all(self):
        readings = self.reading.list_readings()
        today = datetime.datetime.now().date()
        response = {}
        for reading in readings:
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
