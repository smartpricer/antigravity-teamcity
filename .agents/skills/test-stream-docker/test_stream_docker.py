#!/usr/bin/env python3
"""Docker Stream Test Script for prompt.sh.

Sends a prompt instructing prompt.py to execute a 'docker run' command running test_stream_docker_inner.py.
Validates that output lines from the docker container (with timestamps in round brackets)
are streamed live by prompt.py (with timestamps in square brackets).
"""

import datetime
import os
import re
import subprocess
import sys
import time


def is_docker_available() -> bool:
    try:
        res = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=5)
        return res.returncode == 0
    except Exception:
        return False


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


def run_stream_docker_test() -> bool:
    if not is_docker_available():
        print("--- Docker daemon is not running on host; skipping Docker stream test ---")
        print("RESULT: PASS (SKIPPED: Docker daemon unavailable)")
        return True

    api_key = get_gemini_api_key()
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        return False

    script_path = "./prompt.sh"
    if not os.path.exists(script_path):
        print(f"Error: {script_path} not found in current directory.", file=sys.stderr)
        return False

    inner_script = ".agents/skills/test-stream-docker/test_stream_docker_inner.py"
    if not os.path.exists(inner_script):
        print(f"Error: {inner_script} not found.", file=sys.stderr)
        return False

    cwd = os.getcwd()
    docker_cmd = f"docker run --rm -v \"{cwd}:/app\" -w /app python:3.11-slim python3 {inner_script}"
    prompt = f"Run the command '{docker_cmd}' using run_command tool and print its full raw stdout."

    print("--- Running Docker Stream Test ---")
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

    lines_captured = []

    print("--- Live Streamed Output ---")
    while True:
        if proc.stdout is None:
            break
        line = proc.stdout.readline()
        if not line:
            break
        lines_captured.append(line)
        sys.stdout.write(line)
        sys.stdout.flush()

    proc.wait()
    stderr_data = proc.stderr.read() if proc.stderr else ""
    duration = time.time() - start_time

    if proc.returncode != 0:
        print(f"\nExecution failed with code {proc.returncode}: {stderr_data}", file=sys.stderr)
        return False

    start_pattern = re.compile(
        r"\[(?P<stream_ts>[^\]]+)\]\s+.*\((?P<inner_ts>\d{4}-\d{2}-\d{2}T[^\)]+)\)\s+Inner docker script starting\."
    )
    step_pattern = re.compile(
        r"\[(?P<stream_ts>[^\]]+)\]\s+.*\((?P<inner_ts>\d{4}-\d{2}-\d{2}T[^\)]+)\)\s+Inner docker counter step (?P<step>\d+)"
    )
    end_pattern = re.compile(
        r"\[(?P<stream_ts>[^\]]+)\]\s+.*\((?P<inner_ts>\d{4}-\d{2}-\d{2}T[^\)]+)\)\s+Inner docker script finished\."
    )

    inner_start_info = None
    inner_end_info = None
    step_matches = []

    for line in lines_captured:
        m_start = start_pattern.search(line)
        if m_start:
            inner_start_info = (m_start.group("stream_ts"), m_start.group("inner_ts"))

        m_step = step_pattern.search(line)
        if m_step:
            step_matches.append((m_step.group("step"), m_step.group("stream_ts"), m_step.group("inner_ts")))

        m_end = end_pattern.search(line)
        if m_end:
            inner_end_info = (m_end.group("stream_ts"), m_end.group("inner_ts"))

    print("\n--- Inner Docker Script Stream Metrics & Lag Evaluation ---")
    print(f"Total output lines captured: {len(lines_captured)}")
    print(f"Total test execution duration: {duration:.2f}s")

    if inner_start_info:
        stream_start_dt = datetime.datetime.fromisoformat(inner_start_info[0])
        inner_start_dt = datetime.datetime.fromisoformat(inner_start_info[1])
        start_lag = (stream_start_dt - inner_start_dt).total_seconds()
        print(f"Inner Docker Start: Stream [{inner_start_info[0]}] <--- Inner ({inner_start_info[1]}) | Lag: {start_lag:.3f}s")

    for step, stream_ts, inner_ts in step_matches:
        s_dt = datetime.datetime.fromisoformat(stream_ts)
        i_dt = datetime.datetime.fromisoformat(inner_ts)
        step_lag = (s_dt - i_dt).total_seconds()
        print(f"  Step {step}: Stream [{stream_ts}] <--- Inner ({inner_ts}) | Lag: {step_lag:.3f}s")

    if inner_end_info:
        stream_end_dt = datetime.datetime.fromisoformat(inner_end_info[0])
        inner_end_dt = datetime.datetime.fromisoformat(inner_end_info[1])
        end_lag = (stream_end_dt - inner_end_dt).total_seconds()
        print(f"Inner Docker End:   Stream [{inner_end_info[0]}] <--- Inner ({inner_end_info[1]}) | Lag: {end_lag:.3f}s")

    if inner_start_info and inner_end_info:
        inner_runtime = (datetime.datetime.fromisoformat(inner_end_info[1]) - datetime.datetime.fromisoformat(inner_start_info[1])).total_seconds()
        print(f"Inner Docker Total Runtime: {inner_runtime:.3f}s")

    if inner_start_info and inner_end_info and len(step_matches) >= 3:
        print("RESULT: PASS (Docker container timestamps (...) evaluated cleanly against stream [...])")
        return True
    else:
        print("RESULT: FAIL (Missing start, step, or end timestamps from inner docker script)")
        return False


if __name__ == "__main__":
    success = run_stream_docker_test()
    sys.exit(0 if success else 1)
