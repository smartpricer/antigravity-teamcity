---
name: test-no-empty-lines
description: Tests and verifies that no empty lines are printed to the console output.
---

# Test No Empty Lines Skill

This skill validates that `./prompt.sh --with-timestamp` emits no blank/empty lines during tool calls or text generation.

## Instructions

1. Ensure `GEMINI_API_KEY` environment variable is exported.
2. Execute the test script:
   ```bash
   python3 .agents/skills/test-no-empty-lines/test_no_empty_lines.py
   ```
3. The script will:
   - Run `./prompt.sh --with-timestamp` with a prompt invoking tools and text output.
   - Capture standard output and split into lines.
   - Verify that `0` empty or whitespace-only lines are present in the output.
