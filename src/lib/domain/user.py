import json
import uuid
from lib.port.user import UserPort

class User:
    def __init__(self):
        self.port = UserPort()

    def list_users(self):
        response = self.port.list_users()
        return response

    def get_user(self, uid):
        response = self.port.get_user(uid)
        return response

    def get_user_with_description(self, description):
        response = self.port.get_user_with_description(description)
        return response

    def create_user(self, description, email, group_id):
        uid = str(uuid.uuid4())
        response = self.port.create_user(uid, description, email, group_id)
        return response

    def update_user(self, uid, description, email, group_id):
        response = self.port.update_user(uid, description, email, group_id)
        return response

    def delete_user(self, uid):
        response = self.port.delete_user(uid)
        return response
