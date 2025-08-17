import requests
import os
import sys
from pathlib import Path

CALLBACK_URL = "http://localhost:8000/honeypot/tokens/callback"

def phone_home():
    token = Path(sys.argv[0]).stem
    try:
        requests.post(
            CALLBACK_URL,
            json={
                "token": token,
                "hostname": os.uname().nodename,
            },
            timeout=5
        )
    except Exception:
        pass

if __name__ == "__main__":
    phone_home()
