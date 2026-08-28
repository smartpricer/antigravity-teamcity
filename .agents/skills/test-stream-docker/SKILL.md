---
name: test-stream-docker
description: Tests and verifies real-time streaming of docker run execution output containing timestamps.
---

# Test Stream Docker Skill

This skill validates that execution output from a `docker run` command running an inner script streams out live with timestamps.

## Instructions

1. Ensure `GEMINI_API_KEY` environment variable is set and Docker is running.
2. Run the test script:
   ```bash
   python3 .agents/skills/test-stream-docker/test_stream_docker.py
   ```
3. The script will:
   - Command `./prompt.sh` to run `docker run --rm -v ... python:3.11-slim python3 .agents/skills/test-stream-docker/test_stream_docker_inner.py`.
   - Stream the output in real time.
   - Parse and compare the Docker container's inner execution timestamps `(...)` with the prompt runner's stream line timestamps `[...]`.
