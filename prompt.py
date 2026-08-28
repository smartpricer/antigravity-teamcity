#!/usr/bin/env python3
"""TeamCity Prompt Runner using Google Antigravity SDK.

This script executes prompts non-interactively within a TeamCity build step,
providing specialized TeamCity service message tools and clean, uncolored output.
"""

import asyncio
import os
import sys
import time
import uuid as _uuid_module

from google.antigravity import Agent, CapabilitiesConfig, LocalAgentConfig
from google.antigravity import policy
from google.antigravity.types import (
    GeminiAPIEndpoint,
    GeminiModelOptions,
    ModelTarget,
    ModelType,
    ThinkingLevel,
)


def escape_tc_string(val: object) -> str:
    """Escapes special characters according to TeamCity service message specifications.

    Escape rules:
      '  -> |'
      \n -> |n
      \r -> |r
      |  -> ||
      [  -> |[
      ]  -> |]
    """
    if val is None:
        return ""
    s = str(val)
    s = s.replace("|", "||")
    s = s.replace("'", "|'")
    s = s.replace("\n", "|n")
    s = s.replace("\r", "|r")
    s = s.replace("[", "|[")
    s = s.replace("]", "|]")
    return s


def emit_tc_service_message(message_type: str, single_value: str | None = None, **kwargs: object) -> str:
    """Formats and emits a TeamCity service message to stdout."""
    if single_value is not None:
        msg = f"##teamcity[{message_type} '{escape_tc_string(single_value)}']"
    else:
        attrs: list[str] = []
        for k, v in kwargs.items():
            if v is not None:
                attrs.append(f"{k}='{escape_tc_string(v)}'")
        msg = f"##teamcity[{message_type} {' '.join(attrs)}]"

    print(msg, file=sys.stdout, flush=True)
    return msg


# --- TeamCity Tools ---

def tc_log_message(text: str, status: str = "NORMAL", error_details: str | None = None) -> str:
    """Logs a message to the TeamCity build log with an optional status level and error details.

    Args:
        text: The message text to display in the build log.
        status: Message status level. Allowed values: 'NORMAL', 'WARNING', 'FAILURE', 'ERROR'.
        error_details: Optional error details or stack trace for FAILURE/ERROR messages.
    """
    msg = emit_tc_service_message("message", text=text, status=status, errorDetails=error_details)
    return f"Logged TeamCity message: {msg}"


def tc_block_open(name: str, description: str = "") -> str:
    """Opens a collapsible log block in the TeamCity build log.

    Args:
        name: The name/title of the log block.
        description: Optional additional description for the block.
    """
    kwargs = {"name": name}
    if description:
        kwargs["description"] = description
    msg = emit_tc_service_message("blockOpened", **kwargs)
    return f"Opened TeamCity log block: {msg}"


def tc_block_close(name: str) -> str:
    """Closes a previously opened collapsible log block in the TeamCity build log.

    Args:
        name: The name of the log block to close (must match the blockOpened name).
    """
    msg = emit_tc_service_message("blockClosed", name=name)
    return f"Closed TeamCity log block: {msg}"


def tc_set_parameter(name: str, value: str) -> str:
    """Sets a TeamCity build parameter, configuration parameter, or environment variable for subsequent steps.

    Prefixes:
      - 'env.VAR_NAME' sets an environment variable.
      - 'system.PROPERTY_NAME' sets a system property.
      - 'PARAM_NAME' sets a build configuration parameter.

    Args:
        name: Name of the parameter (e.g. 'env.DEPLOY_TARGET', 'app.version').
        value: Value to assign to the parameter.
    """
    msg = emit_tc_service_message("setParameter", name=name, value=value)
    return f"Set TeamCity parameter: {msg}"


def tc_set_build_status(status: str = "SUCCESS", text: str = "") -> str:
    """Sets or modifies the build status and status text in TeamCity.

    Args:
        status: The build status, either 'SUCCESS' or 'FAILURE'.
        text: Custom status text. You can use '{build.status.text}' to append or prepend to existing text.
    """
    kwargs = {"status": status}
    if text:
        kwargs["text"] = text
    msg = emit_tc_service_message("buildStatus", **kwargs)
    return f"Updated TeamCity build status: {msg}"


def tc_report_build_problem(description: str, identity: str = "") -> str:
    """Reports a build problem, marking the build as failed and displaying the issue prominently.

    Args:
        description: A human-readable description of the build problem.
        identity: Unique identity string for this problem (used for grouping/investigation in TeamCity).
    """
    kwargs = {"description": description}
    if identity:
        kwargs["identity"] = identity
    msg = emit_tc_service_message("buildProblem", **kwargs)
    return f"Reported TeamCity build problem: {msg}"


def tc_publish_artifacts(path: str) -> str:
    """Publishes artifacts from the build runner immediately while the build is running.

    Args:
        path: Path rules for artifacts (e.g., 'target/*.jar', 'logs => logs.zip', 'reports => reports').
    """
    msg = emit_tc_service_message("publishArtifacts", single_value=path)
    return f"Published TeamCity artifacts: {msg}"


def tc_set_build_number(build_number: str) -> str:
    """Updates the build number of the current running build.

    Args:
        build_number: New build number format or string (e.g. '1.0.42-release').
    """
    msg = emit_tc_service_message("buildNumber", single_value=build_number)
    return f"Updated TeamCity build number: {msg}"


def tc_set_progress_message(message: str) -> str:
    """Sets the current progress message displayed in the TeamCity web UI.

    Args:
        message: Progress status message to display.
    """
    msg = emit_tc_service_message("progressMessage", single_value=message)
    return f"Updated TeamCity progress message: {msg}"


def tc_progress_start(message: str) -> str:
    """Starts a progress activity stage in the TeamCity web UI.

    Args:
        message: Name or description of the activity starting.
    """
    msg = emit_tc_service_message("progressStart", single_value=message)
    return f"Started TeamCity progress stage: {msg}"


def tc_progress_finish(message: str) -> str:
    """Finishes a progress activity stage in the TeamCity web UI.

    Args:
        message: Name or description of the activity finishing.
    """
    msg = emit_tc_service_message("progressFinish", single_value=message)
    return f"Finished TeamCity progress stage: {msg}"


def tc_report_build_statistic(key: str, value: float) -> str:
    """Reports a numeric build statistic metric to TeamCity for charting and trends.

    Args:
        key: The statistic key name (e.g., 'CodeCoverageL', 'ArtifactsSize', 'MyCustomMetric').
        value: Numeric value for the metric.
    """
    msg = emit_tc_service_message("buildStatisticValue", key=key, value=str(value))
    return f"Reported TeamCity build statistic: {msg}"


def tc_test_suite_start(name: str) -> str:
    """Reports the start of a test suite in TeamCity.

    Args:
        name: Name of the test suite.
    """
    msg = emit_tc_service_message("testSuiteStarted", name=name)
    return f"Started TeamCity test suite: {msg}"


def tc_test_suite_finish(name: str) -> str:
    """Reports the completion of a test suite in TeamCity.

    Args:
        name: Name of the test suite.
    """
    msg = emit_tc_service_message("testSuiteFinished", name=name)
    return f"Finished TeamCity test suite: {msg}"


def tc_test_start(name: str, capture_standard_output: bool = True) -> str:
    """Reports that an individual test has started.

    Args:
        name: Full test name including namespace/class.
        capture_standard_output: Whether stdout/stderr from this test should be captured by TeamCity.
    """
    msg = emit_tc_service_message("testStarted", name=name, captureStandardOutput="true" if capture_standard_output else "false")
    return f"Started TeamCity test: {msg}"


def tc_test_finish(name: str, duration_ms: int = 0) -> str:
    """Reports that an individual test has completed.

    Args:
        name: Full test name.
        duration_ms: Duration in milliseconds (optional).
    """
    kwargs = {"name": name}
    if duration_ms > 0:
        kwargs["duration"] = str(duration_ms)
    msg = emit_tc_service_message("testFinished", **kwargs)
    return f"Finished TeamCity test: {msg}"


def tc_test_failed(name: str, message: str = "", details: str = "") -> str:
    """Reports that a test has failed with failure message and stack trace.

    Args:
        name: Full test name.
        message: Failure message/summary.
        details: Full error details or stack trace.
    """
    kwargs = {"name": name}
    if message:
        kwargs["message"] = message
    if details:
        kwargs["details"] = details
    msg = emit_tc_service_message("testFailed", **kwargs)
    return f"Reported TeamCity test failure: {msg}"


def tc_test_ignored(name: str, message: str = "") -> str:
    """Reports that a test was skipped or ignored.

    Args:
        name: Full test name.
        message: Optional reason why the test was ignored.
    """
    kwargs = {"name": name}
    if message:
        kwargs["message"] = message
    msg = emit_tc_service_message("testIgnored", **kwargs)
    return f"Reported TeamCity test ignored: {msg}"


def tc_test_output(name: str, stdout: str | None = None, stderr: str | None = None) -> str:
    """Attaches standard output or standard error to a specific test.

    Args:
        name: Full test name.
        stdout: Standard output text from the test.
        stderr: Standard error text from the test.
    """
    res: list[str] = []
    if stdout:
        res.append(emit_tc_service_message("testStdOut", name=name, out=stdout))
    if stderr:
        res.append(emit_tc_service_message("testStdErr", name=name, out=stderr))
    return f"Emitted test output for {name}: {', '.join(res)}"


def tc_import_data(data_type: str, path: str) -> str:
    """Instructs TeamCity to import and parse report data (e.g. test results or code inspection).

    Args:
        data_type: Report type (e.g., 'junit', 'surefire', 'nunit', 'mstest', 'vstest', 'checkstyle', 'pmd', 'findBugs', 'dotNetCoverage').
        path: Path to report file or directory (ant-style wildcards supported, e.g. 'build/test-results/**/*.xml').
    """
    msg = emit_tc_service_message("importData", type=data_type, path=path)
    return f"Configured TeamCity data import: {msg}"


def tc_compilation_start(compiler: str) -> str:
    """Reports the start of a compilation step.

    Args:
        compiler: Name of the compiler or compilation tool.
    """
    msg = emit_tc_service_message("compilationStarted", compiler=compiler)
    return f"Started compilation block: {msg}"


def tc_compilation_finish(compiler: str) -> str:
    """Reports the completion of a compilation step.

    Args:
        compiler: Name of the compiler or compilation tool.
    """
    msg = emit_tc_service_message("compilationFinished", compiler=compiler)
    return f"Finished compilation block: {msg}"


def tc_get_build_env() -> dict[str, str]:
    """Retrieves standard TeamCity environment variables and build properties.

    Returns:
        Dictionary of known TeamCity environment variables and their current values.
    """
    tc_keys = [
        "TEAMCITY_VERSION",
        "BUILD_NUMBER",
        "BUILD_VCS_NUMBER",
        "TEAMCITY_BUILDCONF_NAME",
        "TEAMCITY_PROJECT_NAME",
        "TEAMCITY_BUILD_PROPERTIES_FILE",
        "TEAMCITY_BUILD_CHECKOUTDIR",
        "SERVER_URL",
    ]
    env_info = {}
    for key in tc_keys:
        val = os.getenv(key)
        if val is not None:
            env_info[key] = val

    # Include any additional env variables starting with TEAMCITY_ or BUILD_
    for k, v in os.environ.items():
        if k.startswith(("TEAMCITY_", "BUILD_")) and k not in env_info:
            env_info[k] = v

    return env_info


def uuid_v4() -> str:
    """Generates and returns a random UUID v4 string."""
    return str(_uuid_module.uuid4())


def uuid() -> str:
    """Generates and returns a random UUID v4 string (alias for uuid_v4)."""
    return uuid_v4()


def uuid_v7() -> str:
    """Generates and returns a time-ordered UUID v7 string according to RFC 9562."""
    timestamp_ms = int(time.time() * 1000)
    rand_a = int.from_bytes(os.urandom(2), "big") & 0x0FFF
    rand_b = int.from_bytes(os.urandom(8), "big") & 0x3FFFFFFFFFFFFFFF
    val = (timestamp_ms << 80) | (0x7 << 76) | (rand_a << 64) | (0x2 << 62) | rand_b
    return str(_uuid_module.UUID(int=val))


TEAMCITY_TOOLS = [
    tc_log_message,
    tc_block_open,
    tc_block_close,
    tc_set_parameter,
    tc_set_build_status,
    tc_report_build_problem,
    tc_publish_artifacts,
    tc_set_build_number,
    tc_set_progress_message,
    tc_progress_start,
    tc_progress_finish,
    tc_report_build_statistic,
    tc_test_suite_start,
    tc_test_suite_finish,
    tc_test_start,
    tc_test_finish,
    tc_test_failed,
    tc_test_ignored,
    tc_test_output,
    tc_import_data,
    tc_compilation_start,
    tc_compilation_finish,
    tc_get_build_env,
    uuid,
    uuid_v4,
    uuid_v7,
]


def get_gemini_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if key:
        return key

    try:
        pid = os.getpid()
        while pid > 1:
            proc_env_path = f"/proc/{pid}/environ"
            if os.path.exists(proc_env_path):
                try:
                    with open(proc_env_path, "rb") as f:
                        env_data = f.read().split(b"\x00")
                        for item in env_data:
                            item_str = item.decode("utf-8", errors="ignore")
                            if item_str.startswith(("GEMINI_API_KEY=", "GOOGLE_API_KEY=")):
                                val = item_str.split("=", 1)[1]
                                if val:
                                    return val
                except OSError:
                    pass

            try:
                with open(f"/proc/{pid}/stat", "r", encoding="utf-8") as f:
                    stat_parts = f.read().split()
                    pid = int(stat_parts[3])
            except OSError:
                break
    except Exception:
        pass

    return ""


async def main():
    # Read prompt from stdin
    prompt = sys.stdin.read().strip()

    # Fallback to command-line arguments or environment variables if stdin was empty
    if not prompt:
        if len(sys.argv) > 1:
            prompt = " ".join(sys.argv[1:]).strip()
        else:
            prompt = os.getenv("GEMINI_PROMPT", os.getenv("PROMPT", "")).strip()

    if not prompt:
        print("Error: No prompt provided. Provide prompt via stdin, arguments, or GEMINI_PROMPT.", file=sys.stderr)
        sys.exit(1)

    model_name = os.getenv("GEMINI_MODEL", os.getenv("ANTIGRAVITY_MODEL", "gemini-2.5-flash"))
    api_key = get_gemini_api_key()

    effort_str = os.getenv("GEMINI_EFFORT", "medium").lower().strip()
    effort_map = {
        "minimal": ThinkingLevel.MINIMAL,
        "low": ThinkingLevel.LOW,
        "medium": ThinkingLevel.MEDIUM,
        "high": ThinkingLevel.HIGH,
        "extra_high": ThinkingLevel.EXTRA_HIGH,
        "extra-high": ThinkingLevel.EXTRA_HIGH,
    }
    thinking_level = effort_map.get(effort_str, ThinkingLevel.MEDIUM)

    # Gemini 2.5 / 1.5 / 2.0 models do not support thinking_level in API options
    supports_thinking = not any(v in model_name for v in ("2.5", "1.5", "2.0"))

    checkout_dir = os.getenv("TEAMCITY_BUILD_CHECKOUTDIR", os.getcwd())
    workspaces = [checkout_dir]

    system_instructions = """You are an AI assistant executing tasks inside a TeamCity CI/CD build server.
You have access to tools for interacting directly with the TeamCity build runner via TeamCity service messages.
Use these tools to:
- Open and close log blocks (`tc_block_open`, `tc_block_close`) to group related output.
- Set build status or report problems (`tc_set_build_status`, `tc_report_build_problem`).
- Report progress and log messages (`tc_set_progress_message`, `tc_log_message`).
- Set build parameters or environment variables for subsequent steps (`tc_set_parameter`).
- Publish build artifacts when generated (`tc_publish_artifacts`).
- Report test execution and results (`tc_test_start`, `tc_test_finish`, `tc_test_failed`, `tc_test_ignored`).
- Report compilation blocks and build statistics (`tc_compilation_start`, `tc_report_build_statistic`).

On a regular basis report your progress using the `tc_set_progress_message` tool.

Output plain text directly without interactive formatting or ANSI color codes.
"""

    context_files = ["AGENTS.md", "GEMINI.md", "CLAUDE.md", "README.md", "TEAMCITY.md"]
    context_contents: list[str] = []
    for cf in context_files:
        full_path = os.path.join(checkout_dir, cf)
        if os.path.exists(full_path):
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    context_contents.append(f"--- {cf} ---\n{content}\n")
            except OSError:
                pass

    if context_contents:
        system_instructions += "\n\nWorkspace Context:\n" + "\n".join(context_contents)

    models: list[ModelTarget] | None = None
    if supports_thinking:
        models = [
            ModelTarget(
                name=model_name,
                types=[ModelType.TEXT],
                endpoint=GeminiAPIEndpoint(
                    api_key=api_key if api_key else None,
                    options=GeminiModelOptions(thinking_level=thinking_level),
                ),
            )
        ]

    config = LocalAgentConfig(
        model=model_name,
        models=models,
        api_key=api_key,
        capabilities=CapabilitiesConfig(),
        policies=[policy.allow_all()],
        tools=TEAMCITY_TOOLS,
        system_instructions=system_instructions,
        workspaces=workspaces,
    )

    async with Agent(config) as agent:
        response = await agent.chat(prompt)
        async for token in response:
            sys.stdout.write(token)
            sys.stdout.flush()
        print()


def main_cli():
    asyncio.run(main())


if __name__ == "__main__":
    main_cli()
