---
name: test
description: Runs all test skills available in the repository (.agents/skills/test-*).
---

# Test Skill

Discovers and executes all test skills located under `.agents/skills/test-*` (such as `test-stream`).

## Instructions

1. Ensure the `GEMINI_API_KEY` environment variable is exported.
2. Run the test runner script:
   ```bash
   python3 .agents/skills/test/run_all_tests.py
   ```
3. The script will:
   - Discover all test scripts matching `.agents/skills/test-*/test_*.py`.
   - Execute each test sequentially against `./prompt.sh`.
   - Emit TeamCity test reporting messages (`##teamcity[testStarted ...]`, `##teamcity[testFinished ...]`) if running within a TeamCity build agent.
   - Display a summary of all test results with pass/fail counts and timing.
