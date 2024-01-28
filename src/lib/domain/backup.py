import json
import uuid
from lib.port.backup import BackupPort

class Backup:
    def __init__(self):
        self.port = BackupPort()

    def backup(self):
        response = self.port.backup()
        return response