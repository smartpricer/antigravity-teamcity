#!/usr/bin/env python3
"""Inner script executed by prompt.py via run_command tool during test-stream-tool.

Prints start timestamp, timestamped counter steps, and an end timestamp in normal brackets (...) with sleep delays
so lag can be evaluated between the outer and inner scripts.
"""

import datetime
import sys
import time


def main():
    start_ts = datetime.datetime.now().isoformat()
    print(f"({start_ts}) Inner script starting...", flush=True)

    for i in range(1, 6):
        iso_ts = datetime.datetime.now().isoformat()
        print(f"({iso_ts}) Inner counter step {i}", flush=True)
        time.sleep(0.4)

    end_ts = datetime.datetime.now().isoformat()
    print(f"({end_ts}) Inner script finished.", flush=True)


if __name__ == "__main__":
    main()
