import json
import uuid
from lib.port.group import GroupPort

class Group:
    def __init__(self):
        self.port = GroupPort()

    def list_groups(self):
        response = self.port.list_groups()
        return response

    def get_group(self, uid):
        response = self.port.get_group(uid)
        return response

    def get_group_with_description(self, description):
        response = self.port.get_group_with_description(description)
        return response

    def create_group(self, name):
        uid = str(uuid.uuid4())
        response = self.port.create_group(uid, name)
        response["Item"] = {
            "uid": uid
        }
        return response
    
    def delete_group(self, uid):
        response = self.port.delete_group(uid)
        return response
