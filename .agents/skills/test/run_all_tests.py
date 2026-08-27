#!/usr/bin/env python3
"""Test Runner for all Agent Skills.

Discovers and runs test scripts across all skills in .agents/skills/.
Supports standard console output and emits TeamCity service messages when applicable.
"""

import glob
import os
import subprocess
import sys
import time


def escape_tc_string(val: object) -> str:
    if val is None:
        return ""
    s = str(val)
    s = s.replace("|", "||").replace("'", "|'").replace("\n", "|n").replace("\r", "|r").replace("[", "|[").replace("]", "|]")
    return s


def emit_tc(msg_type: str, **kwargs: object):
    attrs = [f"{k}='{escape_tc_string(v)}'" for k, v in kwargs.items() if v is not None]
    print(f"##teamcity[{msg_type} {' '.join(attrs)}]", flush=True)


def main() -> int:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    skills_dir = os.path.join(repo_root, ".agents", "skills")

    test_scripts = sorted(glob.glob(os.path.join(skills_dir, "test-*", "test_*.py")))

    if not test_scripts:
        print("No skill test scripts found under .agents/skills/test-*/", file=sys.stderr)
        return 0

    is_teamcity = bool(os.getenv("TEAMCITY_VERSION"))
    suite_name = "AgentSkillsTests"

    if is_teamcity:
        emit_tc("testSuiteStarted", name=suite_name)

    passed = 0
    failed = 0
    results = []

    print(f"Discovered {len(test_scripts)} skill test(s):\n")

    for script_path in test_scripts:
        rel_path = os.path.relpath(script_path, repo_root)
        test_name = os.path.basename(os.path.dirname(script_path))

        print(f"==> Running test skill: {test_name} ({rel_path})")
        if is_teamcity:
            emit_tc("testStarted", name=test_name, captureStandardOutput="true")

        start_time = time.time()
        proc = subprocess.run(
            [sys.executable, script_path],
            cwd=repo_root,
            capture_output=True,
            text=True,
            env=os.environ.copy()
        )
        duration_ms = int((time.time() - start_time) * 1000)

        if proc.stdout:
            print(proc.stdout)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)

        if proc.returncode == 0:
            passed += 1
            results.append((test_name, "PASSED", f"{duration_ms}ms"))
            if is_teamcity:
                emit_tc("testFinished", name=test_name, duration=str(duration_ms))
        else:
            failed += 1
            err_msg = f"Process returned exit code {proc.returncode}"
            results.append((test_name, "FAILED", f"{duration_ms}ms"))
            if is_teamcity:
                emit_tc("testFailed", name=test_name, message=err_msg, details=proc.stderr or proc.stdout)
                emit_tc("testFinished", name=test_name, duration=str(duration_ms))

    if is_teamcity:
        emit_tc("testSuiteFinished", name=suite_name)

    print("\n" + "=" * 50)
    print(f"Summary: {passed} passed, {failed} failed out of {len(test_scripts)} test(s)")
    for name, status, duration in results:
        print(f"  - {name}: {status} ({duration})")
    print("=" * 50)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
