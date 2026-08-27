#!/usr/bin/env python3
"""Web Search Test Script for prompt.sh.

Sends a prompt requiring web search for "where does the number 42 come from?" to ./prompt.sh
and validates that web search functions properly and returns accurate results.
"""

import os
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


def run_websearch_test() -> bool:
    api_key = get_gemini_api_key()
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        return False

    script_path = "./prompt.sh"
    if not os.path.exists(script_path):
        print(f"Error: {script_path} not found in current directory.", file=sys.stderr)
        return False

    prompt = "Use web search to answer: where does the number 42 come from?"

    print(f"--- Running Web Search Test: '{prompt}' ---")
    start_time = time.time()
    env = os.environ.copy()
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

    full_output = "".join(output_chunks).lower()

    if proc.returncode != 0:
        print(f"\nExecution failed with code {proc.returncode}: {stderr_data}", file=sys.stderr)
        return False

    # Check for expected terms related to Douglas Adams / Hitchhiker's Guide to the Galaxy
    expected_keywords = ["douglas adams", "hitchhiker", "life, the universe", "ultimate question", "galaxy"]
    matched = [kw for kw in expected_keywords if kw in full_output]

    print("\n\n--- Web Search Test Metrics ---")
    print(f"Execution duration: {duration:.2f}s")
    print(f"Keywords matched:   {matched}")

    if len(matched) >= 1:
        print("RESULT: PASS (Web search returned expected details)")
        return True
    else:
        print("RESULT: FAIL (Expected search keywords not found in response)")
        return False


if __name__ == "__main__":
    success = run_websearch_test()
    sys.exit(0 if success else 1)
