import json
from lib.util import log_event
from lib.domain.backup import Backup

def main():
    backup = Backup()
    response = backup.backup()
    print(json.dumps(response))

if __name__ == "__main__":
    main()