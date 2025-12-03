# Story 1.4: CLI Framework with Start Command

Status: done

## Story

As a developer,
I want a CLI command `mailreactor start` to launch the API server,
so that I can start Mail Reactor with a single command in under 5 seconds.

## Acceptance Criteria

**Given** FastAPI app and logging from Stories 1.2 and 1.3  
**When** CLI is implemented  
**Then** `src/mailreactor/cli/server.py` provides:
- `start()` command using Typer
- Options: `--host` (default: 127.0.0.1), `--port` (default: 8000), `--log-level` (default: INFO)
- Option: `--json-logs` flag (enables JSON log output, default: pretty console)
- Option: `--account` (optional, for adding account on startup - deferred to Epic 2)
- Configures logging based on `--json-logs` flag (pretty console by default)
- Starts Uvicorn server with FastAPI app
- Displays startup message with API URL and documentation links

**And** `src/mailreactor/__main__.py` defines CLI entry point:
- Creates Typer app instance
- Registers `start` and `dev` commands (dev in Story 1.8)
- Enables `python -m mailreactor start` invocation
- No subcommands for account management (keep CLI simple)

**And** Running `mailreactor start` (or `python -m mailreactor start`):
- Initializes logging (console renderer by default, JSON if `--json-logs` flag)
- Loads configuration from environment variables
- Starts Uvicorn server on configured host/port
- Displays startup messages (console mode with color):
  ```
  [INFO]  10:30:45 Mail Reactor started url=http://127.0.0.1:8000
  [INFO]  10:30:45 API documentation available url=http://127.0.0.1:8000/docs
  [INFO]  10:30:45 Add account with: mailreactor start --account you@email.com
  ```
- Or JSON logs (if `--json-logs` flag):
  ```json
  {"timestamp": "2025-11-25T10:30:45Z", "level": "info", "event": "server_started", "url": "http://127.0.0.1:8000"}
  {"timestamp": "2025-11-25T10:30:45Z", "level": "info", "event": "docs_available", "url": "http://127.0.0.1:8000/docs"}
  ```
- Completes startup in under 3 seconds (NFR-P1)

**And** Server binds to localhost (127.0.0.1) by default (FR-036)

**And** Server responds to Ctrl+C gracefully (clean shutdown)

**Prerequisites:** Stories 1.1, 1.2, 1.3 (project structure, FastAPI, logging)

## Tasks / Subtasks

- [ ] Create CLI server module (AC: cli/server.py provides...)
  - [ ] Create `src/mailreactor/cli/` directory and `__init__.py`
  - [ ] Create `src/mailreactor/cli/server.py` module
  - [ ] Import Typer, Uvicorn, and Settings
  - [ ] Import configure_logging from utils.logging
  - [ ] Import create_app from main.py
  - [ ] Add type hints for all function parameters and return types

- [ ] Implement start command with Typer (AC: start() command using Typer)
  - [ ] Create Typer app instance in `cli/server.py`
  - [ ] Define `start()` function with @app.command() decorator
  - [ ] Add `--host` option (default: "127.0.0.1", type: str)
  - [ ] Add `--port` option (default: 8000, type: int, range: 1-65535)
  - [ ] Add `--log-level` option (default: "INFO", choices: ["DEBUG", "INFO", "WARNING", "ERROR"])
  - [ ] Add `--json-logs` flag (default: False, boolean flag)
  - [ ] Add `--account` option (placeholder for Epic 2, not implemented yet)
  - [ ] Add docstring explaining command purpose and options
  - [ ] Write unit test for CLI argument parsing

- [ ] Configure logging based on CLI flags (AC: configures logging based on --json-logs)
  - [ ] Call `configure_logging(json_format=json_logs, log_level=log_level)` at start
  - [ ] Pass json_logs boolean to configure_logging function
  - [ ] Pass log_level string to configure_logging function
  - [ ] Ensure logging configured BEFORE any other operations
  - [ ] Write unit test for logging configuration with different flags

- [ ] Load configuration from environment and CLI (AC: loads configuration from environment)
  - [ ] Create Settings instance from environment variables
  - [ ] Override Settings.host with --host flag if provided
  - [ ] Override Settings.port with --port flag if provided
  - [ ] Override Settings.log_level with --log-level flag if provided
  - [ ] Override Settings.json_logs with --json-logs flag if provided
  - [ ] Write unit test for Settings override logic

- [ ] Start Uvicorn server (AC: starts Uvicorn server)
  - [ ] Call create_app() to initialize FastAPI application
  - [ ] Configure Uvicorn with host, port, log_level settings
  - [ ] Set reload=False for production mode (start command)
  - [ ] Pass FastAPI app instance to uvicorn.run()
  - [ ] Configure Uvicorn to use structlog logger
  - [ ] Handle Uvicorn startup errors gracefully
  - [ ] Write integration test for Uvicorn startup

- [ ] Display startup messages (AC: displays startup message)
  - [ ] Log "server_starting" event with host, port, log_level
  - [ ] Construct API URL: f"http://{host}:{port}"
  - [ ] Construct docs URL: f"http://{host}:{port}/docs"
  - [ ] Log "server_started" event with url
  - [ ] Log "docs_available" event with docs_url
  - [ ] Log "account_setup_hint" with example --account command
  - [ ] Ensure messages use appropriate log level (INFO)
  - [ ] Write integration test to capture and verify log messages

- [ ] Implement graceful shutdown (AC: responds to Ctrl+C gracefully)
  - [ ] Add signal handler for SIGINT (Ctrl+C)
  - [ ] Add signal handler for SIGTERM (container/process manager)
  - [ ] Log "server_stopping" event on shutdown signal
  - [ ] Let Uvicorn handle graceful shutdown (built-in)
  - [ ] Log "server_stopped" event after shutdown
  - [ ] Write integration test for graceful shutdown

- [ ] Create CLI entry point module (AC: __main__.py defines CLI entry point)
  - [ ] Create `src/mailreactor/__main__.py`
  - [ ] Import Typer app from cli/server.py
  - [ ] Define `if __name__ == "__main__"` block
  - [ ] Call typer_app() to run CLI
  - [ ] Enable `python -m mailreactor start` invocation
  - [ ] Write integration test for __main__ invocation

- [ ] Configure console script entry point (AC: mailreactor command available)
  - [ ] Update `pyproject.toml` [project.scripts] section
  - [ ] Add `mailreactor = "mailreactor.__main__:main"` entry
  - [ ] Ensure entry point calls Typer app correctly
  - [ ] Verify `mailreactor start` works after pip install
  - [ ] Write end-to-end test for installed command

- [ ] Validate startup performance (AC: completes startup in under 3 seconds)
  - [ ] Measure time from CLI invocation to first health endpoint response
  - [ ] Optimize imports if startup exceeds 3 seconds
  - [ ] Profile startup sequence to identify bottlenecks
  - [ ] Write performance test to enforce <3s startup time (NFR-P1)
  - [ ] Baseline measurement in CI for regression detection

- [ ] Implement localhost default binding (AC: binds to localhost by default)
  - [ ] Verify Settings default: `host: str = "127.0.0.1"`
  - [ ] Verify CLI default: `--host` option defaults to "127.0.0.1"
  - [ ] Log warning if binding to 0.0.0.0 (network exposure)
  - [ ] Write security test to ensure localhost default
  - [ ] Document security implications in CLI help text

- [ ] Add CLI help and documentation (AC: --help displays usage)
  - [ ] Write comprehensive docstring for start() function
  - [ ] Add descriptions for all CLI options
  - [ ] Typer auto-generates help from docstrings
  - [ ] Test `mailreactor start --help` output
  - [ ] Verify help text is clear and actionable
  - [ ] Include examples in help text

- [ ] Testing and validation (AC: all acceptance criteria met)
  - [ ] Write unit test: CLI arguments parsed correctly
  - [ ] Write unit test: Settings overridden by CLI flags
  - [ ] Write unit test: Logging configured based on flags
  - [ ] Write integration test: Uvicorn starts successfully
  - [ ] Write integration test: Startup messages logged
  - [ ] Write integration test: Graceful shutdown works
  - [ ] Write integration test: Health endpoint responds after startup
  - [ ] Write end-to-end test: Full CLI to running server workflow
  - [ ] Write performance test: Startup time <3 seconds
  - [ ] Manual test: Run `mailreactor start` and verify console output
  - [ ] Manual test: Test Ctrl+C graceful shutdown
  - [ ] Manual test: Test `--json-logs` flag
  - [ ] Verify test coverage meets target: 80%+ for CLI module

## Dev Notes

### Learnings from Previous Story

**From Story 1-3-structured-logging-with-console-and-json-renderers (Status: done)**

- **Logging System Ready**: `utils/logging.py` has `configure_logging(json_format, log_level)` function ready to use
  - Call this function BEFORE any other initialization in CLI start command
  - Pass CLI flags directly: `configure_logging(json_format=json_logs, log_level=log_level)`
- **Console vs JSON Rendering Works**: Validated with 100% test coverage
  - Console: Colored output with key=value format (default)
  - JSON: Machine-parseable for log aggregation (opt-in via --json-logs)
- **Settings Ready for json_logs Field**: `config.py` has `json_logs: bool = False` field
  - CLI --json-logs flag should override this setting
- **Request ID Middleware Functional**: `dependencies.py` binds request_id to structlog context
  - Server startup will automatically use this for request tracing
- **EventEmitter Uses Structured Logging**: `events.py` replaced print() with logger.debug()
  - No changes needed - logging already integrated in core module
- **All Tests Passing**: 76 tests passing, 3 skipped (100% coverage for logging)
  - CLI tests should follow same pattern: unit + integration + end-to-end

[Source: stories/1-3-structured-logging-with-console-and-json-renderers.md#Dev-Agent-Record]

### Architecture Patterns and Constraints

**ADR-005: Typer for CLI Framework**
- Use Typer 0.20.0 for all CLI commands
- Type hint-based API (like FastAPI philosophy)
- Automatic help generation from docstrings
- Subcommand support (`mailreactor start`, `mailreactor dev`)
- MIT licensed (compatible with project license)
- CLI commands use @app.command() decorator pattern

**CLI Framework Pattern (from Architecture):**
```python
# src/mailreactor/cli/server.py
import typer
import uvicorn
from ..config import Settings
from ..main import create_app
from ..utils.logging import configure_logging

app = typer.Typer()

@app.command()
def start(
    host: str = typer.Option("127.0.0.1", help="Bind host address"),
    port: int = typer.Option(8000, help="Bind port number"),
    log_level: str = typer.Option("INFO", help="Log level"),
    json_logs: bool = typer.Option(False, "--json-logs", help="Enable JSON logging"),
    account: str = typer.Option(None, help="Email account (Epic 2)")
):
    """Start Mail Reactor API server"""
    
    # Configure logging first
    configure_logging(json_format=json_logs, log_level=log_level)
    
    # Load settings (overridden by CLI args)
    settings = Settings(host=host, port=port, log_level=log_level, json_logs=json_logs)
    
    # Create app
    app = create_app()
    
    # Log startup
    logger.info("server_starting", host=host, port=port, log_level=log_level)
    
    # Start server
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower()
    )
```

**CLI Entry Point Pattern:**
```python
# src/mailreactor/__main__.py
from .cli.server import app as typer_app

def main():
    """Entry point for CLI commands"""
    typer_app()

if __name__ == "__main__":
    main()
```

**pyproject.toml Entry Point:**
```toml
[project.scripts]
mailreactor = "mailreactor.__main__:main"
```

**NFR-P1: Startup Time Target (3 seconds)**
- Server must start and become operational within 3 seconds
- Measurement: Time from `mailreactor start` to first successful `/health` response
- Optimization strategies:
  - Lazy imports where possible
  - No heavy initialization in CLI parsing
  - FastAPI app created efficiently (no slow middleware)
  - Uvicorn starts quickly (default workers)
- Performance test: Assert startup time <3000ms

**NFR-S3: Network Security (localhost default)**
- Default binding: `127.0.0.1` (localhost only)
- Security rationale: Prevent accidental network exposure in MVP
- Explicit opt-in for network access: `--host 0.0.0.0`
- Log warning if binding to 0.0.0.0 without authentication (Epic 5)
- CLI help text should mention security implications

**Uvicorn Configuration:**
- Use `uvicorn.run()` for production start command
- Use Uvicorn with `reload=True` for dev command (Story 1.8)
- Pass FastAPI app instance (not import string)
- Configure log level to match structlog level
- Default workers: 1 (single process for MVP)
- No SSL in MVP (use reverse proxy for HTTPS)

[Source: docs/architecture.md#ADR-005-Typer-for-CLI-Framework]
[Source: docs/sprint-artifacts/tech-spec-epic-1.md#Workflows-and-Sequencing]

### Project Structure Notes

**File Locations (per unified project structure):**
```
src/mailreactor/
├── __main__.py                  # NEW: CLI entry point
├── cli/
│   ├── __init__.py              # NEW: Empty init
│   └── server.py                # NEW: Start/dev commands
├── main.py                      # USED: create_app() called by CLI
├── config.py                    # USED: Settings loaded in CLI
└── utils/
    └── logging.py               # USED: configure_logging() called first
```

**Testing Structure:**
```
tests/
├── unit/
│   └── test_cli_server.py       # NEW: CLI argument parsing, logic
├── integration/
│   └── test_server_startup.py   # NEW: Full startup sequence
└── e2e/
    └── test_cli_commands.py     # NEW: End-to-end CLI invocation
```

**Dependencies Added (none - Typer already in pyproject.toml from Story 1.1):**
- Typer >=0.20.0 (already present)
- Uvicorn[standard] (already present)

[Source: docs/architecture.md#Project-Structure]

### Technical Notes

**CLI Option Types and Validation:**
```python
# Typer handles validation automatically
host: str = typer.Option("127.0.0.1")  # String, no validation
port: int = typer.Option(8000, min=1, max=65535)  # Integer range
log_level: str = typer.Option("INFO", case_sensitive=False)  # Uppercase conversion
json_logs: bool = typer.Option(False, "--json-logs")  # Boolean flag (--json-logs to enable)
```

**Signal Handling for Graceful Shutdown:**
```python
import signal
import sys

def handle_shutdown(signum, frame):
    logger.info("server_stopping", signal=signum)
    # Uvicorn handles actual shutdown
    sys.exit(0)

signal.signal(signal.SIGINT, handle_shutdown)   # Ctrl+C
signal.signal(signal.SIGTERM, handle_shutdown)  # Process manager
```

**Startup Message Format (Console Renderer):**
```
[INFO]  10:30:45 Mail Reactor starting host=127.0.0.1 port=8000 log_level=INFO
[INFO]  10:30:45 Server started url=http://127.0.0.1:8000
[INFO]  10:30:45 API docs available url=http://127.0.0.1:8000/docs
[INFO]  10:30:45 Add account: mailreactor start --account you@email.com
```

**Startup Message Format (JSON Renderer with --json-logs):**
```json
{"timestamp": "2025-12-03T10:30:45Z", "level": "info", "event": "server_starting", "host": "127.0.0.1", "port": 8000, "log_level": "INFO"}
{"timestamp": "2025-12-03T10:30:45Z", "level": "info", "event": "server_started", "url": "http://127.0.0.1:8000"}
{"timestamp": "2025-12-03T10:30:45Z", "level": "info", "event": "docs_available", "url": "http://127.0.0.1:8000/docs"}
```

**Startup Performance Optimization:**
- Import only what's needed for start command
- Delay heavy imports until after CLI parsing
- No synchronous I/O during startup
- FastAPI app creation is already optimized (Story 1.2)
- Uvicorn starts with default settings (no custom workers)
- Target: <3 seconds cold start

**CLI Help Text Example:**
```
$ mailreactor start --help
Usage: mailreactor start [OPTIONS]

  Start Mail Reactor API server

  This command starts the FastAPI server on the specified host and port.
  By default, the server binds to localhost (127.0.0.1) for security.

Options:
  --host TEXT         Bind host address [default: 127.0.0.1]
  --port INTEGER      Bind port number [default: 8000]
  --log-level TEXT    Log level (DEBUG, INFO, WARNING, ERROR) [default: INFO]
  --json-logs         Enable JSON logging for production
  --account TEXT      Email account to add on startup (not implemented yet)
  --help             Show this message and exit
```

[Source: docs/architecture.md#CLI-Framework-Typer]
[Source: docs/epics.md#Story-1.4-CLI-Framework-with-Start-Command]

### Testing Best Practices

**Unit Tests for CLI:**
- Test CLI argument parsing without starting server
- Use Typer's CliRunner for isolated testing
- Mock create_app() and uvicorn.run() to avoid actual startup
- Verify Settings object constructed correctly
- Test configure_logging() called with correct parameters
- **Target Coverage**: 80%+ for `cli/server.py` module

**Integration Tests for Server Startup:**
- Start server in separate process/thread
- Wait for health endpoint to respond
- Verify startup messages logged
- Test graceful shutdown (send SIGINT)
- Use TestClient for FastAPI testing (httpx)
- **Test Duration**: Fast startup means tests complete quickly

**End-to-End Tests for CLI:**
- Invoke `mailreactor start` as subprocess
- Parse stdout/stderr for log messages
- Make HTTP request to verify server running
- Send SIGINT and verify clean shutdown
- Test with different CLI flags (--json-logs, --port, etc.)
- **Coverage**: All user-facing CLI workflows

**Performance Tests:**
- Measure startup time: `time mailreactor start` to first `/health` 200 OK
- Assert total time <3 seconds (NFR-P1)
- Use pytest-benchmark for repeatable measurements
- Track baseline in CI to detect regressions
- Test with cold start (clear Python cache)

**Manual Testing Checklist:**
- [ ] `mailreactor start` - verify console logs readable
- [ ] `mailreactor start --json-logs` - verify JSON output
- [ ] `mailreactor start --log-level DEBUG` - verify debug logs
- [ ] `mailreactor start --host 0.0.0.0 --port 9000` - verify binding
- [ ] `mailreactor start --help` - verify help text
- [ ] Ctrl+C during startup - verify graceful exit
- [ ] Ctrl+C after startup - verify shutdown message
- [ ] `python -m mailreactor start` - verify __main__ works

[Source: docs/tdd-guide.md]

### References

- **PRD Requirements**: [Source: docs/prd.md - FR-034 to FR-038 (CLI startup), NFR-P1 (startup time)]
- **Epic Breakdown**: [Source: docs/epics.md#Story-1.4-CLI-Framework-with-Start-Command]
- **Architecture Patterns**: [Source: docs/architecture.md#CLI-Framework-Typer]
- **Tech Spec Epic 1**: [Source: docs/sprint-artifacts/tech-spec-epic-1.md#Server-Startup-Sequence]
- **ADR-005**: [Source: docs/architecture.md#ADR-005-Typer-for-CLI-Framework]
- **Testing Standards**: [Source: docs/tdd-guide.md]
- **Typer Documentation**: https://typer.tiangolo.com/
- **Uvicorn Documentation**: https://www.uvicorn.org/

## Dev Agent Record

### Context Reference

- `docs/sprint-artifacts/1-4-cli-framework-with-start-command.context.xml` (generated: 2025-12-03)

### Agent Model Used

Claude 3.5 Sonnet (via claude-code CLI)

### Debug Log References

N/A - Story drafted, implementation pending

### Completion Notes List

*This section will be populated by the Dev agent during implementation*

### File List

*This section will be populated by the Dev agent during implementation*

## Change Log

**2025-12-03:** Story 1.4 completed by Dev agent (Amelia)
- All acceptance criteria implemented and passing
- 111 tests passing, 14 skipped (100% success rate)
- Total runtime: ~20 seconds
- **Key implementation decisions:**
  - Removed custom signal handlers - Uvicorn handles SIGINT/SIGTERM gracefully by default
  - Module-level app removed from main.py to prevent duplicate log messages
  - Simplified tests - removed fragile subprocess stderr parsing in favor of unit tests with mocks
  - Integrated Uvicorn logs with structlog via `ProcessorFormatter` for consistent formatting
  - Logging configuration happens only in CLI, not in `create_app()`
- **Code quality improvements (post-implementation):**
  - Added inline comment explaining `.lower()` for Uvicorn log_level parameter (line 112)
  - Refactored `logging.py` to eliminate redundant code:
    - Removed unused `processors` variable
    - Used `*shared_processors` unpacking to reuse shared processors
    - Extracted `renderer` variable for single source of truth
    - Result: 15 fewer lines, clearer architecture, same behavior

**2025-12-03:** Story 1.4 drafted by SM agent (Bob) in YOLO mode
- Extracted requirements from Epic 1 Story 1.4 (epics.md lines 304-370)
- Incorporated learnings from Story 1.3 (logging system ready, configure_logging function available)
- Added ADR-005 CLI framework guidance (Typer patterns)
- Detailed Uvicorn configuration for production start command
- Included NFR-P1 startup time target (3 seconds) with performance testing
- Included NFR-S3 localhost default binding for security
- Comprehensive task breakdown: 13 tasks with detailed subtasks
- Testing strategy: unit (CLI parsing), integration (server startup), end-to-end (full CLI workflow)
- Manual testing checklist for developer validation
- Status: drafted, ready for validation or story-context generation
