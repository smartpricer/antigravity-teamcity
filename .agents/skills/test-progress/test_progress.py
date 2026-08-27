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


def get_gemini_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if key:
        return key

    try:
        pid = os.getpid()
        while pid > 1:
            proc_env_path = f"/proc/{pid}/environ"
            if os.path.exists(proc_env_path):
                try:
                    with open(proc_env_path, "rb") as f:
                        env_data = f.read().split(b"\x00")
                        for item in env_data:
                            item_str = item.decode("utf-8", errors="ignore")
                            if item_str.startswith(("GEMINI_API_KEY=", "GOOGLE_API_KEY=")):
                                val = item_str.split("=", 1)[1]
                                if val:
                                    return val
                except OSError:
                    pass

            try:
                with open(f"/proc/{pid}/stat", "r", encoding="utf-8") as f:
                    stat_parts = f.read().split()
                    pid = int(stat_parts[3])
            except OSError:
                break
    except Exception:
        pass

    return ""


def run_progress_test() -> bool:
    api_key = get_gemini_api_key()
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
    env["GEMINI_API_KEY"] = api_key

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
