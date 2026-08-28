---
name: test-stream-tool
description: Tests and verifies real-time streaming of tool calls (TeamCity service messages) and text.
---

# Test Stream Tool Skill

This skill validates that tool execution outputs (such as `##teamcity[progressMessage '...']`) stream directly to standard output in real-time when called during agent turns.

## Instructions

1. Ensure `GEMINI_API_KEY` environment variable is exported.
2. Run the test script:
   ```bash
   python3 .agents/skills/test-stream-tool/test_stream_tool.py
   ```
3. The script will:
   - Send prompt: `"Call tc_set_progress_message with message 'Step 1: Starting streaming test' and then print a list of numbers from 1 to 5, one per line."`
   - Capture streamed output chunk-by-chunk with timestamps.
   - Verify that the `##teamcity[progressMessage 'Step 1: Starting streaming test']` service message is emitted cleanly on stdout during tool execution.
