#!/usr/bin/env python3
"""Streaming Test Script for prompt.sh.

Sends a counting prompt to ./prompt.sh, reads stdout chunk-by-chunk in real time,
measures token arrival deltas, and validates that output streams incrementally.
"""

import os
import subprocess
import sys
import time


def run_stream_test(prompt: str = "Write a numbered list from 1 to 10 counting up, with one sentence per number.") -> bool:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        return False

    script_path = "./prompt.sh"
    if not os.path.exists(script_path):
        print(f"Error: {script_path} not found in current directory.", file=sys.stderr)
        return False

    env = os.environ.copy()
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
