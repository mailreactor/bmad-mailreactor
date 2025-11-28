# Epic Technical Specification: Foundation & Zero-Config Deployment

Date: 2025-11-28
Author: HC
Epic ID: epic-1
Status: Draft

---

## Overview

Epic 1 delivers the foundational infrastructure for Mail Reactor - a zero-configuration, developer-first email API service. This epic enables developers to install Mail Reactor via PyPI, start it with a single command, and have a fully operational REST API with auto-generated documentation within 3 seconds. The epic establishes the core FastAPI application, CLI framework, structured logging, health monitoring, and API documentation that all subsequent features will build upon.

The foundation prioritizes exceptional developer experience: beautiful console logs with color-coded output, interactive API documentation at `/docs`, clear error messages, and a development mode with hot-reload for rapid iteration. This epic delivers no email functionality - it creates the platform on which email features (Epic 2+) will run.

## Objectives and Scope

**In Scope:**
- ✅ Python package structure with proper namespace (`src/mailreactor/`)
- ✅ **Dual-mode architecture foundation (FR-099):** Core library separate from API layer
- ✅ **EventEmitter implementation (FR-102):** Transport-agnostic event system in `core/events.py`
- ✅ FastAPI application initialization with middleware and exception handling
- ✅ Structured logging with dual renderers (console for humans, JSON for machines)
- ✅ CLI framework (`mailreactor start`, `mailreactor dev`) with Typer
- ✅ Health check endpoint (`GET /health`) for monitoring
- ✅ Auto-generated OpenAPI documentation (Swagger UI + ReDoc)
- ✅ Standardized API response envelopes and error handling
- ✅ Development mode with auto-reload for rapid iteration
- ✅ Installation patterns: `pip install mailreactor` (library mode) vs `mailreactor[api]` (API mode)
- ✅ Package structure enforcing core/api separation (validated via SPIKE-001)

**Out of Scope:**
- ❌ Email account management (Epic 2)
- ❌ Email sending/receiving (Epic 3, 4)
- ❌ Actual event handler registration (FR-100, FR-101 - deferred to Epic 4)
- ❌ IMAP/SMTP client implementation (AsyncIMAPClient, AsyncSMTPClient in Epic 2/3)
- ❌ API authentication (Epic 5)
- ❌ State persistence or database connections
- ❌ Production deployment configuration (Docker, Kubernetes)

**Note on Dual-Mode Architecture:**
Epic 1 establishes the **foundation** for dual-mode usage (library + API) by:
- Implementing the EventEmitter class (no email features yet)
- Setting up package structure with optional dependencies
- Ensuring core/ module has zero FastAPI coupling

The actual email monitoring and event emission will be implemented in Epic 4 (Email Retrieval), leveraging this foundation.

**Success Criteria:**
- Developer can install and start Mail Reactor in under 5 minutes
- Server starts within 3 seconds (NFR-P1)
- Health endpoint responds within 50ms p95 (NFR-P2)
- Console logs are clean, colored, and human-readable
- API documentation is interactive and complete
- Zero configuration required for basic operation

## System Architecture Alignment

This epic implements the foundation described in Architecture ADR-001 through ADR-006:

**Web Framework (ADR-001):** FastAPI 0.122.0 provides the HTTP server with automatic OpenAPI generation, dependency injection, and native async support. All API endpoints follow FastAPI patterns with Pydantic validation.

**Project Structure (Architecture Doc):** Implements the `src/mailreactor/` layout with clear separation: `api/` for FastAPI routers, `core/` for business logic (unused in Epic 1), `models/` for Pydantic schemas, `cli/` for Typer commands, and `utils/` for shared utilities.

**CLI Framework (ADR-005):** Typer 0.20.0 provides the `mailreactor start` and `mailreactor dev` commands with type-safe argument parsing and auto-generated help text.

**Logging (ADR-006):** structlog delivers structured logging with two renderers: rich-enhanced console output (colored, key=value format) for development, and JSON output (opt-in via `--json-logs`) for production log aggregation.

**Configuration (Architecture Patterns):** Pydantic Settings manages configuration with environment variable support (`MAILREACTOR_*` prefix), `.env` file loading, and sensible defaults (localhost binding, 8000 port, INFO log level).

**Error Handling (Architecture Patterns):** Custom exception hierarchy (`MailReactorException` base class) with FastAPI exception handlers that return consistent error responses with proper HTTP status codes and clear messages.

**Event-Driven Architecture (ADR-007):** Implements transport-agnostic EventEmitter in `core/events.py` validated via SPIKE-001. This establishes the foundation for dual-mode usage: library mode (Python callbacks via FR-100) and API mode (HTTP webhooks via FR-101). Epic 1 delivers the EventEmitter class itself; actual email event emission comes in Epic 4.

**Dependencies:** Pure Python with MIT-compatible licenses - FastAPI, Uvicorn, Typer, Pydantic v2, structlog. Package structure uses optional dependencies (`[api]` extra) to enable library-only installation. No database, no external services, installable via PyPI/pipx.

## Detailed Design

### Services and Modules

| Module | Responsibility | Inputs | Outputs | Owner/Story |
|--------|---------------|--------|---------|-------------|
| `core/events.py` | **Transport-agnostic EventEmitter (FR-102)** | Event type, handler functions | Concurrent async handler execution | Story 1.2 |
| `main.py` | FastAPI application factory, middleware setup, exception handlers | Settings, router registrations | Configured FastAPI app instance | Story 1.2 |
| `config.py` | Application configuration via Pydantic Settings | Environment variables, `.env` file | Settings singleton with validated config | Story 1.2 |
| `exceptions.py` | Custom exception hierarchy and FastAPI handlers | Exception raises throughout app | HTTP error responses with standard format | Story 1.7 |
| `cli/server.py` | CLI commands for server lifecycle (`start`, `dev`) | CLI args (host, port, log level) | Uvicorn server process | Story 1.4 |
| `api/health.py` | Health check router with system metrics | None (reads app state) | Health status JSON response | Story 1.5 |
| `api/dependencies.py` | Shared FastAPI dependencies (future auth, state) | Request context | Dependency injection values | Story 1.2 |
| `models/responses.py` | Pydantic response models (envelopes, errors) | Data to serialize | Validated response objects | Story 1.7 |
| `utils/logging.py` | structlog configuration with console/JSON renderers | Log level, output format | Configured logger instances | Story 1.3 |

### Data Models and Contracts

**EventEmitter (FR-102 - Core Library):**
```python
from dataclasses import dataclass
from typing import Callable, Awaitable, Any
import asyncio

@dataclass
class Event:
    """Base event class"""
    event_type: str
    data: dict[str, Any]

class EventEmitter:
    """Transport-agnostic event dispatcher (validated in SPIKE-001)"""
    
    def __init__(self):
        self._handlers: dict[str, list[Callable]] = {}
    
    def on(self, event_type: str) -> Callable:
        """Decorator for registering async event handlers"""
        def decorator(handler: Callable[[Event], Awaitable[None]]):
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(handler)
            return handler
        return decorator
    
    async def emit(self, event: Event) -> None:
        """Emit event to all registered handlers concurrently"""
        handlers = self._handlers.get(event.event_type, [])
        if handlers:
            await asyncio.gather(
                *[h(event) for h in handlers],
                return_exceptions=True  # Isolate handler failures
            )
```

**Usage Pattern (Library Mode - Epic 4 will use this):**
```python
from mailreactor.core.events import EventEmitter, Event

emitter = EventEmitter()

@emitter.on("message.received")
async def handle_message(event: Event):
    print(f"New message: {event.data['subject']}")

# Epic 4 will emit events like this:
await emitter.emit(Event("message.received", {"subject": "Test"}))
```

**Health Check Response:**
```python
from pydantic import BaseModel
from datetime import datetime

class HealthResponse(BaseModel):
    status: str  # "healthy" | "degraded" | "unhealthy"
    version: str  # Package version
    uptime_seconds: float
    timestamp: datetime
```

**API Error Response (Standard Envelope):**
```python
from pydantic import BaseModel
from typing import Optional, Dict, Any

class ErrorDetail(BaseModel):
    code: str  # Machine-readable error code (e.g., "VALIDATION_ERROR")
    message: str  # Human-readable error message
    details: Optional[Dict[str, Any]] = None  # Field-specific validation errors

class ErrorResponse(BaseModel):
    error: ErrorDetail
```

**Settings Model:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Server
    host: str = "127.0.0.1"  # Localhost by default (security)
    port: int = 8000
    reload: bool = False  # Hot-reload for dev mode
    
    # Logging
    log_level: str = "INFO"  # DEBUG, INFO, WARN, ERROR
    json_logs: bool = False  # Console (default) or JSON
    
    # Metadata
    app_name: str = "Mail Reactor"
    version: str = "0.1.0"  # Read from pyproject.toml
    
    class Config:
        env_prefix = "MAILREACTOR_"
        env_file = ".env"
```

### APIs and Interfaces

**Base URL:** `http://localhost:8000`

**Health Check Endpoint:**
```
GET /health
Response: 200 OK
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime_seconds": 123.45,
  "timestamp": "2025-11-28T10:30:00Z"
}
```

**API Documentation Endpoints:**
```
GET /docs         → Swagger UI (interactive API explorer)
GET /redoc        → ReDoc (alternative documentation)
GET /openapi.json → OpenAPI 3.0 specification (JSON)
```

**Error Response Format (all endpoints):**
```
4xx/5xx Status Code
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": ["error message"]
    }
  }
}
```

**HTTP Status Codes Used:**
- `200 OK` - Successful request
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Unexpected server error
- `503 Service Unavailable` - Service degraded

### Workflows and Sequencing

**Server Startup Sequence:**
```
1. CLI invoked: `mailreactor start --host 0.0.0.0 --port 8000`
2. Typer parses arguments and validates
3. Load Settings from environment + CLI args
4. Configure structlog (console renderer for dev, JSON if --json-logs)
5. Log startup message with config summary
6. Initialize FastAPI app via factory function
7. Register exception handlers
8. Register health router
9. Start Uvicorn server (async)
10. Log "Server ready" with endpoint URLs
11. Health endpoint becomes responsive within 3 seconds
```

**Development Mode Startup:**
```
1. CLI invoked: `mailreactor dev`
2. Same as above, but set reload=True in Settings
3. Uvicorn watches file changes and auto-reloads
4. Log "Development mode enabled - auto-reload active"
```

**Health Check Request Flow:**
```
1. Client: GET /health
2. FastAPI routes to health.py endpoint
3. Read app startup time (calculate uptime)
4. Read package version from settings
5. Return HealthResponse (200 OK)
6. Response time: <50ms p95
```

**Error Handling Flow:**
```
1. Exception raised in endpoint (e.g., ValidationError)
2. FastAPI exception handler catches it
3. Match exception type to HTTP status code
4. Log error with structlog (level based on severity)
5. Return ErrorResponse with standard envelope
6. Never expose stack traces in production
```

## Non-Functional Requirements

### Performance

**NFR-P1: Startup Time (3 seconds)**
- Target: Cold start to operational health endpoint within 3 seconds on typical hardware (4-core CPU, 8GB RAM)
- Measurement: Time from `mailreactor start` command to first successful `GET /health` response
- Implementation: No database connections, minimal imports, lazy loading where possible
- Story 1.4 validates this with startup timing logs

**NFR-P2: API Response Latency (50ms p95 for health check)**
- Target: Health check endpoint responds within 50ms at 95th percentile
- Measurement: HTTP request duration from client perspective
- Implementation: In-memory uptime calculation, no external calls, async FastAPI endpoint
- Story 1.5 implements health endpoint optimized for speed

**NFR-P4: Memory Footprint (<100MB baseline)**
- Target: FastAPI app with no accounts consumes <100MB RAM at idle
- Measurement: Process RSS after startup stabilization
- Implementation: Pure Python, no heavy dependencies, no caching in Epic 1
- Validated during Story 1.1 dependency selection

**NFR-P6: Concurrent Connections (10 simultaneous requests for MVP)**
- Target: Handle 10 concurrent health check requests without degradation
- Measurement: Load test with 10 parallel clients
- Implementation: FastAPI async endpoints, Uvicorn worker pool
- Story 1.2 configures Uvicorn with appropriate worker settings

### Security

**NFR-S1: Credential Storage (N/A for Epic 1)**
- Epic 1 has no email credentials - deferred to Epic 2
- Settings object uses `exclude=True` for sensitive fields (pattern established)
- Never log passwords or secrets (structlog configured in Story 1.3)

**NFR-S3: Network Security (localhost binding by default)**
- Default binding: `127.0.0.1` (localhost only)
- Explicit opt-in required for remote access: `--host 0.0.0.0`
- Warning logged when binding to 0.0.0.0 without authentication (Epic 5)
- Story 1.4 implements CLI with secure defaults

**NFR-S4: Dependency Security (actively maintained, no known CVEs)**
- All dependencies checked for recent updates (within 6 months)
- FastAPI: 0.122.0 (maintained)
- Uvicorn: latest stable (maintained)
- Pydantic: v2 (actively developed)
- Typer: 0.20.0 (maintained)
- structlog: latest (maintained)
- Story 1.1 documents dependency versions and update policy

**NFR-S5: Data Privacy (no telemetry in Epic 1)**
- No usage data collection
- No external network calls except user-initiated API requests
- Clear privacy policy: "Mail Reactor collects no telemetry data"
- Future opt-in telemetry requires explicit user consent

### Reliability/Availability

**NFR-R2: Error Handling (meaningful messages, never expose internals)**
- All exceptions caught and converted to HTTP error responses
- Generic "Internal Server Error" in production, details in development mode
- Error responses include actionable messages: "Server configuration invalid: port must be 1-65535"
- Stack traces logged but never returned in API responses
- Story 1.7 implements exception hierarchy and handlers

**NFR-R4: Graceful Degradation (N/A for Epic 1)**
- Epic 1 has no external dependencies to degrade from
- Pattern established: log warnings for non-critical failures, continue operation
- Future epics will use this pattern for IMAP/SMTP connection failures

**NFR-R5: Uptime (health endpoint always responsive)**
- Health endpoint cannot fail - it's the canary for monitoring
- No external dependencies, no database queries
- Returns 503 "Service Unavailable" if app is shutting down (Uvicorn lifecycle)
- Story 1.5 ensures health endpoint robustness

### Observability

**NFR-O1: Logging (structured, configurable levels, sensitive data redacted)**
- Structured logging via structlog with key=value format
- Log levels: DEBUG, INFO, WARN, ERROR (configurable via `--log-level` or `MAILREACTOR_LOG_LEVEL`)
- Console renderer (default): Colored output with timestamps, human-readable
- JSON renderer (opt-in): Machine-parseable for log aggregation (e.g., ELK stack)
- Request/response logging at INFO level with duration_ms
- Sensitive data redacted: no passwords, no API keys in logs
- Story 1.3 configures structlog with dual renderers

**Logging Examples:**
```
# Console format (development)
2025-11-28T10:30:00Z [INFO ] server_starting host=127.0.0.1 port=8000 log_level=INFO
2025-11-28T10:30:03Z [INFO ] server_ready docs_url=http://127.0.0.1:8000/docs uptime_ms=2847

# JSON format (production with --json-logs)
{"event": "server_starting", "level": "info", "timestamp": "2025-11-28T10:30:00Z", "host": "127.0.0.1", "port": 8000}
{"event": "api_request", "level": "info", "method": "GET", "path": "/health", "status_code": 200, "duration_ms": 12}
```

**NFR-O2: Metrics (N/A for MVP, planned for Production Pack)**
- Epic 1 establishes logging foundation for future metrics
- Prometheus endpoint deferred to Phase 2
- Performance-critical events logged with duration_ms for manual analysis

**NFR-O3: Tracing (request IDs for correlation)**
- Every API request gets unique request_id (UUID)
- request_id logged with all events for that request
- Returned in response headers: `X-Request-ID`
- Enables end-to-end request tracing in logs
- Story 1.2 adds middleware to generate request IDs

## Dependencies and Integrations

### Runtime Dependencies

All dependencies are MIT-compatible and actively maintained:

**Default Installation (`pipx install mailreactor` or `pip install mailreactor`):**

All dependencies installed by default for full API server experience:

| Dependency | Version | License | Purpose | Story |
|------------|---------|---------|---------|-------|
| **imapclient** | >=3.0.0 | BSD-3 | IMAP client (unused in Epic 1, foundation for Epic 2) | N/A |
| **aiosmtplib** | >=3.0.0 | MIT | Async SMTP client (unused in Epic 1, foundation for Epic 3) | N/A |
| **fastapi** | >=0.122.0 | MIT | Web framework, OpenAPI generation, dependency injection | 1.2, 1.6 |
| **uvicorn[standard]** | latest | BSD-3 | ASGI server for FastAPI | 1.4 |
| **pydantic** | >=2.0.0 | MIT | Data validation (bundled with FastAPI) | 1.7 |
| **pydantic-settings** | latest | MIT | Environment-based configuration | 1.2 |
| **typer** | >=0.20.0 | MIT | CLI framework for server commands | 1.4 |
| **structlog** | latest | MIT/Apache-2.0 | Structured logging with console/JSON renderers | 1.3 |

**Library-Only Usage (No Optional Extra Required):**

Users who want library-only mode simply import from `mailreactor.core`:
```python
from mailreactor.core.events import EventEmitter  # Zero FastAPI imports
```

FastAPI is installed but never loaded unless user imports from `mailreactor.api`. This architectural separation (validated in SPIKE-001) enables dual-mode usage from a single installation.

**Python Version:** >=3.10 (modern async features, structural pattern matching, better type hints)

**Build System:** Hatchling (modern, PEP 517 compliant)

### Development Dependencies

| Dependency | Purpose | Story |
|------------|---------|-------|
| **pytest** | Test framework | All stories (TDD) |
| **pytest-asyncio** | Async test support | 1.2, 1.5 |
| **pytest-cov** | Coverage reporting | All stories |
| **httpx** | FastAPI TestClient | 1.5, 1.7 |
| **ruff** | Fast linter and formatter | 1.1 (code quality) |
| **mypy** | Static type checking | 1.1 (type safety) |
| **pre-commit** | Git hooks for code quality | 1.1 (Sprint 0 setup) |

### Integration Points

**No external integrations in Epic 1.** The foundation is self-contained:
- No database connections
- No email protocols (IMAP/SMTP unused until Epic 2+)
- No external APIs
- No cloud services

**Future Integration Hooks (established in Epic 1):**
- `api/dependencies.py` - Dependency injection pattern for future state management
- `config.py` - Settings model ready for database URLs, API keys, etc.
- `exceptions.py` - Exception hierarchy ready for connection errors
- `utils/logging.py` - Logging configured for future IMAP/SMTP operation logs

### Package Installation

**End User - Full API Server (Recommended):**
```bash
pipx install mailreactor
# Installs ALL dependencies (FastAPI, Uvicorn, IMAP, SMTP, CLI, logging)
# Creates isolated environment
# Adds 'mailreactor' command to PATH
# Ready to run: mailreactor start
```

**End User - Library Mode (Advanced):**
```bash
pip install mailreactor
# Same installation as above (all dependencies)
# But use only: from mailreactor.core import ...
# FastAPI installed but never imported
```

**Why No Separate Package?**
- Single installation is simpler (zero friction for main use case)
- Core library has zero runtime FastAPI coupling (validated in SPIKE-001)
- FastAPI only loads if user imports mailreactor.api
- Disk space savings minimal (~10MB for FastAPI vs 100+ MB for typical projects)

**Developer (from source):**
```bash
git clone https://github.com/yourusername/mailreactor.git
cd mailreactor/mailreactor
pip install -e ".[dev]"
# Installs runtime + development dependencies
# Editable mode for rapid iteration
```

**Dependency Constraints:**
- All versions pinned with `>=` to allow patch updates
- No upper bounds to avoid dependency hell
- Tested against latest versions in CI
- Update policy: Review security advisories weekly, update within 7 days

## Acceptance Criteria (Authoritative)

These are the atomic, testable acceptance criteria for Epic 1:

**AC-1:** Developer can install Mail Reactor via `pipx install mailreactor` without errors on macOS, Linux, and Windows 10+ with Python 3.10+

**AC-2:** Developer can run `mailreactor start` and server becomes operational (health endpoint responds 200 OK) within 3 seconds

**AC-3:** Health endpoint `GET /health` responds within 50ms p95 with status, version, uptime, and timestamp fields

**AC-4:** Server binds to `127.0.0.1:8000` by default (localhost only for security)

**AC-5:** Developer can override host and port via CLI flags: `mailreactor start --host 0.0.0.0 --port 9000`

**AC-6:** Developer can start in development mode with `mailreactor dev` and file changes trigger auto-reload

**AC-7:** Startup sequence logs configuration summary (host, port, log level, docs URL) to console

**AC-8:** Console logs are structured with timestamps, color-coded log levels, and key=value format

**AC-9:** Developer can enable JSON logging via `--json-logs` flag for production log aggregation

**AC-10:** Interactive API documentation is accessible at `http://localhost:8000/docs` (Swagger UI)

**AC-11:** Alternative API documentation is accessible at `http://localhost:8000/redoc` (ReDoc)

**AC-12:** OpenAPI 3.0 specification is accessible at `http://localhost:8000/openapi.json`

**AC-13:** All API error responses use standardized envelope: `{"error": {"code": "...", "message": "..."}}`

**AC-14:** Server returns 404 Not Found for undefined endpoints with clear error message

**AC-15:** Server handles exceptions gracefully, returning 500 Internal Server Error with generic message (no stack trace in response)

**AC-16:** All exceptions are logged with full context (stack trace in logs, not API responses)

**AC-17:** Server startup memory footprint is under 100MB RAM at idle

**AC-18:** Developer can configure log level via `--log-level DEBUG|INFO|WARN|ERROR` or `MAILREACTOR_LOG_LEVEL` environment variable

**AC-19:** Server can handle 10 concurrent health check requests without performance degradation

**AC-20:** Package has zero system dependencies (pure Python, no compiled extensions, no database)

**AC-21:** `mailreactor --help` displays CLI usage documentation with all commands and options

**AC-22:** `mailreactor --version` displays current package version

**AC-23:** Server logs "Server ready" message with API endpoint URLs after successful startup

**AC-24:** Every API request gets unique `X-Request-ID` header in response for traceability

**AC-25 (FR-099):** Core library can be imported without FastAPI: `from mailreactor.core import EventEmitter` succeeds with zero FastAPI modules loaded

**AC-26 (FR-102):** EventEmitter class exists in `core/events.py` with async handler registration via decorator pattern and concurrent execution via `asyncio.gather()`

**AC-27 (Package Structure):** `pipx install mailreactor` installs ALL dependencies (full API server experience) and `mailreactor start` command works immediately

**AC-28 (FR-099 Validation):** Despite installing FastAPI, core library (`from mailreactor.core import EventEmitter`) can be imported without loading FastAPI modules (validated via sys.modules check)

## Traceability Mapping

| AC | PRD FRs | Spec Section | Component/API | Test Idea |
|----|---------|--------------|---------------|-----------|
| AC-1 | FR-032 | Dependencies | pyproject.toml, package structure | Install test on fresh venv (macOS/Linux/Windows) |
| AC-2 | FR-034, FR-035, NFR-P1 | Workflows, Performance | cli/server.py, main.py | Time from CLI invocation to health endpoint 200 OK |
| AC-3 | FR-027, NFR-P2 | APIs, Performance | api/health.py | Load test health endpoint, measure p95 latency |
| AC-4 | FR-036, NFR-S3 | Security | config.py default binding | Verify default Settings.host="127.0.0.1" |
| AC-5 | FR-037 | APIs | cli/server.py | CLI test with --host/--port, verify server binds |
| AC-6 | FR-027, NFR-P1 | Workflows | cli/server.py | Start dev mode, modify file, verify reload |
| AC-7 | FR-028, FR-038 | Observability | utils/logging.py, cli/server.py | Capture stdout, verify config logged |
| AC-8 | FR-030, NFR-O1 | Observability | utils/logging.py | Parse log output, verify color/timestamp/format |
| AC-9 | NFR-O1 | Observability | utils/logging.py | Start with --json-logs, verify JSON format |
| AC-10 | FR-061 | APIs | main.py FastAPI docs | HTTP GET /docs, verify 200 OK, Swagger UI |
| AC-11 | FR-062 | APIs | main.py FastAPI redoc | HTTP GET /redoc, verify 200 OK, ReDoc |
| AC-12 | FR-060 | APIs | main.py FastAPI OpenAPI | HTTP GET /openapi.json, verify valid OpenAPI 3.0 |
| AC-13 | FR-056, FR-058 | Data Models | models/responses.py | Trigger error, verify response envelope format |
| AC-14 | FR-057 | APIs | main.py exception handlers | GET /nonexistent, verify 404 with error envelope |
| AC-15 | FR-031, NFR-R2 | Reliability | exceptions.py handlers | Raise exception in endpoint, verify 500 (no stack trace) |
| AC-16 | NFR-O1 | Observability | exceptions.py, logging.py | Trigger exception, verify stack trace in logs only |
| AC-17 | NFR-P4 | Performance | N/A | Measure process RSS after startup stabilization |
| AC-18 | FR-030, NFR-O1 | Observability | config.py, cli/server.py | Set log level via CLI/env, verify log output |
| AC-19 | NFR-P6 | Performance | main.py async endpoints | Concurrent load test with 10 parallel clients |
| AC-20 | FR-033 | Dependencies | pyproject.toml | Verify no system deps, install on clean system |
| AC-21 | N/A | N/A | cli/__init__.py Typer | Run --help, verify output completeness |
| AC-22 | N/A | N/A | cli/__init__.py | Run --version, verify matches pyproject.toml |
| AC-23 | FR-038 | Observability | cli/server.py | Capture logs, verify "Server ready" with URLs |
| AC-24 | NFR-O3 | Observability | main.py middleware | Make request, verify X-Request-ID in response |
| AC-25 | FR-099 | Services, Dependencies | core/events.py, pyproject.toml | Import core, check sys.modules for FastAPI absence |
| AC-26 | FR-102 | Services | core/events.py | Create EventEmitter, register handlers, emit event, verify concurrent execution |
| AC-27 | FR-032, FR-034 | Dependencies | pyproject.toml | Fresh venv, pipx install mailreactor, run mailreactor start, verify works |
| AC-28 | FR-099 | Services | core/events.py | Import mailreactor.core.events, check sys.modules has no fastapi.* entries |

## Risks, Assumptions, Open Questions

### Risks

**RISK-1: EventEmitter unused in Epic 1**
- **Impact:** Medium
- **Description:** EventEmitter implemented but no email features to emit events yet
- **Mitigation:** Validate with unit tests, demonstrate with mock events, actual usage comes in Epic 4
- **Status:** Accepted - foundation piece, validated in SPIKE-001

**RISK-2: Startup time target (3 seconds)**
- **Impact:** Medium  
- **Description:** Import overhead from FastAPI/Pydantic might slow cold start
- **Mitigation:** Lazy imports where possible, measure in Story 1.4, optimize if needed
- **Status:** Monitoring - will validate with performance tests

**RISK-3: pyproject.toml structure misunderstood**
- **Impact:** Low
- **Description:** Users might expect `mailreactor[api]` extra for full installation
- **Mitigation:** Clear documentation, pipx installation instructions prominent in README
- **Status:** Mitigated - current pyproject.toml structure is correct (all deps by default)

### Assumptions

**ASSUMPTION-1:** Users installing Mail Reactor want the full API server experience by default
- **Rationale:** Primary use case is REST API, library mode is advanced/embedded use
- **Validation:** Product positioning, competitor analysis (EmailEngine is API-only)
- **Impact if wrong:** Users complain about unnecessary dependencies (low risk, ~10MB FastAPI)

**ASSUMPTION-2:** Core/API separation prevents FastAPI from loading in library mode
- **Rationale:** Python imports are lazy - FastAPI only loads if imported
- **Validation:** SPIKE-001 confirmed zero FastAPI modules in sys.modules when importing core
- **Impact if wrong:** Library mode wouldn't be truly dependency-free (SPIKE validated this works)

**ASSUMPTION-3:** 8 stories can be completed in Sprint 1
- **Rationale:** Stories are focused on foundation, no email protocols yet
- **Validation:** Team velocity unknown (first sprint)
- **Impact if wrong:** Some stories spill to Sprint 2 (acceptable, Epic 1 is foundational)

### Open Questions

**QUESTION-1:** Should we add import-linter to CI to enforce core/API separation?
- **Context:** SPIKE-001 recommended this for automated boundary enforcement
- **Decision needed:** Sprint 1 or defer to Sprint 2?
- **Owner:** HC (Scrum Master) + Winston (Architect)
- **Recommendation:** Add in Story 1.1 (build configuration)

**QUESTION-2:** How much console log output is "too much" for developers?
- **Context:** Structured logging is verbose by design (key=value pairs)
- **Decision needed:** What level of detail for default INFO level?
- **Owner:** HC (user feedback) + Team (implementation)
- **Recommendation:** Start verbose, iterate based on user feedback

**QUESTION-3:** Should EventEmitter support sync handlers (non-async)?
- **Context:** SPIKE-001 prototype only supports async handlers
- **Decision needed:** Support both sync and async, or async-only?
- **Owner:** Winston (Architect)
- **Recommendation:** Async-only for MVP (simpler), add sync wrapper if users request it

## Test Strategy Summary

### Test Levels

**Unit Tests (Primary focus for Epic 1):**
- EventEmitter: Handler registration, concurrent execution, exception isolation
- Config/Settings: Environment variable loading, validation, defaults
- Exception hierarchy: Custom exceptions, HTTP status code mapping
- Logging configuration: Console renderer, JSON renderer, log level filtering
- **Coverage target:** >80% for core modules, >90% for utils

**Integration Tests:**
- FastAPI application startup: Middleware registration, router mounting
- Health endpoint: Response format, uptime calculation, performance
- Error handling: Exception handlers return correct HTTP responses
- **Coverage target:** All API endpoints, all error scenarios

**End-to-End Tests:**
- CLI commands: `mailreactor start`, `mailreactor dev`, `mailreactor --help`
- Full server lifecycle: Start, health check, graceful shutdown
- Development mode: File change detection, auto-reload
- **Coverage target:** All user-facing commands and workflows

**Performance Tests:**
- Startup time: Measure cold start to health endpoint response
- Health endpoint latency: Verify <50ms p95 target
- Memory footprint: Measure RSS after startup stabilization
- Concurrent requests: 10 parallel health checks without degradation
- **Baseline:** Establish metrics for future comparison

### Testing Tools

- **pytest:** Test framework with asyncio support (pytest-asyncio)
- **httpx:** FastAPI TestClient for API endpoint testing
- **pytest-benchmark:** Performance measurement and regression detection
- **pytest-cov:** Coverage reporting with HTML output
- **psutil:** Memory and resource monitoring

### Test Data & Fixtures

**Epic 1 has no email data** (no IMAP/SMTP yet), so fixtures are simple:
- Mock Settings objects with various configurations
- Mock Event instances for EventEmitter testing
- Mock FastAPI Request objects for dependency testing
- Temporary log files for logging output verification

### TDD Approach (from docs/tdd-guide.md)

1. **Write test first** (red)
2. **Implement minimal code** (green)
3. **Refactor** (clean)
4. **Repeat**

**Example (Story 1.3 - Logging):**
```python
# tests/unit/test_logging.py
def test_console_renderer_outputs_colored_logs():
    """Console renderer should use colors for log levels"""
    # RED: Write failing test
    logger = configure_logging(renderer="console")
    # ... assert output has ANSI color codes

# src/mailreactor/utils/logging.py
def configure_logging(renderer="console"):
    # GREEN: Implement just enough to pass
    # ... structlog configuration with ConsoleRenderer

# Then REFACTOR for readability, performance
```

### Continuous Integration

**GitHub Actions workflow (already configured in Sprint 0):**
- Run all tests on push/PR
- Generate coverage report
- Enforce >80% coverage threshold
- Pre-commit hooks (ruff, mypy, detect-secrets)
- Performance benchmarks tracked over time

### Test Organization

```
tests/
├── unit/
│   ├── test_events.py          # EventEmitter tests
│   ├── test_config.py          # Settings/config tests
│   ├── test_exceptions.py      # Exception hierarchy tests
│   └── test_logging.py         # Logging configuration tests
├── integration/
│   ├── test_app_initialization.py  # FastAPI app startup
│   ├── test_health_endpoint.py     # Health check integration
│   └── test_error_handling.py      # Exception handler integration
├── e2e/
│   ├── test_cli_commands.py        # CLI end-to-end tests
│   └── test_server_lifecycle.py    # Full startup/shutdown
└── performance/
    ├── test_startup_time.py        # Cold start performance
    ├── test_api_latency.py         # Health endpoint p95
    └── test_memory.py              # Memory footprint baseline
```
