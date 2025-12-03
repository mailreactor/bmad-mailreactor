# Story 1.5: Health Check Endpoint

Status: drafted

## Story

As a developer,
I want a `/health` endpoint to verify Mail Reactor is operational,
so that I can monitor system status and validate successful deployment.

## Acceptance Criteria

**Given** the running FastAPI server from Story 1.4  
**When** implementing the health check endpoint  
**Then** `src/mailreactor/api/health.py` provides:
- FastAPI router with `GET /health` endpoint
- Returns HTTP 200 OK when system is healthy
- Response includes: `{"status": "healthy", "version": "0.1.0", "uptime_seconds": <seconds>}`
- Calculates uptime from application start time
- Response time under 50ms p95 (NFR-P2)

**And** `src/mailreactor/main.py` registers the health router

**And** Health endpoint is accessible at `http://localhost:8000/health`

**And** Health endpoint does NOT require authentication (always accessible for monitoring)

**And** Health check logs as DEBUG level (not INFO) to avoid log noise

**Prerequisites:** Story 1.4 (server running)

## Tasks / Subtasks

- [ ] Create health check router module (AC: api/health.py provides...)
  - [ ] Create `src/mailreactor/api/` directory if not exists
  - [ ] Create `src/mailreactor/api/__init__.py`
  - [ ] Create `src/mailreactor/api/health.py` module
  - [ ] Import FastAPI Router, Pydantic BaseModel
  - [ ] Import datetime, timedelta for uptime calculation
  - [ ] Add type hints for all function parameters and return types

- [ ] Define health response model (AC: response includes status, version, uptime)
  - [ ] Create `HealthResponse` Pydantic model in health.py
  - [ ] Add `status: str` field (values: "healthy", "degraded", "unhealthy")
  - [ ] Add `version: str` field (read from package metadata)
  - [ ] Add `uptime_seconds: float` field
  - [ ] Add `timestamp: datetime` field (UTC)
  - [ ] Write unit test for HealthResponse model validation

- [ ] Track application start time (AC: calculates uptime from application start)
  - [ ] Add `app_start_time: datetime` to main.py module level
  - [ ] Set app_start_time = datetime.utcnow() at module load
  - [ ] Make app_start_time accessible to health endpoint
  - [ ] Consider using app.state for start time storage
  - [ ] Write unit test for start time initialization

- [ ] Implement GET /health endpoint (AC: returns HTTP 200 OK)
  - [ ] Create FastAPI APIRouter instance
  - [ ] Define `get_health()` async function with @router.get("/health")
  - [ ] Calculate uptime: (datetime.utcnow() - app_start_time).total_seconds()
  - [ ] Read version from package metadata or settings
  - [ ] Construct HealthResponse(status="healthy", version=..., uptime_seconds=...)
  - [ ] Return response with status_code=200
  - [ ] Add response_model=HealthResponse to decorator
  - [ ] Write integration test for GET /health endpoint

- [ ] Register health router in FastAPI app (AC: main.py registers router)
  - [ ] Import health router in main.py: `from .api.health import router as health_router`
  - [ ] Call `app.include_router(health_router)` in create_app()
  - [ ] Verify router mounted at correct path (root level /health)
  - [ ] No authentication middleware for health endpoint
  - [ ] Write integration test verifying router registration

- [ ] Configure minimal logging for health checks (AC: logs as DEBUG level)
  - [ ] Use logger.debug() for health check requests
  - [ ] Log format: "health_check_requested"
  - [ ] Do NOT log at INFO level (avoid log noise)
  - [ ] Consider adding request_id to debug logs for tracing
  - [ ] Write test verifying DEBUG level logging

- [ ] Optimize for performance (AC: response time under 50ms p95)
  - [ ] No external API calls in health endpoint
  - [ ] No database queries (N/A for Epic 1)
  - [ ] Simple calculation: uptime from in-memory timestamp
  - [ ] No heavy processing or blocking operations
  - [ ] Use async def for FastAPI async optimizations
  - [ ] Write performance test: assert response time <50ms p95
  - [ ] Benchmark with pytest-benchmark or ab (Apache Bench)

- [ ] Handle edge cases and errors gracefully (AC: always accessible)
  - [ ] What if app_start_time is None? Return degraded status
  - [ ] What if version read fails? Use "unknown" fallback
  - [ ] Health endpoint should never return 500 (it's the canary)
  - [ ] Consider return 503 "Service Unavailable" if app is shutting down
  - [ ] Write test for error scenarios

- [ ] Add OpenAPI documentation for health endpoint (AC: auto-documented)
  - [ ] Add docstring to get_health() function
  - [ ] Describe endpoint purpose: "Check API health and uptime"
  - [ ] Document response schema with example
  - [ ] Specify response_model in @router.get decorator
  - [ ] FastAPI auto-generates OpenAPI spec from this
  - [ ] Verify /docs shows health endpoint with correct schema

- [ ] Testing and validation (AC: all acceptance criteria met)
  - [ ] Write unit test: HealthResponse model validation
  - [ ] Write unit test: Uptime calculation logic
  - [ ] Write integration test: GET /health returns 200 OK
  - [ ] Write integration test: Response matches expected schema
  - [ ] Write integration test: Health endpoint accessible after server start
  - [ ] Write integration test: Health logs at DEBUG level
  - [ ] Write performance test: Response time <50ms p95 (load test)
  - [ ] Write end-to-end test: Full server startup to health check
  - [ ] Manual test: `curl http://localhost:8000/health` after `mailreactor start`
  - [ ] Manual test: Verify response includes all required fields
  - [ ] Manual test: Check /docs includes health endpoint documentation
  - [ ] Verify test coverage meets target: 80%+ for health module

## Dev Notes

### Learnings from Previous Story

**From Story 1-4-cli-framework-with-start-command (Status: done)**

- **Server Startup Working**: `mailreactor start` command is functional
  - Server starts successfully and binds to localhost:8000
  - FastAPI app created via `create_app()` in main.py
  - Health endpoint can now be added to running server
- **FastAPI App Factory Pattern Established**: `main.py` has `create_app()` function
  - Import health router and register with `app.include_router(health_router)`
  - Router registration happens in create_app() before returning app
- **Structured Logging Configured**: Console/JSON logging working
  - Use `logger.debug("health_check_requested")` for health checks
  - DEBUG level prevents log noise from health check polling
- **Uvicorn Integration Working**: Server startup sequence validated
  - Health endpoint will be accessible immediately after server starts
  - Startup time <3 seconds validated (NFR-P1)
- **Module-Level App Removed**: No app instance at module level in main.py
  - Health module should use app.state for storing start time
  - Alternative: Use module-level variable in health.py itself
- **All Tests Passing**: 111 tests passing with 100% success rate
  - Follow same test patterns: unit + integration + e2e
  - Use TestClient from FastAPI for endpoint testing

[Source: stories/1-4-cli-framework-with-start-command.md#Dev-Agent-Record]

### Architecture Patterns and Constraints

**API Endpoint Pattern (from Architecture):**
```python
# src/mailreactor/api/health.py
from datetime import datetime, timedelta
from fastapi import APIRouter
from pydantic import BaseModel
import structlog

logger = structlog.get_logger(__name__)

# Module-level start time tracking
_app_start_time: datetime = datetime.utcnow()

class HealthResponse(BaseModel):
    status: str  # "healthy" | "degraded" | "unhealthy"
    version: str
    uptime_seconds: float
    timestamp: datetime

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def get_health():
    """
    Check API health and uptime.
    
    Returns system status, version, and uptime in seconds.
    This endpoint is always accessible without authentication.
    """
    logger.debug("health_check_requested")
    
    uptime = (datetime.utcnow() - _app_start_time).total_seconds()
    
    return HealthResponse(
        status="healthy",
        version="0.1.0",  # TODO: Read from package metadata
        uptime_seconds=uptime,
        timestamp=datetime.utcnow()
    )
```

**Router Registration Pattern:**
```python
# src/mailreactor/main.py
from .api.health import router as health_router

def create_app() -> FastAPI:
    app = FastAPI(...)
    
    # Register routers
    app.include_router(health_router)  # No prefix, mounts at /health
    
    return app
```

**NFR-P2: Health Check Performance (50ms p95)**
- Target: Health endpoint responds within 50ms at 95th percentile
- Measurement: HTTP request duration from client perspective
- Implementation:
  - In-memory uptime calculation (no I/O)
  - No external API calls
  - No database queries
  - Async FastAPI endpoint for concurrency
- Performance test: Load test with 100 requests, verify p95 <50ms

**Health Endpoint Design (from Architecture):**
- Always returns 200 OK when system is operational
- Returns 503 Service Unavailable only during shutdown
- Never returns 500 (health endpoint is the monitoring canary)
- No authentication required (monitoring needs unrestricted access)
- Logs at DEBUG level to avoid flooding logs with health check polls

**Version Management:**
```python
# Option 1: Read from package metadata (preferred)
from importlib.metadata import version
app_version = version("mailreactor")

# Option 2: Read from Settings (fallback)
from ..config import Settings
settings = Settings()
app_version = settings.version

# Option 3: Hardcode for MVP (simplest)
app_version = "0.1.0"
```

[Source: docs/architecture.md#API-Endpoint-Pattern]
[Source: docs/sprint-artifacts/tech-spec-epic-1.md#APIs-and-Interfaces]

### Project Structure Notes

**File Locations (per unified project structure):**
```
src/mailreactor/
├── api/
│   ├── __init__.py              # NEW: Empty init
│   └── health.py                # NEW: Health check router
├── main.py                      # MODIFIED: Register health router
├── config.py                    # USED: Settings.version (optional)
└── utils/
    └── logging.py               # USED: logger.debug() for health logs
```

**Testing Structure:**
```
tests/
├── unit/
│   └── test_health.py           # NEW: HealthResponse model, uptime logic
├── integration/
│   └── test_health_endpoint.py  # NEW: GET /health integration test
└── performance/
    └── test_health_latency.py   # NEW: Response time p95 validation
```

**Dependencies (none - FastAPI already present):**
- FastAPI (already installed)
- Pydantic (bundled with FastAPI)
- structlog (already configured)

[Source: docs/architecture.md#Project-Structure]

### Technical Notes

**Start Time Tracking Strategies:**

**Option 1: Module-level variable in health.py (simplest for MVP):**
```python
# src/mailreactor/api/health.py
from datetime import datetime

_app_start_time = datetime.utcnow()  # Set once at module import

async def get_health():
    uptime = (datetime.utcnow() - _app_start_time).total_seconds()
    ...
```
**Pros**: Simple, no state management needed
**Cons**: Resets on module reload (dev mode)

**Option 2: App state via FastAPI lifespan (more robust):**
```python
# src/mailreactor/main.py
from contextlib import asynccontextmanager
from datetime import datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.start_time = datetime.utcnow()
    yield

def create_app():
    app = FastAPI(lifespan=lifespan, ...)
    return app

# src/mailreactor/api/health.py
from fastapi import Request

async def get_health(request: Request):
    start_time = request.app.state.start_time
    uptime = (datetime.utcnow() - start_time).total_seconds()
    ...
```
**Pros**: Survives module reload, proper lifecycle management
**Cons**: More complex, requires FastAPI Request dependency

**Recommendation**: Use Option 1 (module-level) for MVP simplicity. Epic 1 doesn't have dev mode reload yet (Story 1.8), so module-level is sufficient.

**Response Time Optimization:**
- Health endpoint must be fast (NFR-P2: <50ms p95)
- Strategies:
  - No I/O operations (disk, network, database)
  - Minimal CPU work (simple subtraction for uptime)
  - Use async def for FastAPI concurrency
  - No logging at INFO level (reduces overhead)
- Performance testing: Use Apache Bench or pytest-benchmark

**OpenAPI Documentation Auto-Generation:**
- FastAPI automatically generates OpenAPI spec from:
  - Endpoint path and HTTP method
  - Response model (HealthResponse)
  - Docstring (endpoint description)
  - Status codes (default 200)
- Accessible at `/docs` (Swagger UI) and `/redoc`
- No manual OpenAPI configuration needed

**Logging Strategy for Health Checks:**
```python
# DEBUG level: Minimal overhead, useful for troubleshooting
logger.debug("health_check_requested", uptime_seconds=uptime)

# Do NOT use INFO level:
# logger.info("health_check_requested")  # ❌ Creates log noise
```

**Health Status Values:**
- "healthy": System operational, all good
- "degraded": System running but with warnings (future: IMAP connection slow)
- "unhealthy": System not operational (future: IMAP connection failed)
- MVP: Always return "healthy" (no subsystems to check yet)

[Source: docs/epics.md#Story-1.5-Health-Check-Endpoint]
[Source: docs/architecture.md#Logging-Pattern]

### Testing Best Practices

**Unit Tests for Health Module:**
- Test HealthResponse model validation (Pydantic)
- Test uptime calculation logic (mock datetime.utcnow)
- Test version reading (mock package metadata)
- No FastAPI app needed - just test functions
- **Target Coverage**: 80%+ for health.py module

**Integration Tests for Health Endpoint:**
- Use FastAPI TestClient (httpx under the hood)
- Test GET /health returns 200 OK
- Test response body matches HealthResponse schema
- Test response includes all required fields
- Test uptime value is reasonable (>0, <1000 for test)
- Test endpoint accessible without authentication
- **Example**:
```python
from fastapi.testclient import TestClient
from mailreactor.main import create_app

client = TestClient(create_app())

def test_health_endpoint_returns_200():
    response = client.get("/health")
    assert response.status_code == 200
    
def test_health_response_schema():
    response = client.get("/health")
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "version" in data
    assert "uptime_seconds" in data
    assert data["uptime_seconds"] >= 0
```

**Performance Tests:**
- Load test: Send 100 requests, measure response times
- Calculate p95 latency, assert <50ms
- Use pytest-benchmark for repeatable measurements
- Or use Apache Bench: `ab -n 100 -c 10 http://localhost:8000/health`
- Track baseline in CI for regression detection

**Manual Testing Checklist:**
- [ ] `mailreactor start` then `curl http://localhost:8000/health`
- [ ] Verify response has all fields: status, version, uptime_seconds, timestamp
- [ ] Verify uptime increases with subsequent requests
- [ ] Check /docs includes /health endpoint with correct schema
- [ ] Verify logs show DEBUG level (not INFO) for health checks
- [ ] Load test: Run ab or wrk, verify response time <50ms p95

[Source: docs/tdd-guide.md]

### References

- **PRD Requirements**: [Source: docs/prd.md - FR-027 (Health check endpoint), NFR-P2 (50ms p95 latency)]
- **Epic Breakdown**: [Source: docs/epics.md#Story-1.5-Health-Check-Endpoint]
- **Architecture Patterns**: [Source: docs/architecture.md#API-Endpoint-Pattern]
- **Tech Spec Epic 1**: [Source: docs/sprint-artifacts/tech-spec-epic-1.md#APIs-and-Interfaces]
- **NFR-P2**: [Source: docs/sprint-artifacts/tech-spec-epic-1.md#Performance]
- **Testing Standards**: [Source: docs/tdd-guide.md]
- **FastAPI Documentation**: https://fastapi.tiangolo.com/tutorial/bigger-applications/
- **Pydantic Models**: https://docs.pydantic.dev/latest/concepts/models/

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

Claude 3.5 Sonnet (via claude-code CLI)

### Debug Log References

N/A - Story drafted, implementation pending

### Completion Notes List

*This section will be populated by the Dev agent during implementation*

### File List

*This section will be populated by the Dev agent during implementation*

## Change Log

**2025-12-03:** Story 1.5 drafted by SM agent (Bob) via create-story workflow
- Extracted requirements from Epic 1 Story 1.5 (epics.md lines 372-407)
- Incorporated learnings from Story 1.4 (FastAPI app factory pattern, server startup working)
- Added NFR-P2 health check performance target (50ms p95) with load testing
- Detailed two start time tracking strategies: module-level (recommended for MVP) vs app.state
- Comprehensive task breakdown: 10 tasks with detailed subtasks
- Testing strategy: unit (model validation), integration (GET /health), performance (p95 latency)
- Manual testing checklist for developer validation
- Status: drafted, ready for story-context generation or direct implementation
