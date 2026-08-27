---
name: test-uuid
description: Tests if the uuid, uuid_v4, and uuid_v7 tools generate valid UUID v4 and UUID v7 strings.
---

# Test UUID Skill

This skill verifies the functionality of the `uuid`, `uuid_v4`, and `uuid_v7` tools by prompting `./prompt.sh` to generate UUIDs and validating their format and versions.

## Instructions

1. Ensure `GEMINI_API_KEY` environment variable is set.
2. Run the test script:
   ```bash
   python3 .agents/skills/test-uuid/test_uuid.py
   ```
3. The script will:
   - Request UUID generation using `uuid`, `uuid_v4`, and `uuid_v7`.
   - Parse all generated UUIDs from stdout using regex.
   - Verify that at least one valid UUID v4 (version 4) and one valid UUID v7 (version 7) are present.
