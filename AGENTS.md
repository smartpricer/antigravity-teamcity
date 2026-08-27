# Antigravity TeamCity Agent Instructions

This repository provides a non-interactive AI prompt runner powered by the **Google Antigravity SDK** specifically configured for execution inside **TeamCity CI/CD build agents**.

---

## Project Structure

```
├── .agents/
│   └── skills/
│       ├── test/            # Skill listing all repository test skills
│       │   └── SKILL.md
│       └── test-stream/     # Skill to test token streaming output
│           ├── SKILL.md
│           └── test_stream.py
├── .gitignore               # Ignores .venv, cache, and state files
├── AGENTS.md                # Agent reference guide (this file)
├── prompt.py                # Core Python script with Antigravity SDK & TeamCity tools
├── prompt.sh                # Shell entrypoint (manages .venv and executes prompt.py)
└── requirements.txt         # Pinned Python package dependencies
```

---

## Core Components

### 1. `prompt.py`
- Reads prompts non-interactively from `stdin` (or fallback to command arguments / `GEMINI_PROMPT`).
- Configures `LocalAgentConfig` with `policies=[policy.allow_all()]` for automated CI/CD execution.
- Emits clean, uncolored output directly to `stdout` with immediate streaming (`sys.stdout.flush()`).
- Provides native TeamCity service message tools with automatic character escaping (`|`, `'`, `\n`, `\r`, `[`, `]`).
- This script must not depend on any additional files (except `requirements.txt` and those packages installed from it)

### 2. `prompt.sh`
- Automates virtual environment management (`.venv`).
- Installs pinned dependencies from `requirements.txt`.
- Forwards `stdin` and arguments directly to `prompt.py`.

---

## TeamCity Tools Reference

The agent has access to the following built-in TeamCity tools:

| Tool Function | Service Message Emitted | Description |
|---|---|---|
| `tc_log_message(text, status, error_details)` | `##teamcity[message text='...' status='...']` | Logs a message to the build log (`NORMAL`, `WARNING`, `FAILURE`, `ERROR`). |
| `tc_block_open(name, description)` | `##teamcity[blockOpened name='...']` | Opens a collapsible log block. |
| `tc_block_close(name)` | `##teamcity[blockClosed name='...']` | Closes a collapsible log block. |
| `tc_set_parameter(name, value)` | `##teamcity[setParameter name='...' value='...']` | Sets build/environment parameters (`env.VAR`, `system.PROP`, or config params). |
| `tc_set_build_status(status, text)` | `##teamcity[buildStatus status='...' text='...']` | Sets build status (`SUCCESS`, `FAILURE`) and status text. |
| `tc_report_build_problem(description, identity)` | `##teamcity[buildProblem description='...']` | Marks build as failed with a prominent problem description. |
| `tc_publish_artifacts(path)` | `##teamcity[publishArtifacts '...']` | Publishes build artifacts during execution. |
| `tc_set_build_number(build_number)` | `##teamcity[buildNumber '...']` | Dynamically updates the current build number. |
| `tc_set_progress_message(message)` | `##teamcity[progressMessage '...']` | Updates the build progress message in TeamCity web UI. |
| `tc_progress_start(message)` | `##teamcity[progressStart '...']` | Starts a progress stage in the TeamCity UI. |
| `tc_progress_finish(message)` | `##teamcity[progressFinish '...']` | Finishes a progress stage in the TeamCity UI. |
| `tc_report_build_statistic(key, value)` | `##teamcity[buildStatisticValue key='...' value='...']` | Reports numeric metrics for TeamCity build graphs. |
| `tc_test_suite_start(name)` / `tc_test_suite_finish(name)` | `##teamcity[testSuiteStarted/Finished ...]` | Tracks test suite lifecycle. |
| `tc_test_start(name)` / `tc_test_finish(name, duration_ms)` | `##teamcity[testStarted/Finished ...]` | Tracks individual test execution. |
| `tc_test_failed(name, message, details)` | `##teamcity[testFailed ...]` | Reports test failure with error and stack trace. |
| `tc_test_ignored(name, message)` | `##teamcity[testIgnored ...]` | Reports skipped or ignored tests. |
| `tc_test_output(name, stdout, stderr)` | `##teamcity[testStdOut/testStdErr ...]` | Attaches test stdout/stderr. |
| `tc_import_data(data_type, path)` | `##teamcity[importData type='...' path='...']` | Imports external reports (JUnit, Checkstyle, etc.). |
| `tc_compilation_start(compiler)` / `tc_compilation_finish(compiler)` | `##teamcity[compilationStarted/Finished ...]` | Wraps compiler output in TeamCity compilation blocks. |
| `tc_get_build_env()` | *N/A (Inspection tool)* | Reads TeamCity environment variables and build properties. |
| `uuid()` / `uuid_v4()` | *N/A (Utility tool)* | Generates a random UUID v4 string. |
| `uuid_v7()` | *N/A (Utility tool)* | Generates a time-ordered RFC 9562 UUID v7 string. |

---

## Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | `""` | Google Gemini API Key. |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model name. |
| `GEMINI_EFFORT` | `medium` | Model reasoning/thinking effort (`minimal`, `low`, `medium`, `high`, `extra_high`). |
| `TEAMCITY_BUILD_CHECKOUTDIR` | `cwd` | Working directory for the build agent. |

---

## Development & Testing

### Running Prompts
```bash
echo "Summarize build health" | GEMINI_API_KEY=... ./prompt.sh
```

### Running Test Skills
Activate individual test skills (`test-progress`, `test-stream`, `test-uuid`, `test-websearch`) or activate the `test` skill to run all of them.
