"""
subscriber_typer.py
-------------------
Monitors the YouTube channel '1orzeroperfollower' every 1-2 minutes.
The log file always has exactly X digits where X = subscriber count.
On every change, bits are reshuffled randomly.

Requirements:
    pip install requests

YouTube Data API v3 key needed — replace YOUR_API_KEY_HERE below.
"""

import os
import random
import time
import requests
import subprocess

# ─── CONFIG ───────────────────────────────────────────────────────────────────

API_KEY = os.environ.get("YOUTUBE_API_KEY", "AIzaSyBuytdeEX04PBu_jeRbE8P26HXtyU96R1U")
CHANNEL_HANDLE = "1orzeroperfollower"
CHECK_INTERVAL_MIN = 60
CHECK_INTERVAL_MAX = 120
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "subscriber_log.txt")

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def read_bits():
    if not os.path.exists(LOG_FILE):
        return ""
    with open(LOG_FILE, "r") as f:
        return f.read().strip()

def write_bits(bits: str):
    with open(LOG_FILE, "w") as f:
        f.write(bits)

def shuffle_bits(bits: str) -> str:
    b = list(bits)
    random.shuffle(b)
    return "".join(b)

def open_notepad():
    subprocess.Popen(["notepad.exe", LOG_FILE])

def get_channel_id_from_handle(handle: str):
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {"part": "id", "forHandle": handle, "key": API_KEY}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    items = r.json().get("items", [])
    return items[0]["id"] if items else None

def get_subscriber_count(channel_id: str):
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {"part": "statistics", "id": channel_id, "key": API_KEY}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    items = r.json().get("items", [])
    if not items:
        return None
    count = items[0].get("statistics", {}).get("subscriberCount")
    return int(count) if count is not None else None

# ─── MAIN LOOP ────────────────────────────────────────────────────────────────

def main():
    if API_KEY == "YOUR_API_KEY_HERE":
        return

    channel_id = get_channel_id_from_handle(CHANNEL_HANDLE)
    if not channel_id:
        return

    previous_count = get_subscriber_count(channel_id)
    if previous_count is None:
        return

    # Initialize log file to match current subscriber count
    bits = read_bits()
    if len(bits) != previous_count:
        # Pad or trim to match current count
        if len(bits) < previous_count:
            bits += "".join([str(random.randint(0, 1)) for _ in range(previous_count - len(bits))])
        else:
            bits = bits[:previous_count]
        bits = shuffle_bits(bits)
        write_bits(bits)

    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "w").close()
    open_notepad()

    while True:
        wait = random.randint(CHECK_INTERVAL_MIN, CHECK_INTERVAL_MAX)
        time.sleep(wait)

        try:
            current_count = get_subscriber_count(channel_id)
        except Exception:
            continue

        if current_count is None:
            continue

        change = current_count - previous_count

        if change != 0:
            bits = read_bits()

            if change > 0:
                # Add new random bits for each new subscriber
                new_bits = "".join([str(random.randint(0, 1)) for _ in range(change)])
                bits = bits + new_bits
            elif change < 0:
                # Remove bits for lost subscribers
                remove = min(abs(change), len(bits))
                bits = bits[:-remove] if remove > 0 else bits

            # Always reshuffle after any change
            bits = shuffle_bits(bits)
            write_bits(bits)
            previous_count = current_count

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
