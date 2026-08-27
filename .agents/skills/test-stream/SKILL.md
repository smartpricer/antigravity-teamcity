---
name: test-stream
description: Tests and verifies real-time token streaming from prompt.sh to standard output.
---

# Test Stream Skill

This skill runs a live streaming validation test against `./prompt.sh` in the repository, checking whether model generation outputs turn up incrementally chunk-by-chunk rather than arriving buffered all at once.

## Instructions

1. Ensure the `GEMINI_API_KEY` environment variable is available.
2. Run the streaming verification script:
   ```bash
   python3 .agents/skills/test-stream/test_stream.py
   ```
   Or supply a custom counting prompt:
   ```bash
   python3 .agents/skills/test-stream/test_stream.py "Count from 1 to 15 with a short explanation for each number"
   ```
3. Alternatively, test directly using an inline Python one-liner:
   ```bash
   python3 -c '
   import os, subprocess, sys, time
   proc = subprocess.Popen(["./prompt.sh"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=0)
   proc.stdin.write("Count from 1 to 10 slowly")
   proc.stdin.close()
   while True:
       c = proc.stdout.read(4)
       if not c: break
       sys.stdout.write(c)
       sys.stdout.flush()
   proc.wait()
   '
   ```
4. Verify from the metrics that:
   - Chunks arrive over an active stream duration (`> 0.1s`).
   - Output tokens display on the console incrementally in real time.
