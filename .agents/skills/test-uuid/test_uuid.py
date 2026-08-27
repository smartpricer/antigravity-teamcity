#!/usr/bin/env python3
"""UUID Tools Test Script for prompt.sh.

Sends a prompt requiring invocation of uuid, uuid_v4, and uuid_v7 tools to ./prompt.sh
and validates that valid UUID v4 and UUID v7 strings are generated.
"""

import os
import re
import subprocess
import sys
import time
import uuid as _uuid_module


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


def run_uuid_test() -> bool:
    api_key = get_gemini_api_key()
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        return False

    script_path = "./prompt.sh"
    if not os.path.exists(script_path):
        print(f"Error: {script_path} not found in current directory.", file=sys.stderr)
        return False

    prompt = "Use the uuid tool, the uuid_v4 tool, and the uuid_v7 tool to generate UUIDs and output them clearly."

    print(f"--- Running UUID Tools Test ---")
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

    full_output = "".join(output_chunks)

    if proc.returncode != 0:
        print(f"\nExecution failed with code {proc.returncode}: {stderr_data}", file=sys.stderr)
        return False

    # Extract all UUID-like strings matching standard 8-4-4-4-12 pattern
    uuid_pattern = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
    found_uuids = uuid_pattern.findall(full_output)

    v4_found = []
    v7_found = []

    for raw_u in found_uuids:
        try:
            parsed = _uuid_module.UUID(raw_u)
            if parsed.version == 4:
                v4_found.append(raw_u)
            elif parsed.version == 7:
                v7_found.append(raw_u)
        except ValueError:
            pass

    print("\n\n--- UUID Tools Test Metrics ---")
    print(f"Execution duration: {duration:.2f}s")
    print(f"UUID v4 strings found ({len(v4_found)}): {v4_found}")
    print(f"UUID v7 strings found ({len(v7_found)}): {v7_found}")

    if v4_found and v7_found:
        print("RESULT: PASS (Successfully generated and verified valid UUID v4 and v7 strings)")
        return True
    else:
        print("RESULT: FAIL (Missing valid UUID v4 or UUID v7 in output)")
        return False


if __name__ == "__main__":
    success = run_uuid_test()
    sys.exit(0 if success else 1)
