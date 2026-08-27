---
name: test
description: Runs all test skills available in the repository (.agents/skills/test-*).
---

# Test Skill

This skill executes all repository test skills sequentially and summarizes their outcomes.

## Included Test Skills

Execute each of the following test skills in order:

1. **`test-progress`**: Validates TeamCity progress reporting across a 3-step build scenario (`TEAMCITY_VERSION=1`).
2. **`test-stream`**: Validates real-time token streaming to stdout.
3. **`test-uuid`**: Validates `uuid`, `uuid_v4`, and `uuid_v7` tool generation.
4. **`test-websearch`**: Validates live web search functionality.

## Instructions

1. Ensure the `GEMINI_API_KEY` environment variable is exported.
2. Activate and run each test skill listed above sequentially.
3. Collect the execution status and duration of each test.
4. Report a final summary table indicating pass/fail status for each test skill.
