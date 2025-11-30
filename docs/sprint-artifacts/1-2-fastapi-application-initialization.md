# Story 1.2: FastAPI Application Initialization

Status: drafted

## Story

As a developer,
I want the FastAPI application properly initialized with core middleware,
so that the API server can start and handle requests with proper error handling and logging.

## Acceptance Criteria

**Given** the project structure from Story 1.1  
**When** the FastAPI application is initialized  
**Then** `src/mailreactor/main.py` creates a FastAPI app instance with:
- App title: "Mail Reactor API"
- App version: "0.1.0"
- OpenAPI documentation enabled at `/docs` (Swagger UI)
- ReDoc documentation at `/redoc`
- CORS middleware configured (disabled by default, configurable)
- Exception handlers for custom `MailReactorException` hierarchy

**And** `src/mailreactor/exceptions.py` defines:
- Base `MailReactorException(message, status_code)` class
- Derived exceptions: `AccountError`, `ConnectionError`, `AuthenticationError`, `MessageError`, `StateError`
- Each exception includes HTTP status code mapping

**And** `src/mailreactor/config.py` defines Pydantic Settings model:
- `host: str = "127.0.0.1"` (localhost by default per FR-036)
- `port: int = 8000`
- `log_level: str = "INFO"`
- `api_key_header: str = "X-API-Key"`
- Environment variable prefix: `MAILREACTOR_`
- Support for `.env` file loading

**And** Application can be imported and initialized without errors

**And** EventEmitter class implemented in `src/mailreactor/core/events.py` with:
- `on(event_type: str)` decorator for registering async event handlers
- `emit(event: Event)` method for concurrent async handler execution via `asyncio.gather()`
- Transport-agnostic design (no FastAPI imports in core module)
- Exception isolation (handler failures don't crash emit)

**Prerequisites:** Story 1.1 (project structure exists)

## Tasks / Subtasks

- [ ] Implement EventEmitter class (AC: EventEmitter implementation, FR-102)
  - [ ] Create `src/mailreactor/core/events.py` module
  - [ ] Define `Event` dataclass with `event_type` and `data` fields
  - [ ] Implement `EventEmitter` class with `_handlers` dict storage
  - [ ] Implement `on(event_type)` decorator for handler registration
  - [ ] Implement `emit(event)` method with `asyncio.gather()` concurrent execution
  - [ ] Add exception isolation (return_exceptions=True in gather)
  - [ ] Verify zero FastAPI imports in module
  - [ ] Write unit tests for handler registration and concurrent execution

- [ ] Create exception hierarchy (AC: exceptions.py defines...)
  - [ ] Create `src/mailreactor/exceptions.py` module
  - [ ] Define `MailReactorException` base class with `message` and `status_code`
  - [ ] Define `AccountError(MailReactorException)` with 400 status code
  - [ ] Define `ConnectionError(MailReactorException)` with 503 status code
  - [ ] Define `AuthenticationError(MailReactorException)` with 401 status code
  - [ ] Define `MessageError(MailReactorException)` with 400 status code
  - [ ] Define `StateError(MailReactorException)` with 500 status code
  - [ ] Write unit tests for exception instantiation and inheritance

- [ ] Create Pydantic Settings configuration (AC: config.py defines...)
  - [ ] Create `src/mailreactor/config.py` module
  - [ ] Define `Settings` class inheriting from `BaseSettings`
  - [ ] Add `host: str = "127.0.0.1"` field
  - [ ] Add `port: int = 8000` field
  - [ ] Add `log_level: str = "INFO"` field
  - [ ] Add `api_key_header: str = "X-API-Key"` field
  - [ ] Configure `model_config` with `env_prefix="MAILREACTOR_"` and `env_file=".env"`
  - [ ] Create singleton `settings` instance
  - [ ] Write unit tests for settings loading and environment variable override

- [ ] Initialize FastAPI application (AC: main.py creates FastAPI app)
  - [ ] Create `src/mailreactor/main.py` module
  - [ ] Create `create_app()` factory function
  - [ ] Initialize FastAPI app with title "Mail Reactor API" and version "0.1.0"
  - [ ] Configure OpenAPI URLs: `/docs`, `/redoc`, `/openapi.json`
  - [ ] Add CORS middleware with configurable origins (disabled by default)
  - [ ] Register exception handler for `MailReactorException`
  - [ ] Register exception handler for generic `Exception` (500 errors)
  - [ ] Create app instance at module level for uvicorn entry point
  - [ ] Write integration tests for app initialization and exception handlers

- [ ] Add request ID middleware (AC: NFR-O3 tracing)
  - [ ] Create `src/mailreactor/api/dependencies.py` module
  - [ ] Implement `request_id_middleware` to generate unique request IDs
  - [ ] Inject request_id into response headers (`X-Request-ID`)
  - [ ] Bind request_id to structlog context for correlation
  - [ ] Register middleware in `main.py` app initialization
  - [ ] Write integration tests for request ID generation and propagation

- [ ] Testing and validation (AC: Application can be imported without errors)
  - [ ] Write unit test: Import main.py successfully
  - [ ] Write unit test: Verify app title and version
  - [ ] Write integration test: Start test server and verify /docs accessible
  - [ ] Write integration test: Trigger custom exception and verify error response
  - [ ] Write integration test: Verify CORS middleware behavior
  - [ ] Verify core module has zero FastAPI imports (FR-099 validation)

## Dev Notes

### Learnings from Previous Story

**From Story 1-1-project-structure-and-build-configuration (Status: done)**

- **Package Structure Established**: All module directories created (core/, api/, models/, cli/, utils/) with proper __init__.py files
  - Use existing structure: `src/mailreactor/core/` for EventEmitter, `src/mailreactor/` for main.py, config.py, exceptions.py
- **Build Configuration Complete**: pyproject.toml configured with all dependencies
  - FastAPI 0.122.0, Pydantic v2, pydantic-settings, structlog already installed
- **Zero FastAPI Coupling in Core**: Critical validation passed - importing `mailreactor.core` does NOT load FastAPI modules
  - MUST maintain this separation: EventEmitter in `core/events.py` cannot import from `mailreactor.api` or FastAPI
- **No Review Items Pending**: Previous story approved with zero action items

[Source: stories/1-1-project-structure-and-build-configuration.md#Dev-Agent-Record]

### Architecture Patterns and Constraints

**ADR-001: FastAPI Web Framework**
- Use FastAPI 0.122.0 for automatic OpenAPI generation, native async support, and Pydantic integration
- All API endpoints follow FastAPI decorator patterns
- Enable `/docs` (Swagger UI) and `/redoc` (ReDoc) for interactive documentation

**ADR-007: Event-Driven Architecture (FR-102 Foundation)**
- EventEmitter class establishes transport-agnostic event system in `core/events.py`
- Validated in SPIKE-001: Core module has zero FastAPI coupling
- Single internal pipeline: structured events → async handlers → concurrent execution
- Actual email events (message.received, message.sent) will be emitted in Epic 4

**Error Handling Pattern (Architecture sections "Error Handling Pattern", "API Contracts")**
- Custom exception hierarchy with base `MailReactorException`
- FastAPI exception handlers return consistent error responses:
  ```json
  {
    "error": {
      "code": "ERROR_CODE",
      "message": "Human-readable message",
      "details": {...}
    }
  }
  ```
- HTTP status codes mapped per exception type (401/400/500/503)
- Generic errors in production (no stack traces in responses), detailed in development

**Configuration Pattern (Architecture sections "Configuration Pattern")**
- Pydantic Settings for type-safe environment variable support
- Prefix: `MAILREACTOR_` for all environment variables
- `.env` file loading via pydantic-settings
- Defaults favor security: localhost binding (`127.0.0.1`), INFO log level

**NFR-O3: Request Tracing**
- Generate unique `request_id` (UUID) per API request
- Inject into response headers: `X-Request-ID`
- Bind to structlog context for log correlation (implemented in Story 1.3)

**NFR-P6: Concurrent Connections**
- FastAPI async endpoints support concurrent request handling
- Target: 10 simultaneous requests for MVP without degradation

[Source: docs/architecture.md#Technology-Stack-Details, #Implementation-Patterns]
[Source: docs/sprint-artifacts/tech-spec-epic-1.md#Detailed-Design]
[Source: docs/ADR-007-event-driven-architecture.md]

### Project Structure Notes

**File Locations (per unified project structure):**
```
src/mailreactor/
├── main.py                  # FastAPI app factory
├── config.py                # Pydantic Settings
├── exceptions.py            # Custom exception hierarchy
├── core/
│   ├── __init__.py
│   └── events.py            # EventEmitter (FR-102)
└── api/
    ├── __init__.py
    └── dependencies.py      # Request ID middleware, future auth
```

**Import Boundaries (CRITICAL - FR-099 Dual-Mode Architecture):**
- `core/events.py` MUST NOT import: FastAPI, Pydantic HTTP models, `mailreactor.api.*`
- `core/events.py` CAN import: stdlib (asyncio, dataclasses, typing), `mailreactor.models.*`
- Validation: After implementation, verify `import mailreactor.core.events` does NOT load `fastapi` in `sys.modules`

**Testing Structure:**
```
tests/
├── unit/
│   ├── test_events.py          # EventEmitter unit tests
│   ├── test_exceptions.py      # Exception hierarchy tests
│   └── test_config.py          # Settings validation tests
└── integration/
    ├── test_app_initialization.py  # FastAPI app startup
    └── test_error_handling.py      # Exception handler integration
```

[Source: docs/architecture.md#Project-Structure]

### Technical Notes

**EventEmitter Implementation (FR-102):**
```python
# src/mailreactor/core/events.py
from dataclasses import dataclass
from typing import Callable, Awaitable, Any
import asyncio

@dataclass
class Event:
    """Base event class"""
    event_type: str
    data: dict[str, Any]

class EventEmitter:
    """Transport-agnostic event dispatcher"""
    
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

**FastAPI App Factory Pattern:**
```python
# src/mailreactor/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config import settings
from .exceptions import MailReactorException

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="Mail Reactor API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # CORS middleware (disabled by default for security)
    if settings.cors_enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
    
    # Exception handlers
    @app.exception_handler(MailReactorException)
    async def mailreactor_exception_handler(request: Request, exc: MailReactorException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.__class__.__name__.upper(),
                    "message": exc.message
                }
            }
        )
    
    return app

app = create_app()  # Module-level instance for uvicorn
```

**Pydantic Settings Pattern:**
```python
# src/mailreactor/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Server
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "INFO"
    
    # Security
    api_key_header: str = "X-API-Key"
    
    # CORS (disabled by default)
    cors_enabled: bool = False
    allowed_origins: list[str] = ["*"]
    
    model_config = SettingsConfigDict(
        env_prefix="MAILREACTOR_",
        env_file=".env",
        case_sensitive=False
    )

settings = Settings()
```

**Testing Best Practices:**
- Use `from fastapi.testclient import TestClient` for API endpoint tests
- Mock external dependencies (IMAP/SMTP) at integration test level
- Unit test EventEmitter with synthetic events (no email content yet)
- Validate exception handlers return correct HTTP status codes and error envelopes

[Source: docs/architecture.md#Implementation-Patterns]
[Source: docs/sprint-artifacts/tech-spec-epic-1.md#Data-Models-and-Contracts]

### References

- **PRD Requirements**: [Source: docs/prd.md - FR-055 to FR-062 (API Standards)]
- **Epic Breakdown**: [Source: docs/epics.md#Story-1.2-FastAPI-Application-Initialization]
- **Architecture ADR-001**: [Source: docs/architecture.md#ADR-001-Use-FastAPI-for-Web-Framework]
- **Architecture ADR-007**: [Source: docs/ADR-007-event-driven-architecture.md]
- **Tech Spec Epic 1**: [Source: docs/sprint-artifacts/tech-spec-epic-1.md#Detailed-Design]
- **SPIKE-001 Validation**: [Source: docs/sprint-artifacts/SPIKE-001-core-api-separation.md]
- **Testing Standards**: [Source: docs/tdd-guide.md]

## Dev Agent Record

### Context Reference

- `docs/sprint-artifacts/1-2-fastapi-application-initialization.context.xml`

### Agent Model Used

<!-- Agent model will be recorded during implementation -->

### Debug Log References

<!-- Implementation debug logs will be added during development -->

### Completion Notes List

<!-- Completion notes will be added after implementation:
- New patterns/services created
- Architectural decisions made
- Technical debt deferred
- Warnings for next story
- Interfaces/methods for reuse
-->

### File List

<!-- Files created/modified will be tracked here:
- NEW: Files created in this story
- MODIFIED: Files changed in this story
- DELETED: Files removed in this story
-->

## Change Log

**2025-11-30:** Story 1.2 drafted by SM agent (Bob)
- Extracted requirements from Tech Spec Epic 1 and epics.md
- Incorporated learnings from previous story 1-1 (package structure, zero FastAPI coupling validation)
- Added EventEmitter implementation (FR-102) per ADR-007
- Added comprehensive architecture references and citations
- Status: drafted, ready for review or story-context generation
