# Mail Reactor - Epic Breakdown

**Author:** HC
**Date:** 2025-11-25
**Project Level:** MVP
**Target Scale:** Self-hosted, developer-first tool

---

## Overview

This document provides the complete epic and story breakdown for Mail Reactor, decomposing the requirements from the [PRD](./prd.md) into implementable stories.

**Living Document Notice:** This is the initial version created with PRD + Architecture context. Architecture details have been incorporated into technical notes.

### Epic Summary

Mail Reactor's MVP consists of 6 epics delivering 64 functional requirements:

1. **Epic 1: Foundation & Zero-Config Deployment** - Installable API service (24 FRs)
2. **Epic 2: Email Account Connection** - Connect and manage accounts (10 FRs)
3. **Epic 3: Email Sending Capability** - Send emails via API (8 FRs)
4. **Epic 4: Email Retrieval & Search** - Retrieve and search emails (8 FRs)
5. **Epic 5: Production-Ready Security** - API key authentication (5 FRs)
6. **Epic 6: Experimental IMAP-as-Database** - Optional state persistence (9 FRs)

---

## Functional Requirements Inventory

### Account Management (10 FRs)
- FR-001: Auto-detect IMAP/SMTP settings for common providers
- FR-002: Add account via CLI with interactive prompt
- FR-003: Add account via REST API
- FR-004: Secure credential storage in memory
- FR-005: Connect to IMAP server
- FR-006: Connect to SMTP server
- FR-007: Manual override of auto-detected settings
- FR-008: Validate credentials with clear error messages
- FR-009: Retrieve list of accounts via API
- FR-010: Retrieve specific account details via API

### Email Sending (8 FRs)
- FR-011: Send email with to/subject/plain text
- FR-012: Send email with HTML body
- FR-013: Send to multiple recipients (to, cc, bcc)
- FR-014: Send with file attachments (base64)
- FR-015: Send via SMTP with credentials
- FR-016: Return message ID and status
- FR-017: Handle SMTP errors gracefully
- FR-018: Support common headers (Reply-To, custom)

### Email Retrieval & Search (8 FRs)
- FR-019: Query emails with IMAP search syntax
- FR-020: Support standard IMAP criteria
- FR-021: Return structured JSON
- FR-022: Retrieve full email details
- FR-023: Cursor-based pagination
- FR-024: Server-side filtering
- FR-025: In-memory caching
- FR-026: Configure time window for ingestion

### System Health & Monitoring (5 FRs)
- FR-027: Health check endpoint
- FR-028: Log startup sequence
- FR-029: Log connection status
- FR-030: Log API requests/responses
- FR-031: Clear error messages

### Installation & Deployment (7 FRs)
- FR-032: Install via PyPI/pipx
- FR-033: Zero external dependencies
- FR-034: Single command startup
- FR-035: Start within 3 seconds
- FR-036: Bind to localhost by default
- FR-037: Configure host/port via CLI
- FR-038: Display startup message

### Authentication & Security - Core (7 FRs)
- FR-039: No auth in MVP (localhost)
- FR-040: Warn when auth disabled
- FR-041: Enable API key via CLI
- FR-042: Auto-generate API key
- FR-043: Require bearer token when enabled
- FR-044: Return 401 for invalid auth
- FR-045: Store API keys securely (hashed)

### State Management - Experimental (9 FRs)
- FR-046: Stateless by default
- FR-047: Rebuild from IMAP in 5 seconds
- FR-048: Optional IMAP-as-database mode
- FR-049: Write state to IMAP folder
- FR-050: State includes markers, webhooks, config
- FR-051: Periodic flush to IMAP
- FR-052: Reconstruct from IMAP on restart
- FR-053: Detect corrupted state, fallback
- FR-054: Alert on critical state deletion

### API Design & Standards (8 FRs)
- FR-055: JSON content type
- FR-056: Consistent envelope format
- FR-057: Standard HTTP codes
- FR-058: Error responses with details
- FR-059: ISO 8601 timestamps (UTC)
- FR-060: Auto-generate OpenAPI spec
- FR-061: Swagger UI at /docs
- FR-062: ReDoc at /redoc

### Future Phase 2+ (36 FRs)
- FR-063 to FR-068: Plugin Architecture
- FR-069 to FR-076: Webhook Support
- FR-077 to FR-081: Multi-Account Support
- FR-082 to FR-085: OAuth2 Authentication
- FR-086 to FR-098: Advanced Features

**Total:** 98 Functional Requirements  
**MVP Scope:** 64 FRs (65%)

---

## FR Coverage Map

| Epic | FRs Covered | Count | User Value Delivered |
|------|-------------|-------|---------------------|
| **Epic 1: Foundation** | FR-027 to FR-038, FR-039 to FR-040, FR-055 to FR-062 | 24 | Installable, running API service with health checks and docs |
| **Epic 2: Account Connection** | FR-001 to FR-010 | 10 | Connect and manage email accounts with auto-detection |
| **Epic 3: Email Sending** | FR-011 to FR-018 | 8 | Send emails (plain, HTML, attachments) via REST API |
| **Epic 4: Email Retrieval** | FR-019 to FR-026 | 8 | Retrieve and search emails via REST API with IMAP syntax |
| **Epic 5: Security** | FR-041 to FR-045 | 5 | Production-ready API key authentication |
| **Epic 6: IMAP State** | FR-046 to FR-054 | 9 | Optional state persistence using IMAP (experimental) |
| **Future (Phase 2+)** | FR-063 to FR-098 | 36 | Webhooks, Multi-account, OAuth2, Plugins, Advanced |

---

## Epic 1: Foundation & Zero-Config Deployment

**Goal:** Developers can install Mail Reactor and have it running in under 5 minutes with zero configuration, including health checks, API documentation, and structured logging.

**User Value:** Foundation that enables all subsequent features. Developers can verify installation success immediately through health endpoint and interactive API docs.

**FRs Covered:** FR-027 to FR-038 (Health, Installation), FR-039 to FR-040 (Auth basics), FR-055 to FR-062 (API Standards)

---

### Story 1.1: Project Structure and Build Configuration

As a developer,  
I want the Mail Reactor project initialized with proper Python package structure,  
So that I can install, develop, and distribute the package reliably.

**Acceptance Criteria:**

**Given** a new Mail Reactor codebase  
**When** the project structure is initialized  
**Then** the following structure exists:
- `src/mailreactor/` with proper `__init__.py` and package modules
- `tests/` directory with pytest configuration
- `pyproject.toml` with project metadata and dependencies
- `README.md` with quick start instructions
- `LICENSE` file (MIT license)
- `.gitignore` configured for Python projects

**And** `pyproject.toml` includes:
- Project name: `mailreactor`
- Python version requirement: `>=3.10`
- Core dependencies: FastAPI 0.122.0, Uvicorn, IMAPClient 3.0.1, aiosmtplib 5.0.0, Typer 0.20.0, Pydantic v2, structlog
- Dev dependencies: pytest, pytest-asyncio, ruff, mypy, pytest-cov
- Entry point: `mailreactor` CLI command
- Package installable via: `pipx install mailreactor`

**And** running `pip install -e ".[dev]"` installs package in development mode successfully

**Prerequisites:** None (first story)

**Technical Notes:**
- Follow Architecture doc project structure (ADR-001, ADR-005)
- Use modern pyproject.toml (PEP 621)
- Ensure all dependencies are MIT-compatible
- Set up proper Python package namespace under `src/`
- Architecture reference: `/docs/architecture.md` sections "Project Structure" and "Technology Stack Details"

---

### Story 1.2: FastAPI Application Initialization

As a developer,  
I want the FastAPI application properly initialized with core middleware,  
So that the API server can start and handle requests with proper error handling and logging.

**Acceptance Criteria:**

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

**Prerequisites:** Story 1.1 (project structure exists)

**Technical Notes:**
- Follow Architecture pattern section "API Endpoint Pattern"
- Use FastAPI exception handlers for consistent error responses (FR-058)
- Configure Pydantic Settings for environment variable support (ADR Architecture)
- Error response format: `{"detail": "message", "error_code": "CODE", "request_id": "id"}`
- Architecture reference: sections "Error Handling Pattern", "Configuration Pattern"

---

### Story 1.3: Structured Logging with Console and JSON Renderers

As a developer,  
I want clean console logs by default with optional JSON output,  
So that the quick start experience is clear while still supporting production log aggregation.

**Acceptance Criteria:**

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

**Technical Notes:**
- **Single pipeline:** structlog processors → renderer (Console or JSON)
- Use `rich.console.Console` for colored output (default renderer)
- Use `structlog.processors.JSONRenderer` for JSON output (--json-logs flag)
- Shared processors: `add_log_level`, `TimeStamper`, `StackInfoRenderer`, `format_exc_info`
- Console renderer shows: `[LEVEL] timestamp message key=value key=value`
- JSON renderer outputs: `{"timestamp": "...", "level": "...", "event": "...", "key": "value"}`
- Color only (minimal emoji): ✓ for account connected, ✗ for startup failure, ⚠ for auth disabled
- Auto-detect TTY: If stdout is not a terminal (piped/redirected), consider auto-enabling JSON
- Follow Architecture "Logging Pattern" section
- NFR-O1: Structured logging with configurable levels
- DX Priority: Clean console logs for humans, JSON for machines

---

### Story 1.4: CLI Framework with Start Command

As a developer,  
I want a CLI command `mailreactor start` to launch the API server,  
So that I can start Mail Reactor with a single command in under 5 seconds.

**Acceptance Criteria:**

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

**Technical Notes:**
- Use Typer for CLI (ADR-005)
- Uvicorn with FastAPI in production mode (reload=False)
- Pass Settings to Uvicorn configuration
- Handle signals for graceful shutdown
- Keep CLI minimal: only `start` and `dev` commands (no account subcommands)
- Account management happens via REST API or `--account` flag on start
- FR-034: Single command startup
- FR-035: Start within 3 seconds
- FR-036: Bind to localhost by default
- FR-037: Configure via CLI flags
- FR-038: Display startup message
- Architecture reference: sections "CLI Framework: Typer", "Development Workflow"

---

### Story 1.5: Health Check Endpoint

As a developer,  
I want a `/health` endpoint to verify Mail Reactor is operational,  
So that I can monitor system status and validate successful deployment.

**Acceptance Criteria:**

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

**Technical Notes:**
- Simple, fast endpoint - no heavy operations
- Track app start time in `main.py` for uptime calculation
- Return Pydantic model: `HealthResponse(status, version, uptime_seconds)`
- FR-027: Health check endpoint with status, uptime
- NFR-P2: Health check responds within 50ms p95
- Architecture reference: section "API Endpoint Pattern"

---

### Story 1.6: OpenAPI Documentation Auto-Generation

As a developer,  
I want OpenAPI documentation auto-generated and accessible at `/docs` and `/redoc`,  
So that I can explore the API interactively and understand request/response formats.

**Acceptance Criteria:**

**Given** the FastAPI application with health endpoint from Story 1.5  
**When** accessing API documentation endpoints  
**Then** navigating to `http://localhost:8000/docs`:
- Displays Swagger UI interface
- Lists all available endpoints (starting with `/health`)
- Shows request/response schemas with examples
- Provides "Try it out" functionality for testing endpoints
- Auto-generated from FastAPI route definitions and Pydantic models

**And** navigating to `http://localhost:8000/redoc`:
- Displays ReDoc interface (alternative documentation view)
- Same content as Swagger UI, different presentation
- Mobile-friendly, searchable documentation

**And** navigating to `http://localhost:8000/openapi.json`:
- Returns complete OpenAPI 3.0+ specification in JSON
- Includes all endpoint definitions, schemas, parameters

**And** Documentation includes:
- Endpoint descriptions from docstrings
- Request parameter descriptions
- Response model schemas
- HTTP status codes
- Example requests and responses

**Prerequisites:** Story 1.5 (health endpoint exists to document)

**Technical Notes:**
- FastAPI auto-generates OpenAPI spec (ADR-001)
- Add docstrings to all route functions
- Use Pydantic models for request/response validation and doc generation
- Configure FastAPI app with title, version, description
- FR-060: Auto-generate OpenAPI spec
- FR-061: Swagger UI at /docs
- FR-062: ReDoc at /redoc
- Architecture reference: sections "API Documentation Strategy", "OpenAPI Documentation"

---

### Story 1.7: Response Envelope and Error Handling Standards

As a developer,  
I want consistent API response formats and error handling,  
So that client applications can reliably parse responses and handle errors gracefully.

**Acceptance Criteria:**

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

**Prerequisites:** Story 1.2 (exception hierarchy), Story 1.5 (health endpoint to test)

**Technical Notes:**
- Use FastAPI dependency for request ID generation
- Middleware to inject request_id into structlog context
- Generic error handler catches all unhandled exceptions
- FR-055: JSON content type
- FR-056: Consistent envelope format
- FR-057: Standard HTTP codes
- FR-058: Error responses with details
- FR-059: ISO 8601 timestamps (UTC)
- Architecture reference: sections "Error Handling Pattern", "API Contracts"

---

### Story 1.8: Development Mode with Hot Reload

As a developer,  
I want a `mailreactor dev` command that enables auto-reload during development,  
So that I can iterate quickly without manually restarting the server.

**Acceptance Criteria:**

**Given** the CLI from Story 1.4  
**When** adding development mode  
**Then** `src/mailreactor/cli/server.py` provides:
- `dev()` command using Typer
- Same options as `start` command (--host, --port, --log-level)
- Starts Uvicorn with `reload=True` (watches for file changes)
- Watches `src/mailreactor/` directory for changes
- Log level defaults to DEBUG in dev mode

**And** Running `mailreactor dev`:
- Displays "Development mode: auto-reload enabled"
- Reloads application automatically when Python files change
- Logs each reload event
- Uses colored console logging instead of JSON for better DX

**And** Development mode warning displayed: "Do not use in production - dev mode only"

**Prerequisites:** Story 1.4 (CLI with start command)

**Technical Notes:**
- Uvicorn reload mode watches file changes
- Only for development - never in production
- Override log format for dev mode (console vs JSON)
- Typer makes it easy to add command with same options
- Architecture reference: section "Development Workflow"

---

## Epic 1 Summary

**Stories Completed:** 8  
**FRs Delivered:** 24 (FR-027 to FR-040, FR-055 to FR-062)  
**User Value:** Developers can now install Mail Reactor via pip, start it with a single command, verify it's running via `/health`, explore the API via `/docs`, and iterate quickly in dev mode.

**What Developers Can Do:**
✅ Install: `pipx install mailreactor`  
✅ Start: `mailreactor start` (production) or `mailreactor dev` (development)  
✅ Verify: `curl http://localhost:8000/health`  
✅ Explore: Open `http://localhost:8000/docs` in browser  
✅ Develop: Code changes auto-reload in dev mode

**Next:** Epic 2 will enable developers to connect their email accounts with auto-detected IMAP/SMTP settings.

---

## Epic 2: Email Account Connection

**Goal:** Developers can connect their email accounts (Gmail, Outlook, Yahoo, custom servers) with intelligent auto-detection of IMAP/SMTP settings, falling back to Mozilla Autoconfig for broader provider coverage.

**User Value:** Developers can authenticate and connect to their email accounts - the essential first step for any email operation. Auto-detection eliminates the need to look up server settings manually.

**FRs Covered:** FR-001 to FR-010 (Account Management)

---

### Story 2.1: Provider Configuration and Basic Auto-Detection

As a developer,  
I want Mail Reactor to auto-detect IMAP/SMTP settings for major email providers,  
So that I don't have to manually look up server configurations.

**Acceptance Criteria:**

**Given** a new provider detection module  
**When** implementing basic auto-detection  
**Then** `src/mailreactor/utils/providers.yaml` contains:
- Gmail configuration (imap.gmail.com:993, smtp.gmail.com:587)
- Outlook/Office365 configuration (outlook.office365.com:993, smtp.office365.com:587)
- Yahoo Mail configuration (imap.mail.yahoo.com:993, smtp.mail.yahoo.com:587)
- iCloud configuration (imap.mail.me.com:993, smtp.mail.me.com:587)
- Each entry includes: imap_host, imap_port, imap_ssl, smtp_host, smtp_port, smtp_starttls

**And** `src/mailreactor/core/provider_detector.py` provides:
- `detect_provider(email: str) -> Optional[ProviderConfig]` function
- Extracts domain from email address
- Matches domain against known providers (exact match and common variations)
- Returns `ProviderConfig` Pydantic model with IMAP/SMTP settings
- Returns `None` if provider not found in local configuration

**And** `src/mailreactor/models/account.py` defines:
- `ProviderConfig` model with imap/smtp connection details
- `AccountCredentials` model with email, password, optional provider override
- `AccountConfig` model for account-specific settings

**And** Domain extraction handles common patterns:
- `user@gmail.com` → gmail provider
- `user@mycompany.com` → None (unknown, will trigger Mozilla fallback)
- `user@outlook.com` or `user@hotmail.com` → outlook provider

**Prerequisites:** Story 1.2 (Pydantic models), Story 1.3 (logging)

**Technical Notes:**
- Use YAML for provider configs (human-readable, easy to extend)
- PyYAML dependency (already common in Python ecosystem)
- Domain extraction: `email.split('@')[1].lower()`
- Provider matching: dictionary lookup with domain as key
- FR-001: Auto-detect IMAP/SMTP for common providers
- Architecture reference: section "Provider Auto-Detection"

---

### Story 2.1.2: CLI Account Management with Encrypted Storage

As a developer or system administrator,  
I want to manage email accounts via CLI commands with encrypted password storage,  
So that I can securely configure multiple accounts without restarting the service.

**Acceptance Criteria:**

**Given** a need for persistent account management  
**When** implementing CLI-based account management  
**Then** Mail Reactor provides:
- CLI commands: `mailreactor accounts add|list|edit|remove`
- Encrypted TOML config file: `~/.config/mailreactor/config.toml`
- Hot reload via 5-second polling (config changes detected automatically)
- API endpoints: `POST/GET/PUT/DELETE /accounts`
- HTTPS enforcement middleware for production API usage

**And** Account encryption security:
- Fernet symmetric encryption with PBKDF2 key derivation
- Master password from `MAILREACTOR_PASSWORD` env var or runtime prompt
- Passwords encrypted before storage in config file
- 100,000+ PBKDF2 iterations (OWASP standard)

**And** Config file structure:
- Single `~/.config/mailreactor/config.toml` file
- Multiple accounts supported (email is account ID)
- Atomic file writes prevent corruption
- Hot reload detects changes within 5 seconds

**And** CLI autodiscovery integration:
- `mailreactor accounts add` uses provider detection (Story 2.1)
- Falls back to Mozilla autoconfig (Story 2.2) if provider not found
- Interactive password prompt (no echo)
- Writes complete encrypted config to TOML

**Prerequisites:** Story 2.1 (provider detection), SPIKE-003 (architecture decisions)

**Technical Notes:**
- Source: SPIKE-003-cli-account-management.md
- Supersedes Story 2.7 (startup via CLI flag with `--account`)
- Implements encrypted config file vs ephemeral `--account` flag
- Can run in parallel with Story 2.2 (Mozilla autoconfig)
- FR-002: Add account via CLI
- FR-003: Add account via REST API
- FR-006: Remove account
- Architecture reference: sections "Security Architecture", "Configuration Management"

---

### Story 2.2: Mozilla Thunderbird Autoconfig Fallback

As a developer,  
I want Mail Reactor to use Mozilla's Thunderbird Autoconfig database for unknown providers,  
So that I can connect to a wider range of email providers without manual configuration.

**Acceptance Criteria:**

**Given** an email domain not in local providers.yaml  
**When** auto-detection attempts Mozilla Autoconfig fallback  
**Then** `src/mailreactor/core/provider_detector.py` is enhanced with:
- `detect_via_mozilla_autoconfig(domain: str) -> Optional[ProviderConfig]` async function
- Queries Mozilla Autoconfig database via HTTP: `https://autoconfig.thunderbird.net/v1.1/{domain}`
- Parses XML response to extract IMAP/SMTP server settings
- Falls back to trying `autoconfig.{domain}/mail/config-v1.1.xml` (ISP-hosted config)
- Returns `ProviderConfig` if successful, `None` if not found

**And** Detection strategy follows this cascade:
1. Check local providers.yaml (fast, offline)
2. If not found, try Mozilla Autoconfig (network call)
3. If not found, try ISP-hosted autoconfig (network call)
4. If all fail, return None (requires manual configuration)

**And** Mozilla Autoconfig responses are cached in-memory:
- Cache successful lookups for 24 hours (TTL)
- Cache failures for 1 hour (avoid repeated failed lookups)
- Configurable cache TTL via settings

**And** Network calls include:
- 5-second timeout (don't block startup)
- Proper error handling (network failures, invalid XML, missing fields)
- User-Agent header: `MailReactor/{version}`

**And** Logging captures:
- INFO: "Mozilla Autoconfig lookup for domain: {domain}"
- INFO: "Mozilla Autoconfig success for {domain}" or "Mozilla Autoconfig failed for {domain}"
- DEBUG: Full XML response for troubleshooting

**And** XML parsing handles:
- `<incomingServer type="imap">` sections for IMAP config
- `<outgoingServer type="smtp">` sections for SMTP config
- `<hostname>`, `<port>`, `<socketType>` (SSL/STARTTLS) fields
- Invalid/incomplete configurations gracefully (skip and try next source)

**Prerequisites:** Story 2.1 (basic provider detection exists)

**Technical Notes:**
- Use `httpx` async HTTP client (already in FastAPI ecosystem)
- XML parsing: `xml.etree.ElementTree` (Python stdlib)
- Mozilla Autoconfig spec: https://wiki.mozilla.org/Thunderbird:Autoconfiguration
- Autoconfig URL format: `https://autoconfig.thunderbird.net/v1.1/{domain}`
- ISP fallback: `http://autoconfig.{domain}/mail/config-v1.1.xml`
- FR-001: Auto-detect IMAP/SMTP settings (broader coverage)
- This addresses the brainstorming session insight about using Mozilla's mechanism
- Cache implementation: simple dict with timestamp expiry (MVP), can upgrade to Redis in Production Pack

---

### Story 2.3: Manual IMAP/SMTP Configuration Override

As a developer,  
I want to manually specify IMAP/SMTP settings when auto-detection fails or is incorrect,  
So that I can connect to any email server regardless of auto-detection support.

**Acceptance Criteria:**

**Given** auto-detection has completed (success or failure)  
**When** implementing manual override capability  
**Then** `POST /accounts` API endpoint accepts:
- Required: `email`, `password`
- Optional: `imap_host`, `imap_port`, `imap_ssl`, `smtp_host`, `smtp_port`, `smtp_starttls`
- If optional fields provided, use them instead of auto-detection
- If optional fields omitted, use auto-detected settings

**And** `src/mailreactor/api/accounts.py` provides:
- `POST /accounts` endpoint
- Request model: `AddAccountRequest` with email, password, optional overrides
- Response model: `AccountResponse` with account_id, email, connection status

**And** Account addition logic:
1. Attempt auto-detection (local providers.yaml → Mozilla Autoconfig → ISP autoconfig)
2. If manual overrides provided, use them instead of auto-detected values
3. If no auto-detection and no manual overrides, return 400 with helpful error message
4. Store account credentials in StateManager (in-memory)
5. Return account_id for future API calls

**And** Error messages guide users:
- "Unable to auto-detect settings for {domain}. Please provide imap_host, smtp_host manually."
- Include example of manual configuration in error response
- Link to documentation for finding IMAP/SMTP settings

**And** `mailreactor start` command supports manual IMAP/SMTP overrides:
- `mailreactor start --account user@custom.com --imap-host imap.custom.com --smtp-host smtp.custom.com`
- Also supports: `--imap-port`, `--imap-ssl`, `--smtp-host`, `--smtp-port`, `--smtp-starttls`
- Interactive password prompt (not echoed to terminal) after server starts
- All flags optional - auto-detection used if not provided

**Prerequisites:** Stories 2.1, 2.2 (auto-detection cascade), Story 1.4 (CLI start command)

**Technical Notes:**
- Use `getpass` module for password input (no echo)
- Validate port ranges (1-65535)
- Validate hostnames (basic format check)
- FR-007: Manual override of auto-detected settings
- FR-002: Add account via CLI with interactive prompt
- FR-003: Add account via REST API
- Architecture reference: section "API Endpoint Pattern"

---

### Story 2.4: Account Connection Validation and Error Handling

As a developer,  
I want immediate feedback when account credentials are invalid or connection fails,  
So that I can quickly fix configuration issues without waiting for first email operation.

**Acceptance Criteria:**

**Given** account credentials (auto-detected or manual)  
**When** adding an account via API or CLI  
**Then** Mail Reactor validates the connection before storing:
- Attempts IMAP connection with provided credentials
- Attempts IMAP login (authenticate)
- Attempts SMTP connection with provided credentials
- All operations have 10-second timeout

**And** Connection validation succeeds:
- Account stored in StateManager with status: "connected"
- Returns HTTP 201 Created with account details
- Logs: INFO "Account {account_id} connected successfully"

**And** Connection validation fails with clear error messages:
- **IMAP connection failed:** "Unable to connect to IMAP server {host}:{port}. Check hostname and port."
- **IMAP authentication failed:** "IMAP authentication failed. Check email and password. For Gmail, use App Password."
- **SMTP connection failed:** "Unable to connect to SMTP server {host}:{port}. Check hostname and port."
- Returns HTTP 503 Service Unavailable with error details
- Logs: ERROR "Account connection failed" with full error context

**And** Special handling for common issues:
- Gmail without App Password: Error message includes link to Google App Passwords setup
- Outlook 2FA: Error message mentions App Passwords or OAuth requirement
- Certificate errors: Error message suggests checking SSL/TLS settings

**And** `mailreactor start` provides real-time feedback during account setup:
- Displays: "Connecting to IMAP server..." (with spinner)
- Displays: "Authenticating..." (with spinner)
- Displays: "Testing SMTP connection..." (with spinner)
- Success: "✓ Account connected successfully" → proceeds to start server
- Failure: Display error message with remediation steps → exits with error code

**Prerequisites:** Story 2.3 (account addition endpoints), Stories 1.1-1.3 (logging, exceptions), Story 1.4 (start command)

**Technical Notes:**
- Use IMAPClient for IMAP connection test (sync, wrap with executor)
- Use aiosmtplib for SMTP connection test (async)
- Implement custom exception: `IMAPConnectionError`, `IMAPAuthenticationError`, `SMTPConnectionError`
- Include provider-specific hints in error messages
- FR-005: Connect to IMAP server
- FR-006: Connect to SMTP server
- FR-008: Validate credentials with clear error messages
- Architecture reference: sections "IMAP Integration", "SMTP Integration", "Error Handling Pattern"
- NFR-R1: Connection resilience with clear error messages

---

### Story 2.5: Account Listing and Retrieval API

As a developer,  
I want to list all configured accounts and retrieve specific account details via API,  
So that I can manage multiple accounts and verify configuration.

**Acceptance Criteria:**

**Given** one or more accounts stored in StateManager  
**When** implementing account retrieval endpoints  
**Then** `src/mailreactor/api/accounts.py` provides:
- `GET /accounts` - List all accounts
- `GET /accounts/{account_id}` - Get specific account details

**And** `GET /accounts` returns:
- Array of account summaries
- Each summary includes: account_id, email, status, created_at
- Passwords and sensitive credentials excluded from response
- HTTP 200 OK

**And** `GET /accounts/{account_id}` returns:
- Full account details: account_id, email, status, imap_host, smtp_host (no password)
- Connection status: "connected", "disconnected", "error"
- Last connection test timestamp (if applicable)
- HTTP 200 OK if found, HTTP 404 if account_id not found

**And** Response models defined:
- `AccountSummary`: account_id, email, status, created_at
- `AccountDetail`: extends AccountSummary with imap_host, smtp_host, imap_port, smtp_port
- `AccountListResponse`: list of AccountSummary
- Passwords never included in any response (security)

**And** StateManager provides:
- `async def get_all_accounts() -> List[AccountCredentials]`
- `async def get_account(account_id: str) -> Optional[AccountCredentials]`
- Thread-safe operations with asyncio locks

**Prerequisites:** Story 2.4 (accounts can be added), Story 1.7 (response standards)

**Technical Notes:**
- Use Pydantic `exclude` to prevent password serialization
- FR-009: Retrieve list of accounts via API
- FR-010: Retrieve specific account details via API
- FR-004: Credentials stored in memory (passwords never exposed in API)
- Architecture reference: section "State Management (MVP - In-Memory)"

---

### Story 2.6: In-Memory State Management for Accounts

As a developer,  
I want accounts stored securely in memory during runtime,  
So that Mail Reactor operates statelessly without external dependencies while maintaining active connections.

**Acceptance Criteria:**

**Given** the StateManager from Epic 1  
**When** enhancing for account management  
**Then** `src/mailreactor/core/state_manager.py` provides:
- Dictionary of accounts: `Dict[str, AccountCredentials]`
- Asyncio lock for thread-safe access
- Methods: `add_account()`, `get_account()`, `get_all_accounts()`, `remove_account()`
- Account ID generation: `acc_{uuid4().hex[:8]}` (short, unique)

**And** Account credentials include:
- account_id (generated)
- email (user-provided)
- password (stored in memory only, never logged or persisted)
- imap_host, imap_port, imap_ssl (auto-detected or manual)
- smtp_host, smtp_port, smtp_starttls (auto-detected or manual)
- created_at (timestamp)

**And** State lifecycle:
- Application starts: Empty state
- Accounts added via API/CLI: Stored in memory
- Application stops: All state lost (by design for MVP)
- State never written to disk (security)

**And** Security measures:
- Passwords stored in memory only
- No logging of passwords or credentials
- No serialization to disk
- Credentials cleared from memory on account removal

**And** Future enhancement hooks:
- Abstract interface allows swapping to persistent storage (Production Pack)
- Comments indicate where IMAP-as-database persistence would integrate (Epic 6)

**Prerequisites:** Story 1.2 (initial StateManager exists)

**Technical Notes:**
- FR-004: Secure credential storage in memory
- FR-046: Stateless by default
- NFR-S1: Credentials in memory only, never persisted to disk in MVP
- NFR-P4: Memory footprint - efficient credential storage
- Architecture reference: section "State Management (MVP - In-Memory)"

---

### Story 2.7: ~~Startup Account Configuration via CLI Flag~~ [CANCELLED]

**Status:** CANCELLED - Superseded by Story 2.1.2 (CLI Account Management with Encrypted Storage)

**Original Goal:** Enable `--account` flag for single-account startup configuration.

**Why Cancelled:** SPIKE-003 established a more comprehensive account management approach:
- Story 2.1.2 implements persistent encrypted config file (vs ephemeral `--account` flag)
- Multi-account support from day one (vs single account limitation)
- Hot reload mechanism enables account changes without restart
- CLI commands provide full CRUD operations (add/edit/remove/list)

**Functionality Moved To:**
- Account addition: `mailreactor accounts add` (Story 2.1.2)
- Account configuration: `~/.config/mailreactor/config.toml` (Story 2.1.2)
- Password management: Master password encryption (Story 2.1.2)

**Reference:** SPIKE-003-cli-account-management.md

---

### Story 2.8: Account Removal API

As a developer,  
I want to remove email accounts via API,  
So that I can clean up accounts I no longer need or reconfigure from scratch.

**Acceptance Criteria:**

**Given** an existing account in StateManager  
**When** implementing account removal  
**Then** `src/mailreactor/api/accounts.py` provides:
- `DELETE /accounts/{account_id}` endpoint
- Returns HTTP 204 No Content on success
- Returns HTTP 404 Not Found if account_id doesn't exist

**And** Account removal process:
1. Verify account exists
2. Close any active IMAP/SMTP connections (if applicable)
3. Remove from StateManager
4. Clear credentials from memory
5. Log: INFO "Account {account_id} removed"

**And** Error handling:
- Attempting to remove non-existent account returns clear error
- Ongoing operations with removed account fail gracefully

**Prerequisites:** Stories 2.4-2.6 (accounts can be added and listed)

**Technical Notes:**
- Phase 2: Multi-account support will make this more critical
- MVP: Single account typically, but API supports multiple
- Ensure cleanup of any cached data associated with account
- FR-081: Remove accounts via API (listed as Phase 2, but implementing in MVP)
- Architecture reference: section "State Management"

---

## Epic 2 Summary

**Stories Completed:** 8  
**FRs Delivered:** 10 (FR-001 to FR-010)  
**User Value:** Developers can now connect email accounts during startup or via API with intelligent auto-detection (local config → Mozilla Autoconfig → ISP fallback → manual), validate connections immediately, and manage accounts via REST API.

**What Developers Can Do:**
✅ Start with account: `mailreactor start --account you@gmail.com` (zero config, interactive password)  
✅ Connect Gmail, Outlook, Yahoo, iCloud automatically  
✅ Connect custom providers via Mozilla Autoconfig (1000s of providers)  
✅ Manually configure any IMAP/SMTP server via CLI flags or API  
✅ Validate connections immediately with clear error messages  
✅ List and retrieve account details via REST API  
✅ Remove accounts when no longer needed via REST API

**Auto-Detection Coverage:**
- **Tier 1:** Hardcoded providers (Gmail, Outlook, Yahoo, iCloud) - instant, offline
- **Tier 2:** Mozilla Autoconfig - 1000s of providers, requires network
- **Tier 3:** ISP-hosted autoconfig - provider-specific configs
- **Tier 4:** Manual configuration - universal fallback

**Next:** Epic 3 will enable developers to send emails (plain text, HTML, attachments) via REST API.

---

## Epic 3: Email Sending Capability

**Goal:** Developers can send emails (plain text, HTML, attachments) via REST API using connected email accounts.

**User Value:** Core capability #1 - send transactional emails, password resets, notifications, marketing emails. Immediate practical value.

**FRs Covered:** FR-011 to FR-018 (Email Sending)

---

### Story 3.1: SMTP Client Wrapper with Async Support

As a developer,  
I want an async SMTP client abstraction,  
So that email sending doesn't block the API server and integrates cleanly with FastAPI.

**Acceptance Criteria:**

**Given** the account management from Epic 2  
**When** implementing SMTP client wrapper  
**Then** `src/mailreactor/core/smtp_client.py` provides:
- `AsyncSMTPClient` class wrapping `aiosmtplib`
- `async def send_email(account: AccountCredentials, message: EmailMessage) -> str` method
- Returns message ID from SMTP server
- Handles connection, authentication, send, disconnect lifecycle
- Uses TLS/STARTTLS based on account configuration

**And** SMTP connection process:
1. Create SMTP connection to configured host/port
2. Start TLS if `smtp_starttls` enabled (default for port 587)
3. Authenticate with username (email) and password
4. Send email message
5. Retrieve message ID from server response
6. Disconnect cleanly

**And** Error handling for SMTP operations:
- Connection failures: `SMTPConnectionError` with host/port details
- Authentication failures: `SMTPAuthenticationError` with helpful message
- Send failures: `SMTPSendError` with specific error from server
- Timeout after 30 seconds (configurable)

**And** Logging for SMTP operations:
```
[INFO]  Connecting to SMTP host=smtp.gmail.com port=587
[INFO]  SMTP authenticated email=you@gmail.com
[INFO]  Email sent message_id=abc123 recipient=user@example.com
[ERROR] SMTP send failed error="Recipient address rejected"
```

**Prerequisites:** Epic 2 (account credentials available)

**Technical Notes:**
- Use `aiosmtplib` 5.0.0 (native async, MIT licensed per Architecture)
- Create Python `email.message.EmailMessage` objects
- Handle both STARTTLS (port 587) and SSL (port 465)
- Connection pooling deferred to Phase 2 (MVP: connect per send)
- FR-015: Send via SMTP with credentials
- FR-017: Handle SMTP errors gracefully
- Architecture reference: section "SMTP Integration (aiosmtplib - native async)"

---

### Story 3.2: Email Message Builder and Models

As a developer,  
I want Pydantic models for email composition,  
So that the API validates email structure and provides clear error messages for invalid requests.

**Acceptance Criteria:**

**Given** the API framework from Epic 1  
**When** implementing email models  
**Then** `src/mailreactor/models/message.py` provides:
- `SendEmailRequest` model for API input validation
- `SendEmailResponse` model for API output
- `EmailAddress` model for email addresses (with optional name)
- Validation for email addresses (RFC 5322 compliant)

**And** `SendEmailRequest` model includes:
- `to: List[EmailAddress]` - Required, at least one recipient
- `subject: str` - Required, non-empty
- `body_text: Optional[str]` - Plain text body
- `body_html: Optional[str]` - HTML body
- `cc: Optional[List[EmailAddress]]` - CC recipients
- `bcc: Optional[List[EmailAddress]]` - BCC recipients
- `reply_to: Optional[EmailAddress]` - Reply-To header
- `headers: Optional[Dict[str, str]]` - Custom headers
- `attachments: Optional[List[Attachment]]` - File attachments

**And** Validation rules:
- At least one of `body_text` or `body_html` must be provided
- Email addresses validated with Pydantic `EmailStr`
- Subject line max length: 998 characters (RFC 2822)
- At least one recipient in `to` field required
- Custom headers validated (no restricted headers like From, To, etc.)

**And** `Attachment` model includes:
- `filename: str` - Required
- `content: str` - Base64-encoded file content (MVP)
- `content_type: str` - MIME type (e.g., "application/pdf")
- Max attachment size: 10MB per file (configurable)

**And** `SendEmailResponse` model includes:
- `message_id: str` - SMTP message ID
- `status: str` - "sent" or "queued" (MVP always "sent")
- `timestamp: datetime` - When email was sent

**And** Error responses for validation failures:
```json
{
  "detail": "Validation error",
  "error_code": "VALIDATION_ERROR",
  "errors": [
    {"field": "to", "message": "At least one recipient required"},
    {"field": "body_text", "message": "Either body_text or body_html required"}
  ]
}
```

**Prerequisites:** Story 1.2 (Pydantic models framework)

**Technical Notes:**
- Use Pydantic validators for complex rules
- EmailStr validates RFC 5322 format
- Base64 encoding for attachments (simple, but size-limited for MVP)
- Phase 2: Multipart upload for large attachments
- FR-011: Send with to/subject/plain text
- FR-012: Send with HTML body
- FR-013: Send to multiple recipients (to, cc, bcc)
- FR-014: Send with attachments (base64)
- FR-018: Support custom headers

---

### Story 3.3: Send Email API Endpoint

As a developer,  
I want a REST API endpoint to send emails,  
So that I can integrate email sending into my application with simple HTTP requests.

**Acceptance Criteria:**

**Given** the SMTP client from Story 3.1 and models from Story 3.2  
**When** implementing the send endpoint  
**Then** `src/mailreactor/api/send.py` provides:
- `POST /accounts/{account_id}/send` endpoint
- Accepts `SendEmailRequest` in JSON body
- Returns `SendEmailResponse` with message ID and status

**And** Send email flow:
1. Validate account_id exists in StateManager
2. Validate request body (Pydantic automatic)
3. Retrieve account credentials
4. Build `EmailMessage` from request:
   - Set From header (account email)
   - Set To, CC, BCC headers
   - Set Subject
   - Set plain text and/or HTML body (MIME multipart if both)
   - Attach files if provided (base64 decode)
   - Set custom headers if provided
5. Send via `AsyncSMTPClient`
6. Return message ID and timestamp

**And** MIME handling:
- Plain text only: `text/plain` message
- HTML only: `text/html` message
- Both: `multipart/alternative` with text and HTML parts
- With attachments: `multipart/mixed` with content and attachments

**And** Response examples:

**Success (201 Created):**
```json
{
  "message_id": "<abc123@gmail.com>",
  "status": "sent",
  "timestamp": "2025-11-25T10:30:45Z"
}
```

**Error (400 Bad Request - validation):**
```json
{
  "detail": "Validation error",
  "error_code": "VALIDATION_ERROR",
  "errors": [{"field": "to", "message": "Invalid email address"}]
}
```

**Error (404 Not Found - account):**
```json
{
  "detail": "Account acc_123 not found",
  "error_code": "ACCOUNT_NOT_FOUND"
}
```

**Error (503 Service Unavailable - SMTP):**
```json
{
  "detail": "SMTP server unavailable",
  "error_code": "SMTP_CONNECTION_ERROR"
}
```

**And** OpenAPI documentation includes:
- Full request/response schemas
- Example request with all fields
- All possible error responses
- Code examples in curl, Python, JavaScript

**Prerequisites:** Stories 3.1 (SMTP client), 3.2 (models), 2.5 (account retrieval)

**Technical Notes:**
- Use Python `email` stdlib for MIME message construction
- Base64 decode attachments before adding to message
- Validate attachment MIME types (basic validation)
- FR-011 to FR-018: All email sending FRs
- FR-016: Return message ID and status
- Architecture reference: section "API Endpoint Pattern"
- NFR-P2: API response time target (200ms p95, excluding SMTP)

---

### Story 3.4: Email Sending Error Handling and User Guidance

As a developer,  
I want clear, actionable error messages when email sending fails,  
So that I can quickly diagnose and fix issues without digging through documentation.

**Acceptance Criteria:**

**Given** the send email endpoint from Story 3.3  
**When** email sending fails  
**Then** error responses include:
- Specific error code (machine-readable)
- Human-readable error message
- Suggested remediation steps (where applicable)
- Link to relevant documentation

**And** Common error scenarios with helpful messages:

**SMTP Authentication Failed:**
```json
{
  "detail": "SMTP authentication failed for you@gmail.com",
  "error_code": "SMTP_AUTH_FAILED",
  "help": "For Gmail, use an App Password instead of your regular password. See: https://support.google.com/accounts/answer/185833"
}
```

**Invalid Recipient:**
```json
{
  "detail": "Recipient address rejected: invalid@nonexistent-domain-xyz.com",
  "error_code": "RECIPIENT_REJECTED",
  "help": "Verify the recipient email address is valid and properly formatted"
}
```

**Attachment Too Large:**
```json
{
  "detail": "Attachment 'document.pdf' exceeds maximum size (10MB)",
  "error_code": "ATTACHMENT_TOO_LARGE",
  "help": "Reduce attachment size or split into multiple emails"
}
```

**Rate Limited (if detected from SMTP):**
```json
{
  "detail": "SMTP server rate limit exceeded",
  "error_code": "SMTP_RATE_LIMITED",
  "help": "Wait before sending more emails. Gmail limits: 500/day for personal accounts"
}
```

**Connection Timeout:**
```json
{
  "detail": "Connection to SMTP server timed out after 30s",
  "error_code": "SMTP_TIMEOUT",
  "help": "Check network connectivity and firewall settings. Verify SMTP host and port."
}
```

**And** Logging includes full context for troubleshooting:
```
[ERROR] SMTP authentication failed account=you@gmail.com host=smtp.gmail.com error="535 Authentication failed"
[ERROR] Recipient rejected recipient=invalid@domain.com error="550 Address not found"
[ERROR] Attachment too large filename=document.pdf size_mb=15.2 limit_mb=10
```

**And** Provider-specific guidance:
- Gmail: Mention App Passwords requirement for 2FA accounts
- Outlook: Mention modern auth / OAuth requirement for some accounts
- Generic: Provide standard troubleshooting steps

**Prerequisites:** Story 3.3 (send endpoint), Story 1.7 (error response standards)

**Technical Notes:**
- Parse SMTP error codes (535, 550, 552, etc.) and map to helpful messages
- Include documentation links in error responses
- Consider provider-specific error handling (detect from account config)
- FR-017: Handle SMTP errors gracefully with meaningful messages
- FR-031: Clear error messages for common failure scenarios
- Architecture reference: section "Error Handling Pattern"

---

### Story 3.5: Email Sending Integration Tests

As a developer,  
I want comprehensive integration tests for email sending,  
So that the send functionality is reliable and regressions are caught early.

**Acceptance Criteria:**

**Given** the send email endpoint from Story 3.3  
**When** writing integration tests  
**Then** `tests/integration/test_send_email.py` provides:
- Mock SMTP server for testing (no real emails sent)
- Tests for all send scenarios (plain text, HTML, attachments, multiple recipients)
- Tests for all error scenarios (auth failure, invalid recipient, etc.)
- Tests for MIME message construction

**And** Test coverage includes:

**Success scenarios:**
- Send plain text email
- Send HTML email
- Send multipart (text + HTML)
- Send with single attachment
- Send with multiple attachments
- Send to multiple recipients (to, cc, bcc)
- Send with custom headers
- Send with Reply-To header

**Error scenarios:**
- Account not found (404)
- Invalid email address in 'to' field (400)
- Missing subject (400)
- Missing both body_text and body_html (400)
- SMTP connection failure (503)
- SMTP authentication failure (503)
- Attachment exceeds size limit (400)
- Invalid base64 in attachment (400)

**And** Mock SMTP server:
- Uses `aiosmtpd` for test SMTP server
- Captures sent messages for assertion
- Simulates success and failure responses
- No network calls in tests (fully mocked)

**And** Test assertions verify:
- Correct MIME structure
- Proper header encoding
- Base64 attachment decoding
- From/To/Subject headers correct
- Message ID returned in response
- Error responses match specification

**Prerequisites:** Story 3.3 (send endpoint complete), Story 1.1 (pytest setup)

**Technical Notes:**
- Use `aiosmtpd` for mock SMTP server (async-friendly)
- Use `pytest-asyncio` for async test support
- Mock at SMTP level (not HTTP level) for realistic testing
- Test coverage target: 80%+ for send module
- Architecture reference: section "Testing: pytest + pytest-asyncio"

---

## Epic 3 Summary

**Stories Completed:** 5  
**FRs Delivered:** 8 (FR-011 to FR-018)  
**User Value:** Developers can now send emails via REST API - the first core capability delivered. Transactional emails, password resets, notifications all become simple HTTP POST requests.

**What Developers Can Do:**
✅ Send plain text emails via `POST /accounts/{id}/send`  
✅ Send HTML emails (or multipart text+HTML)  
✅ Send to multiple recipients (to, cc, bcc)  
✅ Add file attachments (base64-encoded, up to 10MB)  
✅ Set custom headers (Reply-To, custom headers)  
✅ Get message ID back for tracking  
✅ Receive clear error messages when sending fails  

**Example Usage:**
```bash
curl -X POST http://localhost:8000/accounts/acc_123/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": [{"email": "user@example.com"}],
    "subject": "Password Reset",
    "body_text": "Click here to reset your password...",
    "body_html": "<p>Click here to reset your password...</p>"
  }'
```

**Next:** Epic 4 will enable developers to retrieve and search emails via REST API.

---

## Epic 4: Email Retrieval & Search

**Goal:** Developers can retrieve and search emails using IMAP syntax via REST API, enabling support ticket ingestion, email-based authentication flows, and inbound email processing.

**User Value:** Core capability #2 - process inbound emails, search mailboxes, implement email-based workflows. Completes the send/receive cycle.

**FRs Covered:** FR-019 to FR-026 (Email Retrieval & Search)

---

### Story 4.1: IMAP Client Wrapper with Async Executor Pattern

As a developer,  
I want an async IMAP client abstraction,  
So that email retrieval doesn't block the API server and integrates cleanly with FastAPI.

**Acceptance Criteria:**

**Given** the account management from Epic 2  
**When** implementing IMAP client wrapper  
**Then** `src/mailreactor/core/imap_client.py` provides:
- `AsyncIMAPClient` class wrapping `IMAPClient` with async executor pattern
- `async def connect(account: AccountCredentials) -> IMAPClient` method
- `async def search(client: IMAPClient, criteria: List[str]) -> List[int]` method
- `async def fetch_messages(client: IMAPClient, uids: List[int]) -> List[Message]` method
- All IMAP operations run in thread pool executor (non-blocking)

**And** IMAP connection process:
1. Create IMAP connection to configured host/port
2. Use SSL if `imap_ssl` enabled (default for port 993)
3. Authenticate with username (email) and password
4. Select INBOX folder (or specified folder)
5. Return connected client for subsequent operations

**And** Async executor pattern implementation:
```python
async def _run_sync(self, func, *args, **kwargs):
    """Execute sync IMAPClient method in thread pool"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        self._executor,
        partial(func, *args, **kwargs)
    )
```

**And** IMAP search criteria support (server-side filtering):
- `UNSEEN` - Unread messages
- `SEEN` - Read messages
- `FROM <email>` - From specific sender
- `TO <email>` - To specific recipient
- `SUBJECT <text>` - Subject contains text
- `SINCE <date>` - After specific date
- `BEFORE <date>` - Before specific date
- `BODY <text>` - Body contains text
- Combined criteria with AND logic

**And** Error handling for IMAP operations:
- Connection failures: `IMAPConnectionError` with host/port details
- Authentication failures: `IMAPAuthenticationError` with helpful message
- Search failures: `IMAPSearchError` with query details
- Timeout after 10 seconds per operation (configurable)

**And** Logging for IMAP operations:
```
[INFO]  Connecting to IMAP host=imap.gmail.com port=993
[INFO]  IMAP authenticated email=you@gmail.com folder=INBOX
[INFO]  IMAP search criteria=["UNSEEN"] results=5
[ERROR] IMAP connection failed error="Connection refused"
```

**Prerequisites:** Epic 2 (account credentials available)

**Technical Notes:**
- Use `IMAPClient` 3.0.1 (BSD-3 licensed, production-stable per Architecture)
- Wrap synchronous IMAPClient with `asyncio.run_in_executor()`
- Use ThreadPoolExecutor for IMAP operations (CPU-bound parsing)
- Connection pooling deferred to Phase 2 (MVP: connect per request)
- FR-005: Connect to IMAP server
- FR-020: Support standard IMAP search criteria
- FR-024: Server-side filtering (IMAP SEARCH executes on server)
- Architecture reference: section "IMAP Integration (IMAPClient + asyncio executor)"
- ADR-002: Use IMAPClient with Async Executor Pattern

---

### Story 4.2: Email Message Parser and Normalization

As a developer,  
I want email messages parsed into structured JSON,  
So that I can easily work with email data without dealing with raw MIME parsing.

**Acceptance Criteria:**

**Given** raw email messages from IMAP  
**When** implementing message parser  
**Then** `src/mailreactor/core/message_parser.py` provides:
- `parse_message(raw_message: bytes) -> Message` function
- Extracts envelope (From, To, CC, Subject, Date, Message-ID)
- Extracts plain text body
- Extracts HTML body
- Identifies attachments (filename, content-type, size)
- Handles multipart MIME messages correctly

**And** `Message` model (from Story 3.2, enhanced for retrieval) includes:
- `uid: int` - IMAP UID (unique identifier)
- `message_id: str` - Email Message-ID header
- `from_: EmailAddress` - Sender
- `to: List[EmailAddress]` - Recipients
- `cc: List[EmailAddress]` - CC recipients
- `subject: str` - Email subject
- `date: datetime` - Email date
- `body_text: Optional[str]` - Plain text body
- `body_html: Optional[str]` - HTML body
- `attachments: List[AttachmentInfo]` - Attachment metadata
- `flags: List[str]` - IMAP flags (\\Seen, \\Flagged, etc.)
- `headers: Dict[str, str]` - Full email headers (optional)

**And** `AttachmentInfo` model includes:
- `filename: str` - Attachment filename
- `content_type: str` - MIME type
- `size_bytes: int` - File size
- `attachment_id: str` - Identifier for retrieving full content

**And** Email parsing handles:
- UTF-8 and other character encodings
- Quoted-printable encoding
- Base64 encoding
- Multipart MIME (alternative, mixed, related)
- Inline images vs attachments
- Malformed emails (graceful degradation)

**And** Body preview generation:
- Plain text: First 500 characters
- HTML: Strip tags, first 500 characters of text content
- Truncate with "..." if longer

**And** Error handling:
- Unparseable emails logged but don't crash
- Missing headers use defaults (empty string, None, etc.)
- Invalid dates fall back to IMAP INTERNALDATE

**Prerequisites:** Story 4.1 (IMAP client returns raw messages)

**Technical Notes:**
- Use Python `email` stdlib for MIME parsing
- Use `email.policy.default` for modern parsing behavior
- Handle RFC 2047 encoded headers (=?UTF-8?B?...?=)
- Attachment IDs: `{uid}_{attachment_index}` for retrieval
- FR-021: Return structured JSON
- FR-022: Retrieve full email details
- Architecture reference: section "Core business logic - message_parser.py"

---

### Story 4.3: List Messages API Endpoint with Search

As a developer,  
I want a REST API endpoint to search and list emails,  
So that I can query mailboxes using IMAP search syntax via simple HTTP requests.

**Acceptance Criteria:**

**Given** the IMAP client from Story 4.1 and parser from Story 4.2  
**When** implementing the list messages endpoint  
**Then** `src/mailreactor/api/messages.py` provides:
- `GET /accounts/{account_id}/messages` endpoint
- Query parameters: `folder`, `search`, `limit`, `include_body`
- Returns paginated list of messages

**And** Query parameters:
- `folder` (optional, default: "INBOX") - IMAP folder to search
- `search` (optional, default: "ALL") - IMAP search criteria
- `limit` (optional, default: 50, max: 1000) - Number of messages to return
- `include_body` (optional, default: false) - Include full body in response

**And** IMAP search syntax examples:
- `?search=UNSEEN` - Unread messages only
- `?search=FROM+user@example.com` - From specific sender
- `?search=SINCE+01-Jan-2025` - Since specific date
- `?search=SUBJECT+password` - Subject contains "password"
- `?search=UNSEEN+FROM+user@example.com` - Combined criteria (AND)

**And** List messages flow:
1. Validate account_id exists
2. Retrieve account credentials
3. Connect to IMAP server
4. Select specified folder
5. Execute IMAP SEARCH with criteria (server-side filtering)
6. Fetch message UIDs from search results
7. Fetch message envelopes and bodies (limited by `limit` parameter)
8. Parse messages into structured format
9. Return JSON response

**And** Response format (200 OK):
```json
{
  "messages": [
    {
      "uid": 12345,
      "message_id": "<abc@example.com>",
      "from": {"email": "sender@example.com", "name": "John Doe"},
      "to": [{"email": "you@gmail.com"}],
      "subject": "Password Reset Request",
      "date": "2025-11-25T10:30:45Z",
      "body_preview": "Please click the following link...",
      "has_attachments": false,
      "flags": ["\\Seen"]
    }
  ],
  "count": 1,
  "folder": "INBOX",
  "has_more": false
}
```

**And** Response with `include_body=true`:
- Adds `body_text` and `body_html` fields to each message
- Adds `attachments` array with full attachment metadata
- Slower, but complete message details

**And** Error responses:
- 404: Account not found
- 400: Invalid search criteria
- 503: IMAP connection failed

**And** Performance optimization:
- Fetch only envelope for preview mode (`include_body=false`)
- Fetch full body only when requested
- Limit enforced to prevent large responses

**Prerequisites:** Stories 4.1 (IMAP client), 4.2 (message parser), 2.5 (account retrieval)

**Technical Notes:**
- IMAP SEARCH executed on server (efficient, per FR-024)
- Fetch envelope only for list view (fast)
- Fetch full body on-demand for details view
- FR-019: Query emails with IMAP search syntax
- FR-020: Support standard IMAP criteria
- FR-021: Return structured JSON
- FR-023: Cursor-based pagination (deferred to Phase 2, limit-based for MVP)
- FR-024: Server-side filtering
- Architecture reference: section "API Endpoint Pattern"

---

### Story 4.4: Get Single Message Details API Endpoint

As a developer,  
I want a REST API endpoint to retrieve full details of a specific email,  
So that I can fetch complete email content including body and attachments.

**Acceptance Criteria:**

**Given** the IMAP client and parser from Stories 4.1-4.2  
**When** implementing get message endpoint  
**Then** `src/mailreactor/api/messages.py` provides:
- `GET /accounts/{account_id}/messages/{uid}` endpoint
- Returns complete message details including body and attachments

**And** Get message flow:
1. Validate account_id exists
2. Validate uid is valid integer
3. Retrieve account credentials
4. Connect to IMAP server
5. Fetch message by UID
6. Parse message (full details)
7. Return JSON response

**And** Response format (200 OK):
```json
{
  "uid": 12345,
  "message_id": "<abc@example.com>",
  "from": {"email": "sender@example.com", "name": "John Doe"},
  "to": [{"email": "you@gmail.com"}],
  "cc": [],
  "subject": "Password Reset Request",
  "date": "2025-11-25T10:30:45Z",
  "body_text": "Please click the following link to reset your password...",
  "body_html": "<p>Please click the following link...</p>",
  "attachments": [
    {
      "filename": "document.pdf",
      "content_type": "application/pdf",
      "size_bytes": 102400,
      "attachment_id": "12345_0"
    }
  ],
  "flags": ["\\Seen"],
  "headers": {
    "Return-Path": "sender@example.com",
    "Received": "...",
    "X-Custom-Header": "value"
  }
}
```

**And** Response includes:
- Full plain text body
- Full HTML body (if present)
- Attachment metadata (not content - too large)
- All email headers
- IMAP flags

**And** Error responses:
- 404: Account not found or message UID not found
- 503: IMAP connection failed

**And** Attachment content retrieval (separate endpoint):
- `GET /accounts/{account_id}/messages/{uid}/attachments/{attachment_id}`
- Returns raw attachment content with proper Content-Type header
- Deferred to Story 4.5

**Prerequisites:** Stories 4.1 (IMAP client), 4.2 (message parser)

**Technical Notes:**
- Fetch full RFC822 message from IMAP
- Parse headers, body, attachments
- Don't include attachment content in JSON (use separate endpoint)
- Mark message as \\Seen when fetched (standard IMAP behavior)
- FR-022: Retrieve full email details including headers, body, attachments
- Architecture reference: section "API Endpoint Pattern"

---

### Story 4.5: Attachment Download Endpoint

As a developer,  
I want a REST API endpoint to download email attachments,  
So that I can retrieve attachment content separately from email metadata.

**Acceptance Criteria:**

**Given** the message retrieval from Story 4.4  
**When** implementing attachment download endpoint  
**Then** `src/mailreactor/api/messages.py` provides:
- `GET /accounts/{account_id}/messages/{uid}/attachments/{attachment_id}` endpoint
- Returns raw attachment content with proper headers

**And** Attachment download flow:
1. Validate account_id exists
2. Parse attachment_id (format: `{uid}_{index}`)
3. Retrieve account credentials
4. Connect to IMAP server
5. Fetch message by UID
6. Extract attachment by index
7. Return raw attachment content

**And** Response headers:
- `Content-Type`: Attachment MIME type (e.g., `application/pdf`)
- `Content-Disposition`: `attachment; filename="document.pdf"`
- `Content-Length`: File size in bytes

**And** Response body:
- Raw binary attachment content
- No JSON wrapping

**And** Error responses:
- 404: Account, message, or attachment not found
- 400: Invalid attachment_id format
- 503: IMAP connection failed

**And** Example usage:
```bash
curl http://localhost:8000/accounts/acc_123/messages/12345/attachments/12345_0 \
  --output document.pdf
```

**Prerequisites:** Story 4.4 (message retrieval with attachment metadata)

**Technical Notes:**
- Parse attachment_id to get UID and attachment index
- Fetch message, extract specific attachment
- Return raw bytes with proper Content-Type
- Consider streaming for large attachments (Phase 2)
- Browser will trigger download due to Content-Disposition header
- Architecture reference: section "API Endpoint Pattern"

---

### Story 4.6: In-Memory Email Caching

As a developer,  
I want recently fetched emails cached in memory,  
So that repeated queries are fast without repeatedly hitting the IMAP server.

**Acceptance Criteria:**

**Given** the message retrieval from Stories 4.3-4.4  
**When** implementing caching  
**Then** `src/mailreactor/core/state_manager.py` is enhanced with:
- `MessageCache` class for in-memory message caching
- TTL-based cache expiration (default: 5 minutes)
- LRU eviction when cache size limit reached

**And** Cache key structure:
- `{account_id}:{folder}:{uid}` for individual messages
- `{account_id}:{folder}:search:{criteria}` for search results

**And** Cache behavior:
- First fetch: Query IMAP, store in cache, return result
- Subsequent fetch (within TTL): Return from cache (no IMAP call)
- After TTL expiry: Re-fetch from IMAP, update cache
- Cache size limit: 1000 messages (configurable)

**And** Cache operations:
- `get_message(account_id, folder, uid)` - Returns cached or fetches
- `get_search_results(account_id, folder, criteria)` - Returns cached UIDs
- `invalidate(account_id, folder, uid)` - Clear specific message
- `clear_account(account_id)` - Clear all cached messages for account

**And** Cache eviction:
- TTL-based: Remove after 5 minutes (configurable)
- LRU-based: Remove least recently used when size limit reached
- Account removal: Clear all cached messages for that account

**And** Logging for cache operations:
```
[DEBUG] Message cache hit account=acc_123 folder=INBOX uid=12345
[DEBUG] Message cache miss account=acc_123 folder=INBOX uid=67890
[DEBUG] Message cache evicted count=50 reason=size_limit
```

**Prerequisites:** Stories 4.3-4.4 (message retrieval working), Story 2.6 (StateManager exists)

**Technical Notes:**
- Use Python dict with timestamps for simple TTL cache
- Check timestamp on cache hit, re-fetch if expired
- LRU: Track access times, evict oldest when limit reached
- Thread-safe: Use asyncio locks for cache access
- Phase 2: Consider Redis for shared cache across instances
- FR-025: In-memory caching of recently retrieved emails
- NFR-P4: Memory footprint - efficient cache with size limits
- Architecture reference: section "State Management (MVP - In-Memory)"

---

### Story 4.7: Configurable Email Ingestion Time Window

As a developer,  
I want to limit email ingestion to a configurable time window,  
So that Mail Reactor doesn't fetch my entire mailbox history on every query.

**Acceptance Criteria:**

**Given** the IMAP search from Story 4.3  
**When** implementing time window filtering  
**Then** configuration supports:
- `MAILREACTOR_EMAIL_WINDOW_DAYS` environment variable (default: 30)
- Automatically adds `SINCE` clause to IMAP searches
- Limits email retrieval to recent messages only

**And** Time window behavior:
- Default: Last 30 days of email
- User search: `?search=UNSEEN` → Auto-enhanced to: `UNSEEN SINCE <30 days ago>`
- User search: `?search=FROM+user@example.com` → Auto-enhanced: `FROM user@example.com SINCE <30 days ago>`
- User explicit SINCE: `?search=SINCE+01-Jan-2024` → User override respected (no auto-enhancement)

**And** Configuration options:
- `MAILREACTOR_EMAIL_WINDOW_DAYS=30` (default)
- `MAILREACTOR_EMAIL_WINDOW_DAYS=7` (last week only)
- `MAILREACTOR_EMAIL_WINDOW_DAYS=0` (no limit, all emails)
- Configurable per deployment

**And** Startup logging:
```
[INFO]  Email ingestion window configured days=30
[INFO]  Email searches limited to since=2025-10-26T00:00:00Z
```

**And** Search query logging shows enhancement:
```
[DEBUG] Original search criteria=["UNSEEN"]
[DEBUG] Enhanced search criteria=["UNSEEN", "SINCE", "26-Oct-2025"]
```

**Prerequisites:** Story 4.3 (IMAP search working), Story 1.2 (Settings configuration)

**Technical Notes:**
- Add to Pydantic Settings: `email_window_days: int = 30`
- Enhance search criteria in IMAP client before executing
- Date format for IMAP: "DD-Mon-YYYY" (e.g., "26-Oct-2025")
- Detect user-provided SINCE/BEFORE to avoid double-filtering
- FR-026: Configure time window for email ingestion
- NFR-P3: IMAP search performance - limiting scope improves speed
- Architecture reference: section "Configuration Pattern"

---

## Epic 4 Summary

**Stories Completed:** 7  
**FRs Delivered:** 8 (FR-019 to FR-026)  
**User Value:** Developers can now retrieve and search emails via REST API - the second core capability delivered. Support ticket ingestion, email-based auth flows, inbound email processing all become simple HTTP GET requests.

**What Developers Can Do:**
✅ Search emails with IMAP syntax: `GET /accounts/{id}/messages?search=UNSEEN+FROM+user@example.com`  
✅ List messages from any folder with server-side filtering  
✅ Get full message details including headers and body  
✅ Download email attachments via separate endpoint  
✅ Fast queries via in-memory caching (5-minute TTL)  
✅ Limit search scope to recent emails (configurable time window)  
✅ Process inbound emails for support tickets, auth flows, workflows  

**Example Usage:**
```bash
# Search for unread emails
curl "http://localhost:8000/accounts/acc_123/messages?search=UNSEEN"

# Get full message details
curl "http://localhost:8000/accounts/acc_123/messages/12345"

# Download attachment
curl "http://localhost:8000/accounts/acc_123/messages/12345/attachments/12345_0" \
  --output document.pdf
```

**Performance:**
- Server-side IMAP filtering (efficient, doesn't download all emails)
- In-memory caching (repeated queries are fast)
- Time window limiting (default: last 30 days only)
- Envelope-only fetching for list view (fast preview)

**Next:** Epic 5 will add production-ready API key authentication.

---

## Epic 5: Production-Ready Security

**Goal:** Developers can secure their Mail Reactor instance with API key authentication for production deployment beyond localhost.

**User Value:** Move from localhost development to production-ready deployment with proper authentication. Essential for remote deployments, Docker containers, and team access.

**FRs Covered:** FR-041 to FR-045 (API Key Authentication)

---

### Story 5.1: API Key Generation and Storage

As a developer,  
I want to generate API keys for authentication,  
So that I can secure my Mail Reactor instance when deploying to production.

**Acceptance Criteria:**

**Given** the settings configuration from Epic 1  
**When** implementing API key support  
**Then** `src/mailreactor/core/auth.py` provides:
- `generate_api_key() -> str` function (generates secure random key)
- `hash_api_key(api_key: str) -> str` function (bcrypt hashing)
- `verify_api_key(api_key: str, hashed: str) -> bool` function
- API key format: `mr_` prefix + 32 random characters (e.g., `mr_abc123def456...`)

**And** Settings configuration supports:
- `api_key: Optional[str]` - Single API key (plaintext, from env var or CLI flag)
- `api_key_file: Optional[str]` - Path to file containing API key
- `api_key_auto: bool = False` - Auto-generate key on first start

**And** API key configuration options:

**Option 1 - Environment variable:**
```bash
export MAILREACTOR_API_KEY=mr_your_secret_key_here
mailreactor start
```

**Option 2 - CLI flag:**
```bash
mailreactor start --api-key mr_your_secret_key_here
```

**Option 3 - Auto-generate:**
```bash
mailreactor start --api-key-auto
```
Output:
```
[INFO]  API key auto-generated (save this securely)
[INFO]  API Key: mr_abc123def456...
[WARN]  This key will only be shown once!
```

**Option 4 - From file:**
```bash
echo "mr_your_secret_key_here" > /secrets/mailreactor.key
mailreactor start --api-key-file /secrets/mailreactor.key
```

**And** API key storage:
- Hashed with bcrypt before storing in StateManager
- Never logged in plaintext
- Never returned in API responses
- Cleared from memory on shutdown

**And** Startup logging:
```
[INFO]  API key authentication enabled
[WARN]  API key required for all API requests
```

**Or if no key:**
```
[WARN]  No API key configured - authentication disabled ⚠
[WARN]  Anyone can access this API! Only use on localhost.
```

**Prerequisites:** Story 1.2 (Settings), Story 2.6 (StateManager)

**Technical Notes:**
- Use `secrets` module for cryptographically secure random generation
- Use `bcrypt` for hashing (industry standard, designed for passwords)
- Key format: `mr_` prefix for easy identification (like Stripe keys: `sk_`, `pk_`)
- 32-character random part (base62: alphanumeric) = ~190 bits entropy
- Store hashed key in StateManager (in-memory for MVP)
- FR-041: Enable API key via CLI flag
- FR-042: Auto-generate API key
- FR-045: Store API keys securely (hashed)
- NFR-S1: Credentials never logged or exposed
- NFR-S2: API keys stored using secure hashing (bcrypt)

---

### Story 5.2: API Key Authentication Middleware

As a developer,  
I want API key authentication enforced on all endpoints,  
So that unauthorized users cannot access my Mail Reactor instance.

**Acceptance Criteria:**

**Given** API key configuration from Story 5.1  
**When** implementing authentication middleware  
**Then** `src/mailreactor/api/dependencies.py` provides:
- `verify_api_key` FastAPI dependency
- Checks `Authorization: Bearer {api_key}` header (standard)
- Also checks `X-API-Key: {api_key}` header (alternative, common in APIs)
- Returns 401 Unauthorized if missing or invalid

**And** Authentication flow:
1. Check if API key authentication enabled (Settings.api_key exists)
2. If disabled: Allow request (no auth required)
3. If enabled:
   - Extract key from `Authorization: Bearer {key}` OR `X-API-Key: {key}` header
   - If missing: Return 401 with error message
   - If present: Verify against stored hashed key
   - If invalid: Return 401 with error message
   - If valid: Allow request

**And** Protected endpoints (all except health):
- `POST /accounts`
- `GET /accounts`
- `GET /accounts/{id}`
- `DELETE /accounts/{id}`
- `POST /accounts/{id}/send`
- `GET /accounts/{id}/messages`
- `GET /accounts/{id}/messages/{uid}`
- All other future endpoints

**And** Unprotected endpoints (always accessible):
- `GET /health` - Health check for monitoring
- `GET /docs` - OpenAPI documentation (consider making this configurable in Phase 2)
- `GET /redoc` - ReDoc documentation
- `GET /openapi.json` - OpenAPI spec

**And** Error response for missing API key (401):
```json
{
  "detail": "API key required. Provide via Authorization: Bearer {key} or X-API-Key header.",
  "error_code": "AUTH_REQUIRED"
}
```

**And** Error response for invalid API key (401):
```json
{
  "detail": "Invalid API key",
  "error_code": "AUTH_INVALID"
}
```

**And** Example authenticated requests:

**Authorization header (standard):**
```bash
curl -H "Authorization: Bearer mr_abc123..." \
  http://localhost:8000/accounts
```

**X-API-Key header (alternative):**
```bash
curl -H "X-API-Key: mr_abc123..." \
  http://localhost:8000/accounts
```

**Prerequisites:** Story 5.1 (API key generation), Story 1.2 (FastAPI dependencies)

**Technical Notes:**
- Use FastAPI `Depends()` for dependency injection
- Check both header types for flexibility
- Constant-time comparison for API key verification (prevent timing attacks)
- Log failed auth attempts at WARN level
- FR-043: Require bearer token when auth enabled
- FR-044: Return 401 for invalid authentication
- NFR-S2: API keys transmitted over HTTPS only (localhost HTTP acceptable for MVP)
- Architecture reference: section "API Endpoint Pattern" with auth dependency

---

### Story 5.3: API Key Security and Best Practices Documentation

As a developer,  
I want clear documentation on API key security best practices,  
So that I can deploy Mail Reactor securely and avoid common mistakes.

**Acceptance Criteria:**

**Given** API key authentication from Stories 5.1-5.2  
**When** creating security documentation  
**Then** OpenAPI docs include security scheme:
- `ApiKeyAuth` security scheme defined
- Shows in Swagger UI "Authorize" button
- Interactive testing with API key

**And** Startup warnings guide users:

**No API key:**
```
[WARN]  No API key configured - authentication disabled ⚠
[WARN]  Anyone can access this API! Only use on localhost.
[INFO]  To enable auth: mailreactor start --api-key YOUR_KEY
```

**API key enabled:**
```
[INFO]  API key authentication enabled ✓
[INFO]  All API requests require Authorization header
```

**API key auto-generated:**
```
[INFO]  API key auto-generated (save this securely!)
[INFO]  
[INFO]  ═══════════════════════════════════════
[INFO]   API Key: mr_abc123def456...
[INFO]  ═══════════════════════════════════════
[INFO]  
[WARN]  This key will only be shown once!
[WARN]  Save it to: export MAILREACTOR_API_KEY=mr_abc123...
```

**And** README includes security section:
- How to generate API keys
- How to configure API keys (env var, CLI, file)
- When to use API keys (production, remote access)
- When NOT to use API keys (localhost development)
- HTTPS recommendation for remote deployments
- Reverse proxy setup (Nginx, Caddy) for HTTPS

**And** API documentation includes examples with authentication:
- All curl examples show `-H "Authorization: Bearer {key}"`
- Python examples show `headers={"Authorization": "Bearer {key}"}`
- JavaScript examples show `headers: {"Authorization": "Bearer {key}"}`

**Prerequisites:** Stories 5.1-5.2 (authentication implemented)

**Technical Notes:**
- Update OpenAPI security schemes in FastAPI app
- Add security examples to all endpoint docs
- Consider adding `/docs` authentication in Phase 2 (currently public)
- FR-040: Warn on startup when authentication disabled
- NFR-S3: Network security best practices documented
- Architecture reference: section "API Documentation Strategy"

---

## Epic 5 Summary

**Stories Completed:** 3  
**FRs Delivered:** 5 (FR-041 to FR-045)  
**User Value:** Developers can now deploy Mail Reactor to production with proper API key authentication. Essential for Docker deployments, remote access, and multi-user scenarios.

**What Developers Can Do:**
✅ Generate API keys: `mailreactor start --api-key-auto`  
✅ Configure via environment: `export MAILREACTOR_API_KEY=mr_key`  
✅ Configure via CLI flag: `mailreactor start --api-key mr_key`  
✅ Load from file: `mailreactor start --api-key-file /secrets/key`  
✅ Secure all endpoints (except /health) with API key  
✅ Use standard `Authorization: Bearer` header or `X-API-Key` header  

**Security Features:**
- Bcrypt hashed keys (never stored in plaintext)
- Cryptographically secure key generation
- Constant-time comparison (timing attack prevention)
- Failed auth attempts logged
- Clear warnings when auth disabled

**Example Production Deployment:**
```bash
# Docker deployment with API key
docker run -d \
  -e MAILREACTOR_API_KEY=mr_your_secure_key_here \
  -p 8000:8000 \
  mailreactor/mailreactor:latest

# All requests require authentication
curl -H "Authorization: Bearer mr_your_secure_key_here" \
  http://your-server:8000/accounts
```

**Next:** Epic 6 (optional) adds experimental IMAP-as-database state persistence.

---

## Epic 6: Experimental IMAP-as-Database (Optional)

**Goal:** Developers can optionally enable state persistence using IMAP itself as a storage mechanism, eliminating the need for external databases.

**User Value:** Lightweight persistence without external dependencies for users who need state across restarts but don't want to run Redis/PostgreSQL.

**Status:** EXPERIMENTAL - Validate with real-world usage before promoting to stable

**FRs Covered:** FR-046 to FR-054 (State Management - Experimental)

---

### Story 6.1: IMAP State Folder Management

As a developer,  
I want Mail Reactor to create and manage a dedicated IMAP folder for state storage,  
So that state data is isolated from regular email and easy to identify.

**Acceptance Criteria:**

**Given** IMAP-as-database mode enabled via `--enable-imap-state` flag  
**When** initializing state persistence  
**Then** `src/mailreactor/core/imap_state.py` provides:
- `IMAPStateManager` class for state operations
- Creates `.MailReactor-State` hidden folder in IMAP account
- Subfolder structure for different state types

**And** IMAP folder structure:
```
.MailReactor-State/
  ├── webhooks/          # Webhook delivery tracking
  ├── sync-cursors/      # Last-synced message UIDs
  └── metadata/          # Application metadata
```

**And** Folder creation flow:
1. Connect to IMAP
2. Check if `.MailReactor-State` folder exists
3. If not: Create folder (may require special IMAP permissions)
4. Create subfolders if needed
5. Log success or failure

**And** Provider compatibility checks:
- Gmail: Test folder creation (may have limitations)
- Outlook: Test folder creation
- Self-hosted: Test folder creation
- Document provider-specific quirks

**And** Error handling:
- Folder creation fails: Log error, fall back to stateless mode
- Permission denied: Log warning, continue without persistence
- Graceful degradation: State persistence is optional, not required

**And** Logging:
```
[INFO]  IMAP state persistence enabled (experimental)
[INFO]  Creating state folder folder=.MailReactor-State
[INFO]  State folder created successfully
```

Or:
```
[WARN]  State folder creation failed (continuing without persistence)
[WARN]  Provider may not support custom folders
```

**Prerequisites:** Story 4.1 (IMAP client), Story 1.2 (Settings with feature flags)

**Technical Notes:**
- Use IMAP CREATE command for folder creation
- Hidden folder convention: leading dot (`.MailReactor-State`)
- Some providers may reject folder creation (handle gracefully)
- FR-048: Optional IMAP-as-database mode
- FR-049: Write state to dedicated IMAP folder
- PRD Innovation section: IMAP-as-Database pattern

---

### Story 6.2: State Serialization and IMAP Storage

As a developer,  
I want application state written to IMAP as structured emails,  
So that state persists across restarts without external databases.

**Acceptance Criteria:**

**Given** IMAP state folder from Story 6.1  
**When** persisting state to IMAP  
**Then** state is written as email messages with JSON payloads:

**State email format:**
- **Subject:** `MailReactor-State: {state_type} {timestamp}`
- **From:** Account email (self-addressed)
- **To:** Account email (self-addressed)
- **Body:** JSON payload with state data
- **Custom flag:** `\\Flagged` or custom IMAP flag for identification

**And** State types persisted:

**Webhook delivery tracking:**
```json
{
  "state_type": "webhook_delivery",
  "webhook_id": "wh_123",
  "message_uid": 12345,
  "delivery_status": "success",
  "attempts": 1,
  "last_attempt": "2025-11-25T10:30:45Z"
}
```

**Sync cursors:**
```json
{
  "state_type": "sync_cursor",
  "account_id": "acc_123",
  "folder": "INBOX",
  "last_uid": 12345,
  "last_sync": "2025-11-25T10:30:45Z"
}
```

**And** State write operations:
- `write_state(state_type, key, data)` - Append state email to IMAP folder
- Uses IMAP APPEND command
- State emails marked with custom flag for efficient retrieval
- Old state entries replaced (delete old, write new)

**And** State flush strategy:
- Periodic flush every 5 minutes (configurable)
- Flush on specific events (webhook delivery, sync completion)
- Flush on graceful shutdown
- Async/non-blocking (doesn't slow down API requests)

**And** Logging:
```
[DEBUG] State persisted type=webhook_delivery key=wh_123
[DEBUG] State flush complete items=5 duration_ms=250
[WARN]  State write failed (IMAP append error)
```

**Prerequisites:** Story 6.1 (state folders created)

**Technical Notes:**
- Use IMAP APPEND to add emails to state folders
- JSON payload in email body (structured, parseable)
- Delete old state entries before writing new ones (avoid duplicates)
- FR-050: State includes markers, webhook status, runtime config
- FR-051: Periodic flush to IMAP
- PRD: IMAP-as-database pattern validation

---

### Story 6.3: State Reconstruction on Startup

As a developer,  
I want Mail Reactor to rebuild state from IMAP on startup,  
So that state persists across restarts without external databases.

**Acceptance Criteria:**

**Given** state persisted to IMAP from Story 6.2  
**When** Mail Reactor starts with `--enable-imap-state`  
**Then** state is reconstructed from IMAP:

**State reconstruction flow:**
1. Connect to IMAP
2. Select `.MailReactor-State` folder
3. Search for state emails (by custom flag or subject pattern)
4. Fetch all state emails
5. Parse JSON payloads
6. Reconstruct in-memory state
7. Continue normal operation

**And** Reconstruction completes within 5 seconds (FR-047):
- Efficient IMAP SEARCH for state emails
- Parallel fetch if many state entries
- Timeout if reconstruction takes too long

**And** State validation during reconstruction:
- Invalid JSON: Skip entry, log warning
- Missing required fields: Skip entry, log warning
- Corrupted state: Detect and fall back to clean slate

**And** Fallback behavior when state reconstruction fails:
- Log error with details
- Start in stateless mode
- Display warning: "State reconstruction failed - starting fresh"
- Don't crash or block startup

**And** Logging:
```
[INFO]  Reconstructing state from IMAP
[INFO]  State reconstruction complete items=42 duration_ms=1234
```

Or:
```
[WARN]  State reconstruction failed (starting in stateless mode)
[ERROR] Invalid state JSON file=state_123.eml error="JSON decode error"
```

**Prerequisites:** Story 6.2 (state written to IMAP)

**Technical Notes:**
- IMAP SEARCH for efficient state email discovery
- Parse JSON with error handling (malformed state shouldn't crash)
- FR-047: Rebuild from IMAP in 5 seconds
- FR-052: Reconstruct from IMAP state emails on restart
- FR-053: Detect corrupted state, fall back to stateless mode
- NFR-R3: State recovery resilience

---

### Story 6.4: IMAP State Experimental Mode Documentation

As a developer,  
I want clear documentation on IMAP-as-database mode's experimental status,  
So that I understand the trade-offs and risks before enabling it.

**Acceptance Criteria:**

**Given** IMAP state persistence implemented  
**When** documenting the feature  
**Then** README includes:

**Experimental Feature Warning:**
```markdown
## ⚠️ IMAP-as-Database (Experimental)

**Status:** EXPERIMENTAL - Not recommended for production use yet

Mail Reactor can optionally persist state to IMAP itself, eliminating 
the need for external databases. This is an innovative pattern that 
stores application state as emails in a hidden IMAP folder.

**Enable:** `mailreactor start --enable-imap-state`

**Trade-offs:**
✅ No external database required
✅ State travels with email account
✅ Works with any IMAP server

⚠️ Slower than Redis/database
⚠️ Not all providers tested
⚠️ User could accidentally delete state
⚠️ Limited write throughput

**When to use:**
- Low-volume installations
- Want stateless-by-default with optional persistence
- Prefer zero dependencies over performance

**When NOT to use:**
- High-volume email processing
- Production deployments (use Production Pack with database instead)
- Untrusted email providers
```

**And** Startup warnings when enabled:
```
[WARN]  IMAP state persistence enabled (EXPERIMENTAL) ⚠
[WARN]  Not recommended for production use
[INFO]  For production, use Production Pack with database
```

**And** Documentation includes:
- How to enable (`--enable-imap-state`)
- How it works (emails in `.MailReactor-State` folder)
- Provider compatibility matrix (Gmail, Outlook, self-hosted)
- Fallback behavior (graceful degradation to stateless)
- Migration path to Production Pack

**Prerequisites:** Stories 6.1-6.3 (feature implemented)

**Technical Notes:**
- Clear about experimental status
- Provide migration path to Production Pack (external DB)
- FR-048 to FR-054: IMAP state management (all experimental)
- PRD: IMAP-as-database validation approach
- PRD: Success criteria for this innovation

---

## Epic 6 Summary (EXPERIMENTAL)

**Stories Completed:** 4  
**FRs Delivered:** 9 (FR-046 to FR-054 - all experimental)  
**User Value:** Developers can optionally enable lightweight state persistence without external databases, but with clear experimental status and fallback behavior.

**What Developers Can Do:**
✅ Enable IMAP state: `mailreactor start --enable-imap-state`  
✅ State persists across restarts (webhook delivery, sync cursors)  
✅ No external database required (Redis, PostgreSQL, etc.)  
✅ Graceful fallback to stateless mode if IMAP state fails  

**⚠️ Experimental Status:**
- Not recommended for production use
- Provider compatibility varies
- Slower than external database
- User could accidentally delete state folder

**When to Use:**
- Experimentation and validation
- Low-volume personal installations
- Zero-dependency preference

**When NOT to Use:**
- Production deployments (use Production Pack with database)
- High-volume email processing
- Mission-critical state persistence

**Production Alternative:**
For production deployments, use Production Pack with:
- SQLite (embedded, fast, reliable)
- PostgreSQL (distributed, scalable)
- Redis (high-performance cache)

---

## FR Coverage Matrix

Complete mapping of all 64 MVP functional requirements to epics and stories:

| FR | Description | Epic | Stories |
|----|-------------|------|---------|
| FR-001 | Auto-detect IMAP/SMTP settings | Epic 2 | 2.1, 2.2 |
| FR-002 | Add account via CLI flag | Epic 2 | 2.7 |
| FR-003 | Add account via REST API | Epic 2 | 2.3 |
| FR-004 | Secure credential storage in memory | Epic 2 | 2.6 |
| FR-005 | Connect to IMAP server | Epic 2 | 2.4 |
| FR-006 | Connect to SMTP server | Epic 2 | 2.4 |
| FR-007 | Manual override of settings | Epic 2 | 2.3, 2.7 |
| FR-008 | Validate credentials with clear errors | Epic 2 | 2.4 |
| FR-009 | Retrieve list of accounts via API | Epic 2 | 2.5 |
| FR-010 | Retrieve specific account details | Epic 2 | 2.5 |
| FR-011 | Send email (to/subject/text) | Epic 3 | 3.2, 3.3 |
| FR-012 | Send email with HTML body | Epic 3 | 3.2, 3.3 |
| FR-013 | Send to multiple recipients | Epic 3 | 3.2, 3.3 |
| FR-014 | Send with attachments | Epic 3 | 3.2, 3.3 |
| FR-015 | Send via SMTP | Epic 3 | 3.1, 3.3 |
| FR-016 | Return message ID and status | Epic 3 | 3.2, 3.3 |
| FR-017 | Handle SMTP errors gracefully | Epic 3 | 3.1, 3.4 |
| FR-018 | Support custom headers | Epic 3 | 3.2, 3.3 |
| FR-019 | Query emails with IMAP search | Epic 4 | 4.1, 4.3 |
| FR-020 | Support IMAP search criteria | Epic 4 | 4.1, 4.3 |
| FR-021 | Return structured JSON | Epic 4 | 4.2, 4.3, 4.4 |
| FR-022 | Retrieve full email details | Epic 4 | 4.2, 4.4 |
| FR-023 | Cursor-based pagination | Epic 4 | 4.3 (limit-based in MVP) |
| FR-024 | Server-side filtering | Epic 4 | 4.1, 4.3 |
| FR-025 | In-memory caching | Epic 4 | 4.6 |
| FR-026 | Configure time window | Epic 4 | 4.7 |
| FR-027 | Health check endpoint | Epic 1 | 1.5 |
| FR-028 | Log startup sequence | Epic 1 | 1.3, 1.4 |
| FR-029 | Log connection status | Epic 1 | 1.3, Epic 2 |
| FR-030 | Log API requests/responses | Epic 1 | 1.3 |
| FR-031 | Clear error messages | Epic 1 | 1.7, All epics |
| FR-032 | Install via PyPI/pipx | Epic 1 | 1.1 |
| FR-033 | Zero external dependencies | Epic 1 | 1.1 |
| FR-034 | Single command startup | Epic 1 | 1.4, Epic 2.7 |
| FR-035 | Start within 3 seconds | Epic 1 | 1.4 |
| FR-036 | Bind to localhost by default | Epic 1 | 1.4 |
| FR-037 | Configure host/port via CLI | Epic 1 | 1.4 |
| FR-038 | Display startup message | Epic 1 | 1.4 |
| FR-039 | No auth in MVP (localhost) | Epic 1 | 1.4 |
| FR-040 | Warn when auth disabled | Epic 1, 5 | 5.1, 5.3 |
| FR-041 | Enable API key via CLI | Epic 5 | 5.1 |
| FR-042 | Auto-generate API key | Epic 5 | 5.1 |
| FR-043 | Require bearer token when enabled | Epic 5 | 5.2 |
| FR-044 | Return 401 for invalid auth | Epic 5 | 5.2 |
| FR-045 | Store API keys securely | Epic 5 | 5.1 |
| FR-046 | Stateless by default | Epic 1, 2 | 2.6 |
| FR-047 | Rebuild from IMAP in 5s | Epic 6 | 6.3 |
| FR-048 | Optional IMAP-as-database mode | Epic 6 | 6.1 |
| FR-049 | Write state to IMAP folder | Epic 6 | 6.1, 6.2 |
| FR-050 | State includes markers, webhooks | Epic 6 | 6.2 |
| FR-051 | Periodic flush to IMAP | Epic 6 | 6.2 |
| FR-052 | Reconstruct from IMAP on restart | Epic 6 | 6.3 |
| FR-053 | Detect corrupted state, fallback | Epic 6 | 6.3 |
| FR-054 | Alert on state deletion | Epic 6 | 6.3 |
| FR-055 | JSON content type | Epic 1 | 1.7 |
| FR-056 | Consistent envelope format | Epic 1 | 1.7 |
| FR-057 | Standard HTTP codes | Epic 1 | 1.7 |
| FR-058 | Error responses with details | Epic 1 | 1.7 |
| FR-059 | ISO 8601 timestamps | Epic 1 | 1.7 |
| FR-060 | Auto-generate OpenAPI spec | Epic 1 | 1.6 |
| FR-061 | Swagger UI at /docs | Epic 1 | 1.6 |
| FR-062 | ReDoc at /redoc | Epic 1 | 1.6 |

**Total Coverage:** 64 FRs across 6 epics, 38 stories

---

## Summary

**Mail Reactor MVP - Complete Epic Breakdown**

### Epic Overview
1. **Epic 1: Foundation** (8 stories, 24 FRs) - Installable API service with beautiful console logs
2. **Epic 2: Account Connection** (8 stories, 10 FRs) - Auto-detection with Mozilla Autoconfig fallback
3. **Epic 3: Email Sending** (5 stories, 8 FRs) - Send emails via REST API
4. **Epic 4: Email Retrieval** (7 stories, 8 FRs) - Search and retrieve emails via REST API
5. **Epic 5: Security** (3 stories, 5 FRs) - Production-ready API key authentication
6. **Epic 6: IMAP State** (4 stories, 9 FRs) - Experimental state persistence

**Total:** 6 epics, 38 stories, 64 functional requirements

### What Developers Can Do After MVP

**Install and Start:**
```bash
pipx install mailreactor
mailreactor start --account you@gmail.com
```

**Send Email:**
```bash
curl -X POST http://localhost:8000/accounts/acc_123/send \
  -H "Content-Type: application/json" \
  -d '{"to": [{"email": "user@example.com"}], "subject": "Hello", "body_text": "World"}'
```

**Search Emails:**
```bash
curl "http://localhost:8000/accounts/acc_123/messages?search=UNSEEN+FROM+support@company.com"
```

**Production Deployment:**
```bash
mailreactor start \
  --account you@gmail.com \
  --api-key-auto \
  --host 0.0.0.0 \
  --port 8000
```

### Key Differentiators Delivered

✅ **Zero-config startup** - Works in seconds, not hours  
✅ **Beautiful console logs** - Color-coded, clean, minimal emoji  
✅ **Auto-detection** - Gmail, Outlook, Yahoo, + 1000s via Mozilla Autoconfig  
✅ **Stateless by default** - No database required  
✅ **Production-ready auth** - API key authentication with bcrypt  
✅ **Developer-first** - Interactive docs, clear errors, great DX  

**This is the epic breakdown that delivers the PRD promise: "Email integration in 5 minutes, not 5 weeks."**

---

_For implementation: Use `/bmad:bmm:workflows:sprint-planning` to create sprint plan and begin Phase 4 Implementation._

