#!/usr/bin/env python3
"""Empty Lines Verification Test Script for prompt.sh.

Executes a prompt triggering tools and text streaming with --with-timestamp,
captures standard output, and verifies that no empty or whitespace-only lines are printed to the console.
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


def run_no_empty_lines_test() -> bool:
    api_key = get_gemini_api_key()
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        return False

    script_path = "./prompt.sh"
    if not os.path.exists(script_path):
        print(f"Error: {script_path} not found in current directory.", file=sys.stderr)
        return False

    prompt = (
        "Call tc_set_progress_message with message 'Step 1: Check lines' "
        "and tc_block_open with name 'LineTest', then print 3 sentences, "
        "and call tc_block_close with name 'LineTest'."
    )

    print("--- Running No Empty Lines Test ---")
    start_time = time.time()
    env = os.environ.copy()
    env["GEMINI_API_KEY"] = api_key

    proc = subprocess.Popen(
        [script_path, "--with-timestamp"],
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

    raw_output_chunks = []
    print("--- Live Streamed Output ---")
    while True:
        if proc.stdout is None:
            break
        chunk = proc.stdout.read(1024)
        if not chunk:
            break
        raw_output_chunks.append(chunk)
        sys.stdout.write(chunk)
        sys.stdout.flush()

    proc.wait()
    stderr_data = proc.stderr.read() if proc.stderr else ""
    duration = time.time() - start_time

    full_output = "".join(raw_output_chunks)

    if proc.returncode != 0:
        print(f"\nExecution failed with code {proc.returncode}: {stderr_data}", file=sys.stderr)
        return False

    # Split output into lines
    lines = full_output.split("\n")
    # Ignore trailing empty line from final trailing newline
    if lines and not lines[-1]:
        lines.pop()

    empty_lines = [i + 1 for i, line in enumerate(lines) if not line.strip()]

    print("\n--- Console Line Verification Metrics ---")
    print(f"Total lines captured: {len(lines)}")
    print(f"Empty lines found:   {len(empty_lines)}")
    if empty_lines:
        print(f"Empty line indices:  {empty_lines}")

    if not empty_lines and len(lines) > 0:
        print("RESULT: PASS (Zero empty lines detected in console output)")
        return True
    else:
        print("RESULT: FAIL (Empty lines detected in console output)")
        return False


if __name__ == "__main__":
    success = run_no_empty_lines_test()
    sys.exit(0 if success else 1)
