---
name: test-progress
description: Tests TeamCity progress reporting across a 3-step scenario using tc_set_progress_message with TEAMCITY_VERSION=1.
---

# Test Progress Skill

This skill validates that progress updates are emitted as TeamCity service messages (`##teamcity[progressMessage '...']`) during execution when `TEAMCITY_VERSION=1` is set.

## Instructions

1. Ensure `GEMINI_API_KEY` environment variable is exported.
2. Run the test script:
   ```bash
   python3 .agents/skills/test-progress/test_progress.py
   ```
3. The script will:
   - Execute `./prompt.sh` with `TEAMCITY_VERSION=1`.
   - Prompt the agent to run a 3-step scenario (Initialize workspace, Run compilation, Package artifacts) and report progress via `tc_set_progress_message` for each step.
   - Verify that at least 3 TeamCity progress service messages (`##teamcity[progressMessage '...']`) are captured in standard output.
