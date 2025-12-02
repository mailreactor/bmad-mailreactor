# Story 1.3: Structured Logging with Console and JSON Renderers

Status: drafted

## Story

As a developer,
I want clean console logs by default with optional JSON output,
so that the quick start experience is clear while still supporting production log aggregation.

## Acceptance Criteria

**Given** the FastAPI application from Story 1.2  
**When** logging is configured  
**Then** `src/mailreactor/utils/logging.py` provides:
- `configure_logging(json_format: bool = False)` function setting up structlog
- **Single internal pipeline:** All logs use structlog's structured format internally
- **Console renderer by default:** Colored, human-readable output via `rich` integration
- **JSON renderer when requested:** Machine-readable structured logs for log aggregators
- Shared processors: timestamp (ISO format), log level, logger name, stack info, exception formatting
- Context binding support (account_id, request_id, folder)

**And** Console format (default) displays:
```
[INFO]  10:30:45 Mail Reactor started at http://127.0.0.1:8000
[INFO]  10:30:45 API Documentation: http://127.0.0.1:8000/docs
[INFO]  10:30:46 Account connected email=you@gmail.com
[INFO]  10:30:50 Email sent recipient=recipient@example.com message_id=abc123
```

**And** Console format uses color coding only:
- **Green:** INFO level for successful operations
- **Yellow:** WARN level 
- **Red:** ERROR/CRITICAL levels
- **Blue:** DEBUG level (dev mode)
- **Bold:** Timestamps and log levels
- **Minimal emoji:** Only for critical moments (account connected ✓, startup failed ✗, auth warning ⚠)

**And** Console format shows context as key=value pairs on same line:
```
[INFO]  10:30:50 Email sent recipient=user@example.com message_id=abc123 account=you@gmail.com
[WARN]  10:31:00 IMAP connection slow duration_ms=2500 account=you@gmail.com
[ERROR] 10:31:10 SMTP authentication failed account=test@custom.com error="Invalid credentials"
```

**And** JSON format (opt-in via `--json-logs` flag) outputs same data, different rendering:
```json
{"timestamp": "2025-11-25T10:30:45Z", "level": "info", "event": "server_started", "url": "http://127.0.0.1:8000"}
{"timestamp": "2025-11-25T10:30:50Z", "level": "info", "event": "email_sent", "recipient": "user@example.com", "message_id": "abc123", "account": "you@gmail.com"}
```

**And** Internal logging architecture:
1. Application calls: `logger.info("email_sent", recipient=email, message_id=id)`
2. Structlog processes with shared processors (timestamp, level, context)
3. Final renderer chosen based on configuration:
   - Console: `rich`-based colored output with key=value format
   - JSON: Standard JSON lines format
4. Single pipeline, different output renderers (not two separate logging systems)

**And** Logging is configured on application startup before any other initialization

**And** Log level is configurable via:
- CLI flag: `--log-level` (DEBUG, INFO, WARNING, ERROR)
- Environment variable: `MAILREACTOR_LOG_LEVEL`
- Default: INFO for `start`, DEBUG for `dev`

**And** Sensitive data is never logged (passwords, API keys, full email bodies)

**Prerequisites:** Story 1.2 (FastAPI app initialized)

## Tasks / Subtasks

- [ ] Create logging configuration module (AC: logging.py provides...)
  - [ ] Create `src/mailreactor/utils/logging.py` module
  - [ ] Import required libraries: structlog, rich, logging (stdlib)
  - [ ] Define `configure_logging(json_format: bool = False, log_level: str = "INFO")` function
  - [ ] Add type hints for all function parameters and return types
  - [ ] Write docstring explaining single pipeline with dual renderers

- [ ] Configure structlog shared processors (AC: shared processors)
  - [ ] Add `structlog.processors.TimeStamper(fmt="iso")` for ISO 8601 timestamps
  - [ ] Add `structlog.stdlib.add_log_level` to include level in log context
  - [ ] Add `structlog.stdlib.add_logger_name` to include logger name
  - [ ] Add `structlog.processors.StackInfoRenderer()` for stack traces
  - [ ] Add `structlog.processors.format_exc_info` for exception formatting
  - [ ] Add `structlog.processors.UnicodeDecoder()` for proper string handling
  - [ ] Configure processors list to run before final renderer

- [ ] Implement console renderer with rich integration (AC: Console renderer by default)
  - [ ] Create custom console renderer class extending `structlog.dev.ConsoleRenderer`
  - [ ] Integrate `rich.console.Console` for colored output
  - [ ] Format log entries as: `[LEVEL] HH:MM:SS message key=value key=value`
  - [ ] Apply color scheme:
    - INFO: Green
    - WARNING: Yellow
    - ERROR/CRITICAL: Red
    - DEBUG: Blue
  - [ ] Make timestamps and log levels bold
  - [ ] Add minimal emoji support (✓, ✗, ⚠) only for specific events
  - [ ] Ensure key=value pairs are on same line as message
  - [ ] Write unit tests for console output formatting

- [ ] Implement JSON renderer for production (AC: JSON renderer when requested)
  - [ ] Use `structlog.processors.JSONRenderer()` for JSON output
  - [ ] Configure JSON renderer to output one log entry per line (JSON Lines format)
  - [ ] Ensure all context fields are included in JSON output
  - [ ] Format timestamp as ISO 8601 with UTC timezone
  - [ ] Test JSON output is valid and parseable
  - [ ] Write unit tests for JSON formatting

- [ ] Add context binding support (AC: context binding support)
  - [ ] Configure `structlog.contextvars` for request-scoped context
  - [ ] Add `structlog.contextvars.merge_contextvars` to processor chain
  - [ ] Provide utility function: `bind_context(**kwargs)` for adding context
  - [ ] Provide utility function: `unbind_context(*keys)` for removing context
  - [ ] Provide utility function: `clear_context()` for clearing all context
  - [ ] Add context fields: account_id, request_id, folder, duration_ms
  - [ ] Write unit tests for context binding and propagation

- [ ] Implement sensitive data filtering (AC: sensitive data never logged)
  - [ ] Create processor to detect and redact sensitive fields
  - [ ] Redact fields: password, api_key, auth_token, secret
  - [ ] Replace sensitive values with "[REDACTED]" in logs
  - [ ] Apply filtering before both console and JSON renderers
  - [ ] Add configuration option to customize sensitive field names
  - [ ] Write unit tests for sensitive data redaction

- [ ] Integrate logging with FastAPI app (AC: logging configured on startup)
  - [ ] Update `src/mailreactor/main.py` to call `configure_logging()` at app startup
  - [ ] Pass `json_format` parameter from settings
  - [ ] Pass `log_level` from settings
  - [ ] Add startup logging: "server_starting" with host/port/log_level
  - [ ] Add startup logging: "server_ready" with docs_url/uptime_ms
  - [ ] Configure uvicorn to use structlog logger
  - [ ] Write integration tests for app startup logging

- [ ] Update request ID middleware to bind context (AC: request_id in context)
  - [ ] Update `src/mailreactor/api/dependencies.py` RequestIDMiddleware
  - [ ] Remove TODO comment about structlog binding
  - [ ] Call `bind_context(request_id=request_id)` at request start
  - [ ] Call `clear_context()` at request end (cleanup)
  - [ ] Log request completion with: method, path, status_code, duration_ms
  - [ ] Write integration tests for request ID in log context

- [ ] Update settings for logging configuration (AC: log level configurable)
  - [ ] Add `json_logs: bool = False` to Settings model in `config.py`
  - [ ] Verify `log_level: str = "INFO"` field already exists (from Story 1.2)
  - [ ] Add validation for log_level values (DEBUG, INFO, WARNING, ERROR)
  - [ ] Update environment variable documentation in Settings docstring
  - [ ] Write unit tests for settings with various log configurations

- [ ] Replace print statements with structured logging
  - [ ] Update `src/mailreactor/core/events.py` line 134 print() to logger.debug()
  - [ ] Import structlog logger in events.py: `logger = structlog.get_logger()`
  - [ ] Log event emission: `logger.debug("event_emitted", event_type=event.event_type, handler_count=len(handlers))`
  - [ ] Ensure no FastAPI imports remain in core module (maintain FR-099 compliance)
  - [ ] Write unit test to verify events.py uses structlog, not print

- [ ] Add logging examples and documentation
  - [ ] Create `docs/logging-guide.md` with usage examples
  - [ ] Document console vs JSON renderer differences
  - [ ] Provide code examples for binding context
  - [ ] Document sensitive data filtering
  - [ ] Include troubleshooting section for common logging issues
  - [ ] Add examples for different log levels

- [ ] Testing and validation (AC: All acceptance criteria met)
  - [ ] Write unit test: Console renderer produces colored output
  - [ ] Write unit test: JSON renderer produces valid JSON lines
  - [ ] Write unit test: Shared processors apply correctly
  - [ ] Write unit test: Context binding propagates through log calls
  - [ ] Write unit test: Sensitive data is redacted
  - [ ] Write unit test: Log level filtering works correctly
  - [ ] Write integration test: FastAPI app logs startup sequence
  - [ ] Write integration test: Request ID appears in request logs
  - [ ] Write integration test: Logger can switch between console and JSON renderers
  - [ ] Manual test: Run `mailreactor start` and verify console output is readable
  - [ ] Manual test: Run with `--json-logs` and verify JSON output

## Dev Notes

### Learnings from Previous Story

**From Story 1-2-fastapi-application-initialization (Status: done)**

- **Settings Configuration Ready**: `config.py` has `log_level: str = "INFO"` field ready for use
  - Add new field `json_logs: bool = False` to control renderer selection
- **Request ID Middleware Has TODO**: `dependencies.py` line has TODO comment for structlog binding
  - Implement `bind_context(request_id=request_id)` call in this story
- **EventEmitter Uses Print Statement**: `events.py` line 134 has print() for error logging
  - Replace with `logger.debug("event_emitted", ...)` using structlog
- **Exception Handlers Ready**: Consistent error envelope format established
  - Use structlog for logging exceptions before returning error responses
- **Zero Technical Debt From Story 1.2**: All code review action items resolved
  - No blocking issues to address before starting Story 1.3

[Source: stories/1-2-fastapi-application-initialization.md#Dev-Agent-Record]

### Architecture Patterns and Constraints

**ADR-006: Structured Logging (structlog)**
- Use structlog for structured logging with key=value pairs
- Single internal pipeline with different renderers (not separate logging systems)
- Console renderer for development (human-readable with colors)
- JSON renderer for production (machine-parseable for log aggregation)
- ISO 8601 timestamps in UTC timezone
- Context binding support for request tracing

**NFR-O1: Logging Requirements**
- Structured logging with configurable levels (DEBUG, INFO, WARNING, ERROR)
- Console renderer: Colored output with timestamps, human-readable
- JSON renderer: Machine-parseable for log aggregation (e.g., ELK stack)
- Request/response logging at INFO level with duration_ms
- Sensitive data redacted: no passwords, no API keys in logs

**Console Format Examples (from Tech Spec Epic 1):**
```
# Development (default console renderer)
2025-11-28T10:30:00Z [INFO ] server_starting host=127.0.0.1 port=8000 log_level=INFO
2025-11-28T10:30:03Z [INFO ] server_ready docs_url=http://127.0.0.1:8000/docs uptime_ms=2847

# Production (JSON renderer with --json-logs)
{"event": "server_starting", "level": "info", "timestamp": "2025-11-28T10:30:00Z", "host": "127.0.0.1", "port": 8000}
{"event": "api_request", "level": "info", "method": "GET", "path": "/health", "status_code": 200, "duration_ms": 12}
```

**Color Scheme (Console Only):**
- Use ANSI color codes via `rich` library
- INFO: Green (successful operations)
- WARNING: Yellow (potential issues)
- ERROR/CRITICAL: Red (failures)
- DEBUG: Blue (detailed troubleshooting)
- Bold: Timestamps and log levels for visibility

**Minimal Emoji Usage:**
- Only for critical lifecycle events: ✓ (success), ✗ (failure), ⚠ (warning)
- Examples:
  - `[INFO]  Account connected ✓ email=you@gmail.com`
  - `[ERROR] Server startup failed ✗ error="Port 8000 already in use"`
  - `[WARN]  Authentication disabled ⚠ (use --api-key for production)`

[Source: docs/architecture.md#Logging-Pattern]
[Source: docs/sprint-artifacts/tech-spec-epic-1.md#Observability]

### Project Structure Notes

**File Locations (per unified project structure):**
```
src/mailreactor/
├── utils/
│   ├── __init__.py
│   └── logging.py              # NEW: structlog configuration
├── main.py                      # MODIFIED: Call configure_logging() on startup
├── config.py                    # MODIFIED: Add json_logs field
├── core/
│   └── events.py                # MODIFIED: Replace print() with logger.debug()
└── api/
    └── dependencies.py          # MODIFIED: Remove TODO, add bind_context() calls
```

**Testing Structure:**
```
tests/
├── unit/
│   ├── test_logging.py          # NEW: Console/JSON renderer tests
│   └── test_config.py           # MODIFIED: Add json_logs field tests
└── integration/
    ├── test_app_initialization.py  # MODIFIED: Verify startup logging
    └── test_request_logging.py     # NEW: Verify request ID in logs
```

[Source: docs/architecture.md#Project-Structure]

### Technical Notes

**structlog Configuration Pattern:**
```python
# src/mailreactor/utils/logging.py
import structlog
import logging
from rich.console import Console

def configure_logging(json_format: bool = False, log_level: str = "INFO") -> None:
    """Configure structlog with single pipeline, dual renderers.
    
    Args:
        json_format: If True, use JSON renderer for production. If False, use console renderer.
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR)
    """
    # Configure stdlib logging as backend
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper()),
    )
    
    # Shared processors (before renderer)
    shared_processors = [
        structlog.contextvars.merge_contextvars,  # Include bound context
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        _filter_sensitive_data,  # Custom processor
    ]
    
    # Choose renderer based on configuration
    if json_format:
        # Production: JSON Lines format
        renderer = structlog.processors.JSONRenderer()
    else:
        # Development: Rich-enhanced console output
        renderer = _create_console_renderer()
    
    # Configure structlog
    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

**Context Binding Utilities:**
```python
# src/mailreactor/utils/logging.py
import structlog

def bind_context(**kwargs) -> None:
    """Bind context variables to current structlog context."""
    structlog.contextvars.bind_contextvars(**kwargs)

def unbind_context(*keys: str) -> None:
    """Remove specific keys from structlog context."""
    structlog.contextvars.unbind_contextvars(*keys)

def clear_context() -> None:
    """Clear all context variables."""
    structlog.contextvars.clear_contextvars()
```

**Sensitive Data Filtering:**
```python
def _filter_sensitive_data(logger, method_name, event_dict):
    """Redact sensitive fields from log output."""
    sensitive_fields = {"password", "api_key", "auth_token", "secret", "authorization"}
    
    for key in event_dict.keys():
        if key.lower() in sensitive_fields:
            event_dict[key] = "[REDACTED]"
    
    return event_dict
```

**Integration with FastAPI:**
```python
# src/mailreactor/main.py
from .utils.logging import configure_logging
from .config import settings
import structlog

logger = structlog.get_logger()

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    # Configure logging FIRST (before any other operations)
    configure_logging(json_format=settings.json_logs, log_level=settings.log_level)
    
    logger.info("server_starting", host=settings.host, port=settings.port, log_level=settings.log_level)
    
    app = FastAPI(
        title="Mail Reactor API",
        version="0.1.0",
        # ... rest of config
    )
    
    # ... middleware, routers, etc.
    
    return app
```

**Request ID Middleware Update:**
```python
# src/mailreactor/api/dependencies.py
from ..utils.logging import bind_context, clear_context
import structlog

logger = structlog.get_logger()

async def request_id_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    
    # Bind request_id to structlog context
    bind_context(request_id=request_id)
    
    start_time = time.time()
    
    try:
        response = await call_next(request)
        duration_ms = int((time.time() - start_time) * 1000)
        
        logger.info(
            "api_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms
        )
        
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        # Clean up context after request
        clear_context()
```

[Source: docs/architecture.md#Logging-Pattern]
[Source: docs/sprint-artifacts/tech-spec-epic-1.md#Data-Models-and-Contracts]

### Testing Best Practices

**Unit Tests for Logging:**
- Test console renderer produces expected format
- Test JSON renderer produces valid JSON
- Test log level filtering (DEBUG logs don't appear at INFO level)
- Test sensitive data redaction
- Test context binding and propagation
- Mock rich.Console to capture output for assertions

**Integration Tests:**
- Test FastAPI app startup logs configuration
- Test request middleware logs include request_id
- Test exception handler logs include stack traces
- Test log output can be captured and parsed

**Manual Testing:**
- Run `mailreactor start` and verify console logs are readable and colored
- Run `mailreactor start --log-level DEBUG` and verify debug logs appear
- Run `mailreactor start --json-logs` and verify JSON output
- Make API requests and verify request_id appears in logs
- Trigger errors and verify sensitive data is redacted

[Source: docs/tdd-guide.md]

### References

- **PRD Requirements**: [Source: docs/prd.md - FR-028 to FR-031 (Logging), NFR-O1]
- **Epic Breakdown**: [Source: docs/epics.md#Story-1.3-Structured-Logging]
- **Architecture Patterns**: [Source: docs/architecture.md#Logging-Pattern]
- **Tech Spec Epic 1**: [Source: docs/sprint-artifacts/tech-spec-epic-1.md#Observability]
- **ADR-006**: [Source: docs/architecture.md#ADR-006-Use-structlog-for-Logging]
- **Testing Standards**: [Source: docs/tdd-guide.md]
- **structlog Documentation**: https://www.structlog.org/en/stable/
- **rich Documentation**: https://rich.readthedocs.io/en/stable/

## Dev Agent Record

### Context Reference

- `docs/sprint-artifacts/1-3-structured-logging-with-console-and-json-renderers.context.xml` (to be generated)

### Agent Model Used

(To be filled by dev agent)

### Debug Log References

(To be filled by dev agent)

### Completion Notes List

(To be filled by dev agent after implementation)

### File List

**NEW:**
- (To be filled by dev agent)

**MODIFIED:**
- (To be filled by dev agent)

**DELETED:**
- (To be filled by dev agent)

## Change Log

**2025-12-02:** Story 1.3 drafted by SM agent
- Extracted requirements from Tech Spec Epic 1 and epics.md Story 1.3
- Incorporated learnings from Story 1.2 (settings ready, request ID TODO, print() statement)
- Added comprehensive structlog configuration examples
- Detailed console vs JSON renderer architecture (single pipeline, dual renderers)
- Added sensitive data filtering requirements
- Included context binding utilities for request tracing
- Added integration points with FastAPI app and request middleware
- Status: drafted, ready for review or story-context generation
