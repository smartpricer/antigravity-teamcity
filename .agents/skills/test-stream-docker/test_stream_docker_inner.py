#!/usr/bin/env python3
"""Inner script executed inside Docker by prompt.py via run_command tool during test-stream-docker.

Prints start timestamp, timestamped counter steps, and end timestamp in normal brackets (...) with sleep delays
so lag can be evaluated for docker run commands.
"""

import datetime
import sys
import time


def main():
    start_ts = datetime.datetime.now().astimezone().isoformat()
    print(f"({start_ts}) Inner docker script starting...", flush=True)

    for i in range(1, 6):
        iso_ts = datetime.datetime.now().astimezone().isoformat()
        print(f"({iso_ts}) Inner docker counter step {i}", flush=True)
        time.sleep(0.4)

    end_ts = datetime.datetime.now().astimezone().isoformat()
    print(f"({end_ts}) Inner docker script finished.", flush=True)


if __name__ == "__main__":
    main()
