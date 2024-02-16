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
        self.users = self.user.list_users()
        self.groups = self.group.list_groups()
        self.readings = self.reading.list_readings_until_today()
        self.sent_count = self.get_reading_sent_count()

    # helper
    def _format_isoformatted_date(self, isoformatted):
        return str(datetime.datetime.fromisoformat(isoformatted).date())

    def _list_users_by_group(self, group_id):
        response = []
        for user in self.users:
            if group_id in user["group_ids"]:
                response.append(user)
        return response

    def _list_readings_by_user(self, user_id):
        response = []
        for reading in self.readings:
            if user_id in reading["read_by"]:
                response.append(reading)
        return response

    # user
    def get_user_stats(self, user_id):
        readings = self._list_readings_by_user(user_id)
        completions = {}
        for reading in readings:
            sent_date = self._format_isoformatted_date(reading["sent_date"])
            if "read_by" in reading:
                read_by = json.loads(reading["read_by"])
                if user_id in read_by:
                    completions[sent_date] = read_by[user_id]
        sent_dates = []
        for sent_date in self.sent_count["users"].keys():
            if user_id in self.sent_count["users"][sent_date]:
                sent_dates.append(sent_date)
        response = {
            "user_id": user_id,
            "user_completion_count": len(readings),
            "user_completion_per_reading": completions,
            "sent_count": len(sent_dates),
            "sent_dates": sent_dates
        }
        return response

    # group
    def _get_group_stats(self, group_id):
        response = {
            "group_id": group_id,
            "group_completion_count": 0,
            "group_completion_count_per_reading": {}
        }
        users = self._list_users_by_group(group_id)
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
        for group in self.groups:
            group_id = group["uid"]
            group_stats = self._get_group_stats(group_id)
            response[group_id] = {
                "group_completion_count": group_stats["group_completion_count"],
                "group_completion_count_per_reading": group_stats["group_completion_count_per_reading"],
                "sent_count": 0,
                "sent_count_per_reading": {}
            }
        for sent_date in self.sent_count["groups"].keys():
            for group_id in self.sent_count["groups"][sent_date].keys():
                current_count = self.sent_count["groups"][sent_date][group_id]
                response[group_id]["sent_count"] += current_count
                response[group_id]["sent_count_per_reading"][sent_date] = current_count
        return response

    # reading
    def get_reading_sent_count(self):
        response = {}
        for reading in self.readings:
            date_key = self._format_isoformatted_date(reading["sent_date"])
            if "sent_count" in reading:
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
