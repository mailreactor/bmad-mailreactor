# Story 1.8: Development Mode with Hot Reload

Status: ready-for-dev

## Story

As a developer,
I want a `mailreactor dev` command that enables auto-reload during development,
so that I can iterate quickly without manually restarting the server.

## Acceptance Criteria

**Given** the CLI from Story 1.4  
**When** adding development mode  
**Then** `src/mailreactor/cli/server.py` provides:
- `dev()` command using Typer
- Same options as `start` command (--host, --port, --log-level, --json-logs)
- Starts Uvicorn with `reload=True` (watches for file changes)
- Watches `src/mailreactor/` directory for changes
- Log level defaults to DEBUG in dev mode

**And** Running `mailreactor dev`:
- Displays "[INFO]  Development mode enabled auto_reload=True watch_dir=src/mailreactor"
- Reloads application automatically when Python files change
- Logs each reload event with changed file: "[INFO]  Reloading due to file change file=main.py"
- Uses colored console logging by default (not JSON, better DX)
- Can enable JSON logs with `--json-logs` flag if needed

**And** Development mode warning displayed: "[WARN]  Development mode active (not for production use)"

**And** Console output shows reload events:
```
[INFO]  Development mode enabled auto_reload=True watch_dir=src/mailreactor
[INFO]  Mail Reactor started url=http://127.0.0.1:8000
[INFO]  API documentation available url=http://127.0.0.1:8000/docs
[WARN]  Development mode active (not for production use)
...user edits file...
[INFO]  Reloading due to file change file=main.py
[INFO]  Mail Reactor started url=http://127.0.0.1:8000
```

**Prerequisites:** Story 1.4 (CLI with start command)

## Tasks / Subtasks

- [ ] Add `dev()` command to `cli/server.py` (AC: new command with same options)
  - [ ] Copy `start()` command structure (reuse same option definitions)
  - [ ] Set `reload=True` for Uvicorn configuration
  - [ ] Set `reload_dirs=["src/mailreactor"]` to watch only source code
  - [ ] Default log level to DEBUG (override Settings.log_level)
  - [ ] Disable JSON logs by default (console renderer for better DX)
  - [ ] Add development mode warning to startup logs
  - [ ] Log reload configuration: `auto_reload=True`, `watch_dir=src/mailreactor`

- [ ] Configure Uvicorn reload mode correctly (AC: watches file changes, reloads automatically)
  - [ ] Set `reload=True` in Uvicorn.run() call
  - [ ] Set `reload_dirs=["src/mailreactor"]` to limit watch scope
  - [ ] Use `reload_delay=0.5` for responsiveness (half-second after last change)
  - [ ] Exclude test directories (only watch source code)
  - [ ] Verify .pyc and __pycache__ changes don't trigger reload

- [ ] Add reload event logging (AC: logs each reload with file that changed)
  - [ ] Subscribe to Uvicorn reload events (if possible)
  - [ ] Log file change events: "[INFO]  Reloading due to file change file={path}"
  - [ ] If Uvicorn doesn't expose events, log basic reload message
  - [ ] Include timestamp in reload logs for tracking iterations

- [ ] Update __main__.py to register dev command (AC: `mailreactor dev` invocation works)
  - [ ] Add `dev()` to Typer app commands (already has `start()`)
  - [ ] Verify both `mailreactor dev` and `python -m mailreactor dev` work
  - [ ] Ensure command appears in `mailreactor --help` output
  - [ ] Add short help text: "Start with auto-reload for development"

- [ ] Write integration test for dev command (AC: command starts with reload enabled)
  - [ ] Test `mailreactor dev` starts server successfully
  - [ ] Test log output includes "Development mode enabled" message
  - [ ] Test log level defaults to DEBUG (not INFO)
  - [ ] Test --host and --port options work in dev mode
  - [ ] Test graceful shutdown works (Ctrl+C)
  - [ ] Note: File change reload not tested (requires filesystem events, complex)

- [ ] Update development practices documentation (AC: dev workflow documented)
  - [ ] Add "Development Mode" section to development-practices.md
  - [ ] Document difference between `start` (production) and `dev` (development)
  - [ ] Note that `dev` mode watches for file changes and auto-reloads
  - [ ] Warn against using `dev` mode in production (no performance optimization)
  - [ ] Example: `mailreactor dev` for quick iteration vs `mailreactor start` for deployment

## Dev Notes

### Learnings from Previous Story

**From Story 1-7-response-envelope-and-error-handling-standards (Status: done)**

- **Pydantic models for responses**: All API responses now use `SuccessResponse[T]` or `ErrorResponse` envelopes
- **Request ID middleware**: Already exists at `api/middleware.py`, generates UUID per request
- **Exception handlers refactored**: Use `ErrorResponse.model_dump()` for JSONResponse content
- **Health endpoint updated**: Returns `SuccessResponse[HealthResponse]` envelope with meta fields
- **Timestamp consolidation**: Only in `meta.timestamp` (ISO 8601 UTC), removed duplicates
- **Documentation quality**: Model docstrings removed for clean Swagger UI, inline comments for developers
- **Tests comprehensive**: 131 tests passing (unit + integration)
- **Scope clarification**: Refactoring existing code (middleware, handlers) vs building from scratch
- **`.model_dump()` usage**: Required for JSONResponse content (dict), NOT for FastAPI endpoint returns (auto-serialization)

[Source: stories/1-7-response-envelope-and-error-handling-standards.md#Dev-Agent-Record]

### Architecture Patterns and Constraints

**Development Workflow (from Architecture):**

The architecture doc (section "Development Workflow") establishes a clear distinction between production and development modes:

**Production Mode (`mailreactor start`):**
- Uvicorn runs with `reload=False` (no file watching)
- Optimized for performance and stability
- Used in deployment environments (Docker, VPS, production servers)
- Log level defaults to INFO

**Development Mode (`mailreactor dev`):**
- Uvicorn runs with `reload=True` (watches for file changes)
- Auto-reloads on code changes for fast iteration
- Used during local development only
- Log level defaults to DEBUG for detailed troubleshooting
- Console logs (colored, human-readable) by default

**Typer CLI Pattern (from ADR-005):**

Mail Reactor uses Typer for CLI commands. The `start` command already exists in `cli/server.py`. The `dev` command should:

1. **Reuse Options**: Same CLI flags as `start` (--host, --port, --log-level, --json-logs)
2. **Override Defaults**: Log level = DEBUG (not INFO), reload = True
3. **Add Warning**: Log development mode warning on startup
4. **Maintain Consistency**: Same startup flow as `start`, just different Uvicorn config

**Uvicorn Reload Configuration:**

```python
# cli/server.py - start command (existing)
def start(
    host: str = "127.0.0.1",
    port: int = 8000,
    log_level: str = "INFO",
    json_logs: bool = False,
):
    configure_logging(json_format=json_logs, log_level=log_level)
    logger.info("Mail Reactor started", url=f"http://{host}:{port}")
    
    uvicorn.run(
        "mailreactor.main:create_app",
        host=host,
        port=port,
        reload=False,  # ← Production mode
        factory=True,
        log_config=None,  # Use structlog instead
    )

# cli/server.py - dev command (NEW in Story 1.8)
def dev(
    host: str = "127.0.0.1",
    port: int = 8000,
    log_level: str = "DEBUG",  # ← Override default to DEBUG
    json_logs: bool = False,
):
    configure_logging(json_format=json_logs, log_level=log_level)
    logger.warning("Development mode active (not for production use)")
    logger.info(
        "Development mode enabled",
        auto_reload=True,
        watch_dir="src/mailreactor"
    )
    logger.info("Mail Reactor started", url=f"http://{host}:{port}")
    
    uvicorn.run(
        "mailreactor.main:create_app",
        host=host,
        port=port,
        reload=True,  # ← Enable auto-reload
        reload_dirs=["src/mailreactor"],  # ← Watch source only
        reload_delay=0.5,  # ← Wait 0.5s after last change
        factory=True,
        log_config=None,  # Use structlog instead
    )
```

**Key Differences:**
1. `reload=True` - Enables file watching
2. `reload_dirs=["src/mailreactor"]` - Limits watch scope (don't watch tests)
3. `reload_delay=0.5` - Wait half-second after last change before reloading
4. Default log_level="DEBUG" - More verbose output for development
5. Warning message - Alerts developer not for production

[Source: docs/architecture.md#Development-Workflow]
[Source: docs/architecture.md#CLI-Framework-Typer]

### Project Structure Notes

**Modified Files (Story 1.8):**
```
src/mailreactor/
└── cli/
    └── server.py          # MODIFIED: Add dev() command (parallel to start())
```

**No New Files:**
- `__main__.py` already exists (just register new command)
- `cli/server.py` already has `start()` command (add `dev()` next to it)

**Dependencies:**
- Uvicorn (already installed, used by `start` command)
- Typer (already installed, CLI framework)
- No new dependencies required

**Testing Strategy:**

Per team constraint: "✅ ONLY test functionality WE have added"

Integration test for `dev` command:
- ✅ Test command starts server with reload=True
- ✅ Test log output includes development mode warning
- ✅ Test default log level is DEBUG (not INFO)
- ✅ Test CLI options (--host, --port, --log-level) work
- ❌ Don't test Uvicorn's file watching (that's Uvicorn's responsibility)
- ❌ Don't test actual reload on file change (complex, filesystem events)

Simple integration test approach:
```python
# tests/integration/test_cli_dev_command.py
def test_dev_command_starts_with_reload_enabled(capsys):
    """Test mailreactor dev command starts with reload enabled."""
    # We can't easily test actual reload without filesystem manipulation
    # But we can verify the command accepts correct arguments and logs correctly
    
    # This would need subprocess or process spawning
    # Simplified: just verify the function exists and has correct signature
    from mailreactor.cli.server import dev
    import inspect
    
    sig = inspect.signature(dev)
    assert 'host' in sig.parameters
    assert 'port' in sig.parameters
    assert 'log_level' in sig.parameters
    assert 'json_logs' in sig.parameters
```

**Real-world verification** (manual test during implementation):
```bash
# Terminal 1: Start dev server
mailreactor dev

# Terminal 2: Edit a file
echo "# test change" >> src/mailreactor/main.py

# Terminal 1: Observe reload
[INFO]  Reloading due to file change file=main.py
[INFO]  Mail Reactor started url=http://127.0.0.1:8000
```

[Source: docs/architecture.md#Project-Structure]
[Source: docs/hc-standards.md#Testing-Principle]

### Technical Notes

**Key Implementation Requirements:**

1. **Uvicorn Reload Mode**:
   - Set `reload=True` to enable file watching
   - Set `reload_dirs=["src/mailreactor"]` to limit scope
   - Use `reload_delay=0.5` for responsive reloads
   - Uvicorn watches .py files by default (correct behavior)

2. **Development Warning**:
   - Log warning on startup: "Development mode active (not for production use)"
   - Helps prevent accidental production deployment with reload enabled
   - Warning level (not error) - it's informational

3. **Log Level Override**:
   - Default to DEBUG in dev mode (not INFO)
   - Still allow override via --log-level flag
   - Example: `mailreactor dev --log-level INFO` (if user wants less output)

4. **Console Logs by Default**:
   - Don't use JSON logs in dev mode (harder to read)
   - Console renderer (colored, human-readable) better DX
   - Still allow `--json-logs` flag if user wants structured output

5. **Watch Directory Scope**:
   - Only watch `src/mailreactor/` (not tests, not docs)
   - Prevents unnecessary reloads when editing test files
   - Faster reload detection (less file system scanning)

6. **Reload Delay**:
   - Wait 0.5 seconds after last file change before reloading
   - Prevents multiple reloads if developer saves multiple files quickly
   - Uvicorn default is 0.25s, we use 0.5s for stability

**Uvicorn Reload Internals (FYI, not for testing):**

Uvicorn uses Watchfiles (formerly watchgod) to detect file changes:
- Monitors specified directories for .py file changes
- Debounces changes with configurable delay
- Sends SIGTERM to worker process, spawns new one
- New process imports updated code

We don't test these internals (Uvicorn's responsibility). We test:
- Command exists and accepts correct arguments
- Logging shows development mode enabled
- Server starts successfully with reload=True

**Common Pitfalls to Avoid:**

1. **Don't watch tests/** - Causes reload when editing tests (unnecessary)
2. **Don't watch docs/** - Causes reload when editing documentation (unnecessary)
3. **Don't use reload=True in production** - Performance overhead, security risk
4. **Don't forget development warning** - Users might deploy dev mode by accident

**FR Coverage:**

This story doesn't directly implement FRs (all foundation FRs covered by previous stories). It enhances developer experience:
- Faster iteration cycles (no manual restart)
- Immediate feedback on code changes
- Better alignment with modern development workflows

**Related Stories:**
- Story 1.4: CLI framework with `start` command (this adds `dev` command)
- Story 1.3: Logging configuration (this uses DEBUG level by default)

[Source: docs/epics.md#Story-1.8]
[Source: docs/architecture.md#Development-Workflow]

### References

- **Epic Breakdown**: [Source: docs/epics.md#Story-1.8-Development-Mode-with-Hot-Reload]
- **Architecture Patterns**: [Source: docs/architecture.md#Development-Workflow]
- **CLI Framework**: [Source: docs/architecture.md#CLI-Framework-Typer]
- **Previous Story**: [Source: docs/sprint-artifacts/1-7-response-envelope-and-error-handling-standards.md]
- **Team Standards**: [Source: docs/hc-standards.md]
- **Uvicorn Documentation**: https://www.uvicorn.org/settings/#development
- **Typer Documentation**: https://typer.tiangolo.com/

## Dev Agent Record

### Context Reference

- `docs/sprint-artifacts/1-8-development-mode-with-hot-reload.context.xml`

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

## Change Log

**2025-12-04:** Story 1.8 drafted by SM agent via create-story workflow (initial version)
- Extracted requirements from Epic 1 Story 1.8 (epics.md lines 506-543)
- Incorporated learnings from Story 1.7 (response models, refactoring patterns)
- Key deliverables: `dev()` command with auto-reload, development warning, DEBUG logging
- Reuses existing CLI framework and Uvicorn configuration
- Simple integration test approach (verify command signature, not filesystem events)
- Status: drafted, ready for implementation
