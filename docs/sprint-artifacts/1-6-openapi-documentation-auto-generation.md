# Story 1.6: OpenAPI Documentation Auto-Generation

Status: ready-for-dev

## Story

As a developer,
I want OpenAPI documentation auto-generated and accessible at `/docs` and `/redoc`,
so that I can explore the API interactively and understand request/response formats.

## Acceptance Criteria

**Given** the FastAPI application with health endpoint from Story 1.5  
**When** enhancing OpenAPI documentation metadata  
**Then** `src/mailreactor/main.py` FastAPI app configured with:
- `title`: "Mail Reactor API"
- `description`: Multi-line description with quick start, features, and usage examples
- `version`: Uses centralized `get_version()` utility (from Story 1.5)
- `contact`: Project name, GitHub URL, email
- `license_info`: MIT License with URL

**And** OpenAPI spec at `http://localhost:8000/openapi.json` includes:
- All configured metadata (title, description, version, contact, license)
- Health endpoint documentation with enhanced docstring

**And** Documentation endpoints work correctly:
- `/docs` - Swagger UI displays with "Mail Reactor API" title
- `/redoc` - ReDoc displays with configured metadata
- `/openapi.json` - Returns complete spec with our metadata

**Prerequisites:** Story 1.5 (health endpoint exists to document)

**Note:** FastAPI provides /docs, /redoc, /openapi.json automatically. This story only adds metadata configuration.

## Tasks / Subtasks

- [ ] Configure FastAPI app metadata in main.py (AC: app configured with metadata)
  - [ ] Set `title="Mail Reactor API"`
  - [ ] Set multi-line `description` with quick start, features, links
  - [ ] Set `version=get_version()` using centralized utility from Story 1.5
  - [ ] Set `contact={"name": "...", "url": "...", "email": "..."}`
  - [ ] Set `license_info={"name": "MIT License", "url": "..."}`

- [ ] Manual verification only (AC: documentation endpoints work)
  - [ ] Start server: `cd mailreactor && .venv/bin/python -m mailreactor start`
  - [ ] Check http://localhost:8000/docs displays "Mail Reactor API" title
  - [ ] Check http://localhost:8000/redoc displays configured metadata
  - [ ] Check http://localhost:8000/openapi.json includes our metadata (title, version, contact, license)
  - [ ] Optional: Test "Try it out" on /health endpoint in Swagger UI

**Note:** No automated tests needed - we're only configuring metadata that FastAPI uses. Testing that FastAPI generates docs is testing 3rd party code (violates team constraint).

## Dev Notes

### Learnings from Previous Story

**From Story 1-5-health-check-endpoint (Status: done)**

- **FastAPI App Factory in main.py**: `create_app()` function returns configured FastAPI app
  - Just add metadata parameters to `FastAPI()` constructor
  - App metadata: title, description, version, contact, license_info
- **Centralized Version Utility**: `utils/version.py` provides `get_version()`
  - Use this for FastAPI app version: `version=get_version()`
  - Keeps CLI --version and API /openapi.json version synchronized
- **OpenAPI Already Working**: /docs, /redoc, /openapi.json exist and work
  - Confirmed by manual test above - all three endpoints return 200 OK
  - FastAPI provides these automatically (no code needed)
  - This story only adds metadata to make docs more informative

[Source: stories/1-5-health-check-endpoint.md#Dev-Agent-Record]

### Architecture Patterns and Constraints

**OpenAPI Documentation Strategy (from Architecture):**

FastAPI auto-generates OpenAPI documentation from:
1. **FastAPI app initialization parameters**:
   ```python
   app = FastAPI(
       title="Mail Reactor API",
       description="Self-hosted headless email client with REST API",
       version=get_version(),
       contact={
           "name": "Mail Reactor",
           "url": "https://github.com/mailreactor/mailreactor",
           "email": "hello@mailreactor.com"
       },
       license_info={
           "name": "MIT",
           "url": "https://opensource.org/licenses/MIT"
       }
   )
   ```

2. **Route decorators with OpenAPI parameters**:
   ```python
   @router.get(
       "/health",
       response_model=HealthResponse,
       status_code=200,
       summary="Check API health and uptime",
       description="Returns system status, version, and uptime. No authentication required.",
       tags=["System"],
       responses={
           200: {
               "description": "System is healthy",
               "content": {
                   "application/json": {
                       "example": {
                           "status": "healthy",
                           "version": "0.1.0",
                           "uptime_seconds": 42.5,
                           "timestamp": "2025-12-03T10:30:45Z"
                       }
                   }
               }
           }
       }
   )
   async def get_health():
       """Detailed endpoint description goes here."""
       ...
   ```

3. **Pydantic models with examples**:
   ```python
   class HealthResponse(BaseModel):
       status: str = Field(description="System health status", example="healthy")
       version: str = Field(description="API version", example="0.1.0")
       uptime_seconds: float = Field(description="Uptime in seconds", example=42.5)
       timestamp: datetime = Field(description="Current server time (UTC)")
       
       model_config = ConfigDict(
           json_schema_extra={
               "example": {
                   "status": "healthy",
                   "version": "0.1.0",
                   "uptime_seconds": 42.5,
                   "timestamp": "2025-12-03T10:30:45Z"
               }
           }
       )
   ```

**Documentation URLs (FastAPI defaults):**
- `/docs` - Swagger UI (interactive testing)
- `/redoc` - ReDoc (clean, searchable documentation)
- `/openapi.json` - Raw OpenAPI 3.x specification

**FR-060, FR-061, FR-062 Requirements:**
- FR-060: Auto-generate OpenAPI spec ✓ (FastAPI built-in)
- FR-061: Swagger UI at /docs ✓ (FastAPI built-in)
- FR-062: ReDoc at /redoc ✓ (FastAPI built-in)

**Key Point**: FastAPI already provides these endpoints by default. This story focuses on:
1. Configuring app metadata (title, description, version, contact, license)
2. Enhancing endpoint documentation (docstrings, examples, tags)
3. Verifying documentation quality and functionality

[Source: docs/architecture.md#OpenAPI-Documentation]
[Source: docs/epics.md#Story-1.6-OpenAPI-Documentation-Auto-Generation]

### Project Structure Notes

**File Modifications:**
```
src/mailreactor/
└── main.py                      # MODIFIED: Add 5 lines of metadata to FastAPI() constructor
```

**No New Files:**
- FastAPI already provides /docs, /redoc, /openapi.json
- No tests needed (framework behavior, not our code)

**Dependencies:**
- None - FastAPI already includes OpenAPI/Swagger UI/ReDoc

[Source: docs/architecture.md#Project-Structure]

### Technical Notes

**FastAPI App Metadata Configuration:**

```python
# src/mailreactor/main.py
from fastapi import FastAPI
from .utils.version import get_version
from .api.health import router as health_router

def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Mail Reactor API",
        description="""
        ## Self-hosted headless email client with REST API
        
        Mail Reactor transforms email integration from weeks to minutes.
        Send and receive emails via simple HTTP requests.
        
        ### Quick Start
        
        ```bash
        # Install
        pipx install mailreactor
        
        # Start server
        mailreactor start --account you@gmail.com
        
        # Send email
        curl -X POST http://localhost:8000/accounts/{id}/send \\
          -H "Content-Type: application/json" \\
          -d '{"to": [{"email": "user@example.com"}], "subject": "Hello", "body_text": "Hi there!"}'
        ```
        
        ### Features
        - Zero-config startup (3-second cold start)
        - Auto-detect IMAP/SMTP settings for Gmail, Outlook, Yahoo, iCloud
        - Send emails with attachments, HTML, multiple recipients
        - Retrieve and search emails with IMAP syntax
        - No databases required (stateless by default)
        """,
        version=get_version(),
        contact={
            "name": "Mail Reactor Project",
            "url": "https://github.com/yourusername/mailreactor",
            "email": "hello@mailreactor.dev"
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT"
        },
        # docs_url="/docs",      # Default, can customize
        # redoc_url="/redoc",    # Default, can customize
        # openapi_url="/openapi.json"  # Default, can customize
    )
    
    # Register routers
    app.include_router(health_router)
    
    return app
```

**Endpoint Documentation Pattern:**

```python
# src/mailreactor/api/health.py
@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=200,
    summary="Check API health and uptime",
    description="""
    Returns the current health status of the Mail Reactor API.
    
    This endpoint is always accessible without authentication and is intended
    for monitoring and health check systems.
    
    **Response includes:**
    - System health status (healthy/degraded/unhealthy)
    - API version number
    - Server uptime in seconds
    - Current server timestamp (UTC)
    """,
    tags=["System"],
    responses={
        200: {
            "description": "System is healthy and operational",
            "model": HealthResponse
        }
    }
)
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
        version=get_version(),
        uptime_seconds=uptime,
        timestamp=datetime.utcnow()
    )
```

**Pydantic Model Examples:**

```python
# src/mailreactor/models/responses.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = Field(
        description="System health status: healthy, degraded, or unhealthy",
        example="healthy"
    )
    version: str = Field(
        description="API version number (semantic versioning)",
        example="0.1.0"
    )
    uptime_seconds: float = Field(
        description="Server uptime in seconds since startup",
        example=42.5,
        ge=0
    )
    timestamp: datetime = Field(
        description="Current server time in UTC (ISO 8601 format)",
        example="2025-12-03T10:30:45Z"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "0.1.0",
                "uptime_seconds": 42.5,
                "timestamp": "2025-12-03T10:30:45Z"
            }
        }
    )
```

**OpenAPI Tags for Organization:**

Future stories should use tags to organize endpoints:
- `System` - Health, version, monitoring endpoints
- `Accounts` - Account management (Epic 2)
- `Messages` - Email retrieval and search (Epic 4)
- `Send` - Email sending (Epic 3)
- `Authentication` - API key management (Epic 5)

**Code Changes Required:**

```python
# src/mailreactor/main.py
from fastapi import FastAPI
from .utils.version import get_version
from .api.health import router as health_router

def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Mail Reactor API",
        description="""
        Self-hosted headless email client with REST API.
        
        Transform email integration from weeks to minutes.
        
        ## Quick Start
        
        ```bash
        # Install
        pipx install mailreactor
        
        # Start server
        mailreactor start --account you@gmail.com
        
        # Send email
        curl -X POST http://localhost:8000/accounts/{id}/send \\
          -H "Content-Type: application/json" \\
          -d '{"to": [{"email": "user@example.com"}], "subject": "Hello", "body_text": "Hi!"}'
        ```
        
        ## Features
        - Zero-config startup (3-second cold start)
        - Auto-detect IMAP/SMTP for Gmail, Outlook, Yahoo, iCloud
        - Send emails with attachments, HTML, multiple recipients
        - Retrieve and search emails with IMAP syntax
        - No databases required (stateless by default)
        """,
        version=get_version(),
        contact={
            "name": "Mail Reactor Project",
            "url": "https://github.com/yourusername/mailreactor",
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        },
    )
    
    # Register routers
    app.include_router(health_router)
    
    return app
```

**Manual Testing Checklist:**

1. Start server: `cd mailreactor && .venv/bin/python -m mailreactor start`
2. Browser: http://localhost:8000/docs
   - ✓ Swagger UI loads
   - ✓ Title shows "Mail Reactor API"
   - ✓ Description includes Quick Start and Features sections
3. Browser: http://localhost:8000/redoc
   - ✓ ReDoc UI loads
   - ✓ Shows configured metadata
4. Browser: http://localhost:8000/openapi.json
   - ✓ JSON returned
   - ✓ Contains: title, version, description, contact, license
5. Optional: Test "Try it out" button for /health endpoint

[Source: docs/epics.md#Story-1.6]
[Source: FastAPI docs: https://fastapi.tiangolo.com/tutorial/metadata/]

### Testing Approach

**No Automated Tests Required:**

Per team constraint: "❌ DO NOT test 3rd party library functionality" and "❌ DO NOT test framework behavior"

- FastAPI generates /docs, /redoc, /openapi.json automatically (framework behavior)
- Swagger UI rendering is provided by FastAPI (3rd party)
- Testing that documentation endpoints work = testing FastAPI, not our code
- We're only configuring metadata (title, description, etc.) - no business logic to test

**Manual Verification Only:**
- Check http://localhost:8000/docs shows configured title
- Check http://localhost:8000/openapi.json includes our metadata
- Verify documentation is readable and professional

**What We're Testing in Other Stories:**
- Story 1.5 tests HealthResponse model and /health endpoint (OUR code)
- Future stories test OUR API endpoints, not FastAPI's doc generation

[Source: docs/hc-team-architecture.md - Testing Principle]

### References

- **PRD Requirements**: [Source: docs/prd.md - FR-060 (Auto-generate OpenAPI spec), FR-061 (Swagger UI at /docs), FR-062 (ReDoc at /redoc)]
- **Epic Breakdown**: [Source: docs/epics.md#Story-1.6-OpenAPI-Documentation-Auto-Generation]
- **Architecture Patterns**: [Source: docs/architecture.md#OpenAPI-Documentation]
- **Previous Story**: [Source: docs/sprint-artifacts/1-5-health-check-endpoint.md]
- **FastAPI OpenAPI Docs**: https://fastapi.tiangolo.com/tutorial/metadata/
- **OpenAPI 3.x Specification**: https://swagger.io/specification/
- **Pydantic Schema Examples**: https://docs.pydantic.dev/latest/concepts/json_schema/

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

Claude 3.5 Sonnet (via claude-code CLI)

### Debug Log References

### Completion Notes List

### File List

## Change Log

**2025-12-03:** Story 1.6 drafted by SM agent via create-story workflow
- Extracted requirements from Epic 1 Story 1.6 (epics.md lines 410-454)
- Incorporated learnings from Story 1.5 (centralized version utility exists)
- Key insight: FastAPI already provides /docs, /redoc, /openapi.json automatically
- Manual verification confirms all three endpoints working out of the box
- Story simplified: Only add metadata configuration (title, description, version, contact, license)
- Testing approach: Manual verification only (no automated tests per team constraint)
- Per hc-team-architecture.md: Don't test 3rd party/framework behavior
- Minimal work: ~5 lines of metadata in main.py FastAPI() constructor
- Status: drafted, ready for implementation
