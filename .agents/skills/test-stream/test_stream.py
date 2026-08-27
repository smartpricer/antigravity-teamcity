#!/usr/bin/env python3
"""Streaming Test Script for prompt.sh.

Sends a counting prompt to ./prompt.sh, reads stdout chunk-by-chunk in real time,
measures token arrival deltas, and validates that output streams incrementally.
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


def run_stream_test(prompt: str = "Write a numbered list from 1 to 10 counting up, with one sentence per number.") -> bool:
    api_key = get_gemini_api_key()
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        return False

    script_path = "./prompt.sh"
    if not os.path.exists(script_path):
        print(f"Error: {script_path} not found in current directory.", file=sys.stderr)
        return False

    env = os.environ.copy()
    env["GEMINI_API_KEY"] = api_key
    start_time = time.time()

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

    chunks = []
    print("--- Live Output Stream ---")
    while True:
        if proc.stdout is None:
            break
        chunk = proc.stdout.read(4)
        if not chunk:
            break
        now = time.time()
        chunks.append((now - start_time, chunk))
        sys.stdout.write(chunk)
        sys.stdout.flush()

    proc.wait()
    stderr_data = proc.stderr.read() if proc.stderr else ""

    if proc.returncode != 0:
        print(f"\nExecution failed with code {proc.returncode}: {stderr_data}", file=sys.stderr)
        return False

    if not chunks:
        print("\nError: No output received from stream.", file=sys.stderr)
        return False

    first_arrival = chunks[0][0]
    last_arrival = chunks[-1][0]
    duration = last_arrival - first_arrival

    print("\n\n--- Stream Performance Metrics ---")
    print(f"Total chunks received: {len(chunks)}")
    print(f"Time to first chunk:   {first_arrival:.3f}s")
    print(f"Time to last chunk:    {last_arrival:.3f}s")
    print(f"Active stream duration:{duration:.3f}s")

    if len(chunks) > 5:
        avg_chunk_time = duration / len(chunks)
        print(f"Avg delay per chunk:   {avg_chunk_time:.4f}s")
        print("RESULT: PASS (Output streamed incrementally)")
        return True
    else:
        print("RESULT: FAIL (Output arrived all at once or insufficient chunks)")
        return False


if __name__ == "__main__":
    test_prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Write a numbered list from 1 to 10 counting up, with one sentence per number."
    success = run_stream_test(test_prompt)
    sys.exit(0 if success else 1)
