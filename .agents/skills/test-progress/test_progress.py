#!/usr/bin/env python3
"""TeamCity Progress Reporting Test Script for prompt.sh.

Executes a 3-step test scenario with TEAMCITY_VERSION=1 environment variable
and verifies that progress is reported for those steps via tc_set_progress_message
(emitting ##teamcity[progressMessage '...']).
"""

import os
import re
import subprocess
import sys
import time


def run_progress_test() -> bool:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        return False

    script_path = "./prompt.sh"
    if not os.path.exists(script_path):
        print(f"Error: {script_path} not found in current directory.", file=sys.stderr)
        return False

    prompt = (
        "Execute a 3-step build scenario: "
        "Step 1: Initialize workspace configuration. "
        "Step 2: Run compilation and checks. "
        "Step 3: Package final artifacts. "
    )

    print("--- Running TeamCity Progress Reporting Test (TEAMCITY_VERSION=1) ---")
    start_time = time.time()

    env = os.environ.copy()
    env["TEAMCITY_VERSION"] = "1"

    proc = subprocess.Popen(
        [script_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0,
        env=env,
    )

    if proc.stdin:
        proc.stdin.write(prompt)
        proc.stdin.close()

    output_chunks = []
    while True:
        if proc.stdout is None:
            break
        chunk = proc.stdout.read(1024)
        if not chunk:
            break
        output_chunks.append(chunk)
        sys.stdout.write(chunk)
        sys.stdout.flush()

    proc.wait()
    stderr_data = proc.stderr.read() if proc.stderr else ""
    duration = time.time() - start_time

    full_output = "".join(output_chunks)

    if proc.returncode != 0:
        print(f"\nExecution failed with code {proc.returncode}: {stderr_data}", file=sys.stderr)
        return False

    # Extract all ##teamcity[progressMessage '...'] service messages
    progress_pattern = re.compile(r"##teamcity\[progressMessage\s+'([^']+)'\]")
    progress_matches = progress_pattern.findall(full_output)

    print("\n\n--- Progress Reporting Test Metrics ---")
    print(f"Execution duration: {duration:.2f}s")
    print(f"Progress messages captured ({len(progress_matches)}):")
    for i, msg in enumerate(progress_matches, 1):
        print(f"  {i}. {msg}")

    if len(progress_matches) >= 3:
        print("RESULT: PASS (At least 3 distinct progress messages were reported)")
        return True
    else:
        print(f"RESULT: FAIL (Expected at least 3 progress messages, got {len(progress_matches)})")
        return False


if __name__ == "__main__":
    success = run_progress_test()
    sys.exit(0 if success else 1)
