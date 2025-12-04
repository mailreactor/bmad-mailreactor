# Story 1.7: Response Envelope and Error Handling Standards

Status: drafted

## Story

As a developer,
I want consistent API response formats and error handling,
so that client applications can reliably parse responses and handle errors gracefully.

## Acceptance Criteria

**Given** the FastAPI application from previous stories  
**When** implementing response standards  
**Then** `src/mailreactor/models/responses.py` defines:
- `SuccessResponse[T]` generic model: `{"data": T, "meta": {"request_id": str, "timestamp": str}}`
- `ErrorResponse` model: `{"detail": str, "error_code": str, "request_id": str}`
- Meta includes ISO 8601 UTC timestamp (FR-059)
- Request ID generated per request for tracing

**And** FastAPI exception handlers in `main.py` convert:
- `MailReactorException` → HTTP status + `ErrorResponse`
- Generic `Exception` → HTTP 500 + generic error message (no stack trace in production)
- Validation errors → HTTP 400 + field-specific details

**And** All API endpoints use standard HTTP status codes:
- 200 OK: Successful GET/operation
- 201 Created: Successful POST creating resource
- 400 Bad Request: Invalid input
- 401 Unauthorized: Missing/invalid authentication
- 404 Not Found: Resource not found
- 500 Internal Server Error: Unexpected errors

**And** Error responses never expose:
- Stack traces (production mode)
- Sensitive data (passwords, API keys)
- Internal system paths or implementation details

**And** All timestamps use ISO 8601 format with UTC timezone (e.g., `2025-11-25T10:00:00Z`)

**And** Request ID middleware injects unique `request_id` into structlog context and response headers

**Prerequisites:** Story 1.2 (exception hierarchy), Story 1.5 (health endpoint to test)

## Tasks / Subtasks

- [ ] Define response models in `models/responses.py` (AC: SuccessResponse, ErrorResponse)
  - [ ] Create `ErrorDetail` model with `code`, `message`, `details` fields
  - [ ] Create `ErrorResponse` model with `error: ErrorDetail` field
  - [ ] Create generic `SuccessResponse[T]` with `data: T` and `meta` fields
  - [ ] Create `ResponseMeta` model with `request_id` and `timestamp` (ISO 8601 UTC)
  - [ ] Add Pydantic examples to all models for OpenAPI docs

- [ ] Refactor existing exception handlers in `main.py` to use Pydantic models (AC: convert to standard responses)
  - [ ] Refactor `MailReactorException` handler (lines 96-123) to use `ErrorResponse.model_dump()`
  - [ ] Refactor generic `Exception` handler (lines 125-150) to use `ErrorResponse.model_dump()`
  - [ ] Add NEW handler for `RequestValidationError` → HTTP 400 + field details in `ErrorDetail.details`
  - [ ] Verify all handlers still log full context before converting to response
  - [ ] Verify no stack traces in response content (already implemented)

- [ ] Update health endpoint to use SuccessResponse envelope (AC: consistent format)
  - [ ] Modify `api/health.py` to return `SuccessResponse[HealthResponse]`
  - [ ] Access `request_id` from existing middleware: `request.state.request_id`
  - [ ] Use `SuccessResponse.create()` factory method with request_id
  - [ ] Update `response_model` in route decorator to `SuccessResponse[HealthResponse]`
  - [ ] Verify OpenAPI spec shows new envelope format with `data` and `meta` fields

- [ ] Write unit tests for new response models (AC: models validated)
  - [ ] Test `ErrorResponse` and `ErrorDetail` serialization
  - [ ] Test `SuccessResponse[T]` generic type handling with `HealthResponse`
  - [ ] Test `ResponseMeta` timestamp format (ISO 8601 with UTC)
  - [ ] Test Pydantic examples render correctly in OpenAPI spec

- [ ] Update existing integration tests for exception handling (AC: handlers use Pydantic models)
  - [ ] Update `test_error_handling.py` to verify Pydantic model structure (tests already pass)
  - [ ] Add test for new `RequestValidationError` handler with field details
  - [ ] Verify existing tests still pass after Pydantic model refactor
  - [ ] Add test for `ErrorDetail.details` field (validation errors)

- [ ] Add integration tests for SuccessResponse envelope (AC: consistent format)
  - [ ] Test health endpoint returns `SuccessResponse` envelope with `data` and `meta`
  - [ ] Test `meta.request_id` matches `X-Request-ID` header (from existing middleware)
  - [ ] Test `meta.timestamp` is ISO 8601 UTC format
  - [ ] Verify request_id unique per request (existing middleware behavior)

## Dev Notes

### Learnings from Previous Story

**From Story 1-6-openapi-documentation-auto-generation (Status: done)**

- **Minimal contextual documentation**: Users at /docs don't need redundant examples
- **Inline over external files**: Short content (6 lines) doesn't justify filesystem I/O
- **Remove internal jargon**: NFR-P2, "canary" don't belong in user-facing docs
- **FastAPI app factory**: `create_app()` in `main.py` returns configured FastAPI app
- **OpenAPI spec enhanced**: All metadata (title, description, version, contact, license) configured
- **Health endpoint exists**: Working endpoint at `GET /health` returning `HealthResponse`

[Source: stories/1-6-openapi-documentation-auto-generation.md#Dev-Agent-Record]

### Current Implementation State (Before Story 1.7)

**✅ Already Implemented:**

1. **Request ID Middleware** (`api/middleware.py:RequestIDMiddleware`):
   - Generates unique UUID per request
   - Injects into `request.state.request_id`
   - Binds to structlog context
   - Adds `X-Request-ID` response header
   - Already registered in `main.py` (line 67)

2. **Exception Handlers** (`main.py`):
   - `MailReactorException` handler (lines 96-123) - returns error dict
   - Generic `Exception` handler (lines 125-150) - returns error dict
   - Both log full context and never expose stack traces
   - Tests exist in `test_error_handling.py` and pass

3. **Exception Hierarchy** (`exceptions.py`):
   - `MailReactorException` base class with `message` and `status_code`
   - Derived exceptions: `AccountError`, `ConnectionError`, `AuthenticationError`, `MessageError`, `StateError`
   - HTTP status code mapping working correctly

**❌ What Story 1.7 Adds:**

1. **Pydantic Response Models** (new in `models/responses.py`):
   - `ResponseMeta` - request_id and timestamp
   - `SuccessResponse[T]` - Generic wrapper for success responses
   - `ErrorDetail` - Error code, message, details
   - `ErrorResponse` - Standard error envelope

2. **Refactor Existing Handlers** (update `main.py`):
   - Convert inline dicts to Pydantic models with `.model_dump()`
   - Add `RequestValidationError` handler (new)
   - Keep existing logging and security (no stack traces)

3. **Update Health Endpoint** (update `api/health.py`):
   - Wrap `HealthResponse` in `SuccessResponse` envelope
   - Use existing middleware's `request.state.request_id`
   - Change return type to `SuccessResponse[HealthResponse]`

**Key Insight:** This is mostly a **refactor to use Pydantic models** rather than building from scratch. Exception handlers and middleware already work!

### Architecture Patterns and Constraints

**Error Handling Pattern (from Architecture):**

Exception hierarchy established in Story 1.2:

```python
# exceptions.py
class MailReactorException(Exception):
    """Base exception for all Mail Reactor errors"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class IMAPConnectionError(MailReactorException):
    """IMAP connection failed"""
    def __init__(self, message: str):
        super().__init__(message, status_code=503)

class AuthenticationError(MailReactorException):
    """Authentication failed"""
    def __init__(self, message: str):
        super().__init__(message, status_code=401)

class AccountNotFoundError(MailReactorException):
    """Account not found in state"""
    def __init__(self, account_id: str):
        super().__init__(f"Account {account_id} not found", status_code=404)
```

**Exception Handler Refactor (Story 1.7 Changes):**

**Current state (main.py lines 96-150):**
```python
# BEFORE Story 1.7 - Inline dicts
@app.exception_handler(MailReactorException)
async def mailreactor_exception_handler(request: Request, exc: MailReactorException):
    logger.warning(...)
    return JSONResponse(
        status_code=exc.status_code,
        content={  # ← Inline dict (no Pydantic)
            "error": {
                "code": exc.__class__.__name__.upper(),
                "message": exc.message,
            }
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(..., exc_info=True)
    return JSONResponse(
        status_code=500,
        content={  # ← Inline dict (no Pydantic)
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
            }
        }
    )
```

**After Story 1.7 - Pydantic models:**
```python
# AFTER Story 1.7 - Use ErrorResponse model
from .models.responses import ErrorResponse, ErrorDetail

@app.exception_handler(MailReactorException)
async def mailreactor_exception_handler(request: Request, exc: MailReactorException):
    logger.warning(...)
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(  # ← Pydantic model
            error=ErrorDetail(
                code=exc.__class__.__name__.upper(),
                message=exc.message,
                details=None
            )
        ).model_dump()  # ← Required for JSONResponse
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(..., exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(  # ← Pydantic model
            error=ErrorDetail(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected error occurred",
                details=None
            )
        ).model_dump()  # ← Required for JSONResponse
    )

# NEW handler for Pydantic validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("validation_error", errors=exc.errors())
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message="Invalid request parameters",
                details={"errors": exc.errors()}  # ← Field-specific errors
            )
        ).model_dump()
    )
```

**Key changes:**
1. Replace inline dicts with `ErrorResponse(error=ErrorDetail(...)).model_dump()`
2. Add NEW `RequestValidationError` handler (doesn't exist yet)
3. Keep all existing logging and security (no stack traces)
4. `.model_dump()` required because `JSONResponse.content` expects dict, not Pydantic model

**Request ID Middleware (Already Implemented):**

The middleware already exists at `api/middleware.py:RequestIDMiddleware` and is registered in `main.py` (line 67).

**Current implementation:**
```python
# api/middleware.py (lines 21-86) - ALREADY EXISTS
class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to generate unique request IDs for tracing."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id  # ← Access via request.state
        bind_context(request_id=request_id)     # ← Structlog context
        
        # ... process request, log, add header ...
        
        response.headers["X-Request-ID"] = request_id
        return response
```

**How to use in endpoints (Story 1.7):**
```python
# api/health.py
@router.get("/health", response_model=SuccessResponse[HealthResponse])
async def get_health(request: Request) -> SuccessResponse[HealthResponse]:
    health_data = HealthResponse(...)
    
    # Get request_id from middleware (stored in request.state)
    request_id = request.state.request_id
    
    # Use factory method to create envelope with request_id
    return SuccessResponse.create(data=health_data, request_id=request_id)
```

**No changes needed to middleware** - just use it!

[Source: docs/architecture.md#Error-Handling-Pattern]
[Source: docs/architecture.md#Implementation-Patterns]

**Response Models (from Architecture and Tech Spec):**

```python
# models/responses.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone
from typing import Generic, TypeVar, Optional, Any, Dict

T = TypeVar('T')

class ResponseMeta(BaseModel):
    """Metadata included in all API responses"""
    request_id: str = Field(
        description="Unique request identifier for tracing",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    timestamp: datetime = Field(
        description="Response timestamp in UTC (ISO 8601)",
        example="2025-12-04T10:30:45Z"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2025-12-04T10:30:45Z"
            }
        }
    )

class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response envelope"""
    data: T = Field(description="Response data")
    meta: ResponseMeta = Field(description="Response metadata")
    
    @classmethod
    def create(cls, data: T, request_id: str):
        """Factory method to create success response with current timestamp"""
        return cls(
            data=data,
            meta=ResponseMeta(
                request_id=request_id,
                timestamp=datetime.now(timezone.utc)
            )
        )

class ErrorDetail(BaseModel):
    """Error detail structure"""
    code: str = Field(
        description="Machine-readable error code",
        example="ACCOUNT_NOT_FOUND"
    )
    message: str = Field(
        description="Human-readable error message",
        example="Account acc_123 not found"
    )
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional error context (validation errors, field details)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "ACCOUNT_NOT_FOUND",
                "message": "Account acc_123 not found",
                "details": None
            }
        }
    )

class ErrorResponse(BaseModel):
    """Standard error response envelope"""
    error: ErrorDetail = Field(description="Error details")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request parameters",
                    "details": {
                        "errors": [
                            {
                                "loc": ["body", "email"],
                                "msg": "value is not a valid email address",
                                "type": "value_error.email"
                            }
                        ]
                    }
                }
            }
        }
    )
```

**Update health endpoint to use envelope:**

**Current state (api/health.py lines 28-47):**
```python
# BEFORE Story 1.7 - Returns HealthResponse directly
@router.get("/health", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    uptime = (datetime.utcnow() - _app_start_time).total_seconds()
    
    return HealthResponse(  # ← Flat structure (no envelope)
        status="healthy",
        version=get_app_version(),
        uptime_seconds=uptime,
        timestamp=datetime.utcnow(),
    )
```

**After Story 1.7 - Wrapped in SuccessResponse:**
```python
# AFTER Story 1.7 - Returns SuccessResponse envelope
from fastapi import Request  # ← Add Request parameter
from ..models.responses import SuccessResponse

@router.get(
    "/health",
    response_model=SuccessResponse[HealthResponse],  # ← Changed response model
    status_code=200,
    summary="Check API health and uptime",
    description="Returns system status, version, and uptime. No authentication required.",
    tags=["System"],
)
async def get_health(request: Request) -> SuccessResponse[HealthResponse]:  # ← Add Request param
    """Check API health and uptime.
    
    Returns system status, version, and uptime in seconds.
    No authentication required - always accessible for monitoring.
    """
    uptime = (datetime.utcnow() - _app_start_time).total_seconds()
    
    health_data = HealthResponse(
        status="healthy",
        version=get_app_version(),
        uptime_seconds=uptime,
        timestamp=datetime.utcnow(),
    )
    
    # Get request_id from existing middleware (stored in request.state)
    request_id = request.state.request_id
    
    # Use factory method to wrap in envelope
    return SuccessResponse.create(data=health_data, request_id=request_id)
    # FastAPI auto-serializes (no .model_dump() needed for endpoint returns)
```

**Key changes:**
1. Add `request: Request` parameter to access middleware data
2. Change `response_model` to `SuccessResponse[HealthResponse]`
3. Get `request_id` from `request.state.request_id` (set by existing middleware)
4. Wrap `HealthResponse` in `SuccessResponse.create()`
5. **No `.model_dump()` needed** - FastAPI auto-serializes endpoint returns

[Source: docs/sprint-artifacts/tech-spec-epic-1.md#Data-Models-and-Contracts]
[Source: docs/epics.md#Story-1.7]

### Project Structure Notes

**Modified Files (Story 1.7):**
```
src/mailreactor/
├── models/
│   └── responses.py          # MODIFIED: Add SuccessResponse[T], ErrorResponse, ErrorDetail, ResponseMeta
├── main.py                   # MODIFIED: Refactor exception handlers to use Pydantic models, add RequestValidationError handler
└── api/
    └── health.py             # MODIFIED: Wrap return in SuccessResponse envelope, add Request parameter
```

**No New Files:**
- Request ID middleware already exists at `api/middleware.py`
- Exception handlers already exist in `main.py` (just refactoring)

**Dependencies:**
- None - uses existing FastAPI, Pydantic, structlog, uuid (stdlib)

**Existing Infrastructure (Already Implemented):**
- ✅ `api/middleware.py:RequestIDMiddleware` - generates UUID, binds context, adds header
- ✅ `main.py` exception handlers (lines 96-150) - need Pydantic model refactor
- ✅ `exceptions.py` hierarchy - complete with status codes
- ✅ `test_error_handling.py` - existing tests validate structure

[Source: docs/architecture.md#Project-Structure]

### Technical Notes

**Key Implementation Requirements:**

1. **Response Envelope Consistency (FR-056)**:
   - All success responses use `SuccessResponse[T]` wrapper
   - All error responses use `ErrorResponse` wrapper
   - Consistent `meta` field with `request_id` and `timestamp`

2. **ISO 8601 Timestamps (FR-059)**:
   - Always use UTC timezone: `datetime.now(timezone.utc)`
   - Format example: `"2025-12-04T10:30:45Z"`
   - Pydantic serializes datetime to ISO 8601 automatically

3. **Request Tracing (NFR-O3)**:
   - Unique request_id per request via UUID4
   - Inject into structlog context for all logs
   - Return in `X-Request-ID` response header
   - Include in response `meta.request_id` field

4. **Error Codes (FR-058)**:
   - Machine-readable: `ACCOUNT_NOT_FOUND`, `VALIDATION_ERROR`
   - Derived from exception class name: `AccountNotFoundError` → `ACCOUNT_NOT_FOUND_ERROR`
   - Human-readable message separate from code
   - Optional `details` field for validation errors

5. **Security (NFR-S1, NFR-R2)**:
   - Never include stack traces in responses
   - Log full exception details server-side
   - Generic message for 500 errors: "An unexpected error occurred"
   - Never log passwords, API keys, or sensitive data

6. **HTTP Status Codes (FR-057)**:
   - 200 OK: Successful GET/operation
   - 201 Created: Successful POST creating resource
   - 400 Bad Request: Invalid input (validation)
   - 401 Unauthorized: Missing/invalid auth
   - 404 Not Found: Resource not found
   - 500 Internal Server Error: Unexpected errors
   - 503 Service Unavailable: External service failures (IMAP/SMTP)

**Testing Strategy:**

Per team constraint: "✅ ONLY test functionality WE have added"

- ✅ Test our exception handlers convert to correct responses
- ✅ Test our request ID middleware generates unique IDs
- ✅ Test our response models serialize correctly
- ❌ Don't test FastAPI exception handling machinery
- ❌ Don't test Pydantic validation (test our models only)
- ❌ Don't test uuid.uuid4() generates valid UUIDs

**Integration Test Examples:**

```python
# tests/integration/test_error_handling.py
import pytest
from fastapi.testclient import TestClient
from mailreactor.main import create_app
from mailreactor.exceptions import AccountNotFoundError

client = TestClient(create_app())

def test_mailreactor_exception_handler():
    """Test custom exception converts to ErrorResponse"""
    # Trigger AccountNotFoundError via endpoint
    response = client.get("/accounts/nonexistent")
    
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "ACCOUNT_NOT_FOUND_ERROR"
    assert "acc_" in data["error"]["message"]
    assert response.headers.get("X-Request-ID") is not None

def test_validation_error_handler():
    """Test Pydantic validation error returns field details"""
    response = client.post(
        "/accounts",
        json={"email": "invalid-email", "password": "test123"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "details" in data["error"]
    assert "errors" in data["error"]["details"]

def test_generic_exception_handler():
    """Test unexpected exception returns generic 500 without stack trace"""
    # Trigger unhandled exception via test endpoint
    response = client.get("/test/trigger-error")
    
    assert response.status_code == 500
    data = response.json()
    assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
    assert "unexpected error" in data["error"]["message"].lower()
    # Verify no stack trace in response
    assert "Traceback" not in str(data)
```

```python
# tests/integration/test_request_id.py
def test_request_id_in_response_header():
    """Test X-Request-ID header present in all responses"""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    request_id = response.headers["X-Request-ID"]
    assert len(request_id) == 36  # UUID4 format

def test_request_id_unique_per_request():
    """Test different request IDs for different requests"""
    response1 = client.get("/health")
    response2 = client.get("/health")
    
    id1 = response1.headers["X-Request-ID"]
    id2 = response2.headers["X-Request-ID"]
    assert id1 != id2

def test_request_id_in_response_meta():
    """Test request_id included in response meta field"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "meta" in data
    assert "request_id" in data["meta"]
    
    # Should match X-Request-ID header
    assert data["meta"]["request_id"] == response.headers["X-Request-ID"]
```

[Source: docs/architecture.md#Testing-Pattern]
[Source: docs/hc-standards.md#Testing-Principle]

### References

- **PRD Requirements**: [Source: docs/prd.md - FR-055 (JSON content type), FR-056 (Consistent envelope), FR-057 (Standard HTTP codes), FR-058 (Error details), FR-059 (ISO 8601 timestamps)]
- **Epic Breakdown**: [Source: docs/epics.md#Story-1.7-Response-Envelope-and-Error-Handling-Standards]
- **Architecture Patterns**: [Source: docs/architecture.md#Error-Handling-Pattern, #Implementation-Patterns]
- **Tech Spec**: [Source: docs/sprint-artifacts/tech-spec-epic-1.md#Data-Models-and-Contracts]
- **Previous Story**: [Source: docs/sprint-artifacts/1-6-openapi-documentation-auto-generation.md]
- **Team Standards**: [Source: docs/hc-standards.md]
- **FastAPI Exception Handlers**: https://fastapi.tiangolo.com/tutorial/handling-errors/
- **Pydantic Generic Models**: https://docs.pydantic.dev/latest/concepts/models/#generic-models
- **Starlette Middleware**: https://www.starlette.io/middleware/

## Dev Agent Record

### Context Reference

docs/sprint-artifacts/1-7-response-envelope-and-error-handling-standards.context.xml

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

## Change Log

**2025-12-04:** Story 1.7 updated after HC review - corrected implementation scope
- **Correction 1:** Request ID middleware already exists at `api/middleware.py` (don't recreate)
- **Correction 2:** Exception handlers already exist in `main.py` lines 96-150 (refactor, not create)
- **Correction 3:** Tests already exist in `test_error_handling.py` (update, not write from scratch)
- **Clarification:** `.model_dump()` required for `JSONResponse.content` (dict needed), but NOT for FastAPI endpoint returns (auto-serialization)
- **Scope reduction:** This is primarily a Pydantic model refactor, not building from scratch
- Updated tasks to reflect "refactor existing" vs "implement new"
- Added "Current Implementation State" section documenting what exists
- Simplified middleware section (just use it, don't recreate)
- Updated exception handler examples to show BEFORE/AFTER
- Updated health endpoint example to show BEFORE/AFTER

**2025-12-04:** Story 1.7 drafted by SM agent via create-story workflow (initial version)
- Extracted requirements from Epic 1 Story 1.7 (epics.md lines 457-505)
- Incorporated learnings from Story 1.6 (OpenAPI metadata established)
- Key deliverables: SuccessResponse[T], ErrorResponse, request_id in envelopes
- Manual verification approach for consistent API format
- Status: drafted, ready for implementation (scope corrected after review)
