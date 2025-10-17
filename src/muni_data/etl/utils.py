import sys
from datetime import datetime

def log_info(message):
    # print(f"[{datetime.utcnow().isoformat()}] {message}", file=sys.stdout)
    print("{}: {message}".format(datetime.now()))
