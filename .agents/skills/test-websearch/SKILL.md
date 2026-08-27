---
name: test-websearch
description: Tests if web search functionality is working by querying "where does the number 42 come from?".
---

# Test Web Search Skill

This skill tests whether the agent's web search capability (`search_web`) is functional by asking `./prompt.sh` to search for the origin of the number 42.

## Instructions

1. Ensure `GEMINI_API_KEY` environment variable is exported.
2. Execute the test script:
   ```bash
   python3 .agents/skills/test-websearch/test_websearch.py
   ```
3. The script will:
   - Send prompt: `"Use web search to answer: where does the number 42 come from?"`
   - Capture streamed output from `./prompt.sh`.
   - Validate that the response references Douglas Adams / *The Hitchhiker's Guide to the Galaxy*.
