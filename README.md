# Antigravity TeamCity Runner

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org)

An automated, non-interactive AI prompt runner powered by the **Google Antigravity SDK**, engineered specifically for execution inside **TeamCity CI/CD build agents**.

---

## Features

- 🤖 **Google Antigravity SDK Integration**: Automated execution using Gemini models (`gemini-2.5-flash`, `gemini-3.6-flash`, etc.).
- 🚀 **TeamCity Service Messages**: Built-in tools for logging blocks, status updates, parameters, artifacts, progress messages, and test reports.
- ⚡ **Real-Time Streaming**: Zero-lag, uncolored text token streaming directly to `stdout`.
- 🔑 **Flexible Environment Support**: Configuration via standard environment variables (`GEMINI_API_KEY`, `GEMINI_MODEL`, `GEMINI_EFFORT`).
- 🛠️ **Utility Tools**: Built-in random UUID v4 and time-ordered RFC 9562 UUID v7 generators.
- 🧪 **Comprehensive Skill Test Suite**: Built-in agent skills for validating progress, streaming, UUIDs, and web search.

---

## Quickstart

### Prerequisites
- Python 3.10+
- Google Gemini API Key (`GEMINI_API_KEY`)

### Basic Execution

You can run prompts non-interactively by piping text directly into `./prompt.sh`:

```bash
echo "Summarize build health and check workspace status" | GEMINI_API_KEY="your-api-key" ./prompt.sh
```

The runner automatically sets up a local virtual environment in `.venv/` and installs pinned dependencies on first execution.

---

## TeamCity Tools Reference

`prompt.py` provides native Python tools that emit properly formatted and escaped TeamCity service messages:

| Tool Function | Description | Service Message |
|---|---|---|
| `tc_log_message` | Logs a message to the build log (`NORMAL`, `WARNING`, `FAILURE`, `ERROR`). | `##teamcity[message ...]` |
| `tc_block_open` | Opens a collapsible log block in TeamCity. | `##teamcity[blockOpened ...]` |
| `tc_block_close` | Closes a collapsible log block in TeamCity. | `##teamcity[blockClosed ...]` |
| `tc_set_parameter` | Sets build/environment parameters (`env.*`, `system.*`, config params). | `##teamcity[setParameter ...]` |
| `tc_set_build_status` | Updates build status (`SUCCESS`, `FAILURE`) and status text. | `##teamcity[buildStatus ...]` |
| `tc_report_build_problem` | Marks build as failed with a prominent problem description. | `##teamcity[buildProblem ...]` |
| `tc_publish_artifacts` | Publishes build artifacts during execution. | `##teamcity[publishArtifacts ...]` |
| `tc_set_build_number` | Dynamically updates the current build number. | `##teamcity[buildNumber ...]` |
| `tc_set_progress_message` | Updates the build progress message in TeamCity web UI. | `##teamcity[progressMessage ...]` |
| `tc_progress_start` / `finish` | Starts and finishes progress stages in TeamCity UI. | `##teamcity[progressStart/Finish ...]` |
| `tc_report_build_statistic` | Reports numeric metrics for TeamCity build charts. | `##teamcity[buildStatisticValue ...]` |
| `tc_test_*` | Tracks test suites, tests, failures, ignored tests, and output. | `##teamcity[testStarted/Finished ...]` |
| `tc_import_data` | Imports external report files (JUnit, Checkstyle, etc.). | `##teamcity[importData ...]` |
| `tc_compilation_start` / `finish` | Wraps compilation output in TeamCity compilation blocks. | `##teamcity[compilationStarted/Finished]` |
| `tc_get_build_env` | Returns active TeamCity build properties and environment variables. | *N/A (Inspection tool)* |
| `uuid` / `uuid_v4` | Generates a random UUID v4 string. | *N/A (Utility tool)* |
| `uuid_v7` | Generates a time-ordered RFC 9562 UUID v7 string. | *N/A (Utility tool)* |

---

## Configuration

| Environment Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | `""` | Google Gemini API Key. |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model identifier. |
| `GEMINI_EFFORT` | `medium` | Model reasoning/thinking effort (`minimal`, `low`, `medium`, `high`, `extra_high`). |
| `TEAMCITY_BUILD_CHECKOUTDIR` | `cwd` | Checkout working directory for the build agent. |
| `TEAMCITY_VERSION` | *None* | Set by TeamCity build agents automatically. |

---

## Testing & Agent Skills

This repository includes agent skills under `.agents/skills/`:

| Skill | Path | Purpose |
|---|---|---|
| **`test`** | `.agents/skills/test/` | Discovers and executes all repository test skills. |
| **`test-progress`** | `.agents/skills/test-progress/` | Validates 3-step progress reporting (`tc_set_progress_message`). |
| **`test-stream`** | `.agents/skills/test-stream/` | Validates real-time token streaming output. |
| **`test-uuid`** | `.agents/skills/test-uuid/` | Validates `uuid`, `uuid_v4`, and `uuid_v7` generation. |
| **`test-websearch`** | `.agents/skills/test-websearch/` | Validates live web searching capabilities. |

Activate individual test skills (`test-progress`, `test-stream`, `test-uuid`, `test-websearch`) or activate the `test` skill to execute all test skills in the repository.

---

## GitHub Actions Integration

A GitHub Actions workflow is provided at `.github/workflows/test.yml` using `npx -y @google/gemini-cli`:

```yaml
      - name: Run Gemini CLI
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          GEMINI_MODEL: ${{ vars.GEMINI_MODEL }}
          GEMINI_CLI_TRUST_WORKSPACE: "true"
        run: |
          npx -y @google/gemini-cli -y -m "$GEMINI_MODEL" --prompt 'Activate the test skill to run all test skills and report status'
```

---

## License

This project is licensed under the [MIT License](LICENSE).
