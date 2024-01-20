import json
import uuid
from lib.domain.reading import Reading
from lib.domain.user import User
from lib.port.group import GroupPort

class Group:
    def __init__(self):
        self.port = GroupPort()
        self.reading_domain = Reading()
        self.user_domain = User()

    def list_groups(self):
        response = self.port.list_groups()
        return response

    def get_group(self, uid):
        response = self.port.get_group(uid)
        return response

    def get_group_by_description(self, description):
        response = self.port.get_group_by_description(description)
        return response

    def create_group(self, description, is_private=False):
        uid = str(uuid.uuid4())
        response = self.port.create_group(uid, description, is_private)
        return response

    def update_group(self, uid, description, is_private=False):
        response = self.port.update_group(uid, description, is_private)
        return response

    def delete_group(self, uid):
        response = self.port.delete_group(uid)
        return response

    def _get_group_stats(self, uid):
        response = {
            "group_id": uid,
            "group_completion_count": 0,
            "group_completion_count_per_reading": {}
        }
        users = self.user_domain.list_users_by_group(uid)
        for user in users:
            user_stats = self.user_domain.get_user_stats(user["uid"])
            response["group_completion_count"] += user_stats["user_completion_count"]
            for completion in user_stats["user_completion_timestamps"]:
                if completion["sent_date"] in response["group_completion_count_per_reading"]:
                    response["group_completion_count_per_reading"][completion["sent_date"]] += 1
                else:
                    response["group_completion_count_per_reading"][completion["sent_date"]] = 1
        return response

    def get_group_stats(self):
        response = {}
        groups = self.list_groups()
        for group in groups:
            group_stats = self._get_group_stats(group["uid"])
            response[group_stats["group_id"]] = {
                "group_completion_count": group_stats["group_completion_count"],
                "group_completion_count_per_reading": group_stats["group_completion_count_per_reading"]
            }
        sent_count = self.reading_domain.get_current_sent_count()
        for group_id in sent_count.keys():
            if group_id in response:
                response[group_id]["sent_count"] = sent_count[group_id]
            else:
                response[group_id] = {"sent_count": sent_count[group_id]}
        return response