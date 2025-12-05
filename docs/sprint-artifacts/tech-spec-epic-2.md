# Epic Technical Specification: Email Account Connection

Date: 2025-12-04
Author: HC
Epic ID: 2
Status: Draft

---

## Overview

Epic 2 enables developers to connect their email accounts to Mail Reactor with minimal friction through intelligent auto-detection of IMAP/SMTP settings. The epic implements a multi-tier auto-detection cascade (local providers → Mozilla Autoconfig → ISP fallback → manual configuration) that covers thousands of email providers while maintaining the zero-configuration philosophy critical to Mail Reactor's developer experience.

This epic delivers the foundation for all email operations by establishing secure, validated connections to email accounts. It implements stateless in-memory account management aligned with the NFR-P1 (3-second startup) requirement and NFR-S1 (memory-only credential storage) security constraint.

## Objectives and Scope

**In Scope:**
- Auto-detection for major providers (Gmail, Outlook, Yahoo, iCloud) via local YAML configuration
- Mozilla Thunderbird Autoconfig database integration for broader provider coverage (1000+ providers)
- ISP-hosted autoconfig fallback for provider-specific configurations
- Manual IMAP/SMTP configuration override via CLI flags and REST API
- Connection validation with immediate feedback and clear error messages
- Account management REST API (add, list, retrieve, remove accounts)
- In-memory StateManager with thread-safe asyncio operations
- CLI integration with `--account` flag for zero-config startup
- Provider-specific error guidance (Gmail App Passwords, Outlook 2FA hints)

**Out of Scope (Future Phases):**
- OAuth2 authentication (Phase 2 - Epic TBD)
- Multi-account concurrent management (Phase 2)
- Persistent state storage (Phase 2 - Epic 6: IMAP-as-database)
- Connection pooling and keep-alive (Phase 2 optimization)
- Account-level permission scopes (Future)

## System Architecture Alignment

**Core Components:**
- `core/provider_detector.py` - Auto-detection engine with Mozilla Autoconfig integration
- `core/state_manager.py` - Enhanced with account CRUD operations and asyncio locks
- `api/accounts.py` - REST API for account management (POST, GET, DELETE)
- `models/account.py` - Pydantic models for ProviderConfig, AccountCredentials, AccountConfig
- `cli/server.py` - Extended with `--account` flag and manual override flags
- `utils/providers.yaml` - Local provider configurations (Gmail, Outlook, Yahoo, iCloud)

**Integration Points:**
- **FastAPI:** Account management endpoints integrated into main app router
- **IMAPClient:** Connection validation via sync client wrapped with asyncio executor
- **aiosmtplib:** SMTP connection validation (native async)
- **httpx:** Async HTTP client for Mozilla Autoconfig queries
- **structlog:** Structured logging for connection events and auto-detection flow
- **Typer:** CLI flag handling for account configuration during startup

**Architectural Constraints:**
- Stateless design: All account state in-memory, lost on restart (by design)
- Thread-safe: Asyncio locks protect StateManager account dictionary
- Security: Passwords marked with `exclude=True` in Pydantic, never logged
- Performance: Auto-detection cached (24h success, 1h failure), 5s network timeout
- Error handling: Custom exceptions (IMAPConnectionError, SMTPConnectionError) with provider-specific hints

---

## Detailed Design

### Services and Modules

| Module | Responsibility | Key Methods | Dependencies |
|--------|---------------|-------------|--------------|
| `provider_detector.py` | Auto-detect IMAP/SMTP settings | `detect_provider(email)`, `detect_via_mozilla_autoconfig(domain)` | httpx, xml.etree.ElementTree, PyYAML |
| `state_manager.py` | Thread-safe in-memory account storage | `add_account()`, `get_account()`, `get_all_accounts()`, `remove_account()` | asyncio.Lock |
| `accounts.py` (API) | REST endpoints for account management | POST `/accounts`, GET `/accounts`, GET `/accounts/{id}`, DELETE `/accounts/{id}` | FastAPI, state_manager, provider_detector |
| `server.py` (CLI) | CLI account configuration on startup | Enhanced `start()` with `--account`, `--imap-host`, etc. flags | Typer, getpass, state_manager |
| `account.py` (models) | Pydantic data models | ProviderConfig, AccountCredentials, AccountConfig, AddAccountRequest, AccountResponse | Pydantic, EmailStr |

**Module Interactions:**
```
CLI (--account flag) or REST API (POST /accounts)
    ↓
provider_detector.detect_provider(email)
    ↓ (local providers.yaml → Mozilla Autoconfig → ISP fallback)
ProviderConfig returned (or None)
    ↓
Merge with manual overrides (if provided)
    ↓
Validate connection (IMAPClient + aiosmtplib)
    ↓
state_manager.add_account(account_id, credentials)
    ↓
Return account_id to caller (API response or CLI confirmation)
```

### Data Models and Contracts

**ProviderConfig (Pydantic Model):**
```python
class ProviderConfig(BaseModel):
    """Auto-detected IMAP/SMTP configuration for a provider"""
    provider_name: str  # "gmail", "outlook", "yahoo", etc.
    imap_host: str
    imap_port: int = 993
    imap_ssl: bool = True
    smtp_host: str
    smtp_port: int = 587
    smtp_starttls: bool = True
```

**AccountCredentials (Pydantic Model):**
```python
class AccountCredentials(BaseModel):
    """Account credentials stored in memory"""
    account_id: str  # Generated: acc_{uuid4().hex[:8]}
    email: EmailStr
    password: str = Field(..., exclude=True)  # Never serialized
    imap_host: str
    imap_port: int = 993
    imap_ssl: bool = True
    smtp_host: str
    smtp_port: int = 587
    smtp_starttls: bool = True
    created_at: datetime
    connection_status: str = "pending"  # pending, connected, error
```

**AddAccountRequest (API Request Model):**
```python
class AddAccountRequest(BaseModel):
    """Request to add a new account"""
    email: EmailStr
    password: str
    # Optional manual overrides
    imap_host: str | None = None
    imap_port: int | None = None
    imap_ssl: bool | None = None
    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_starttls: bool | None = None
```

**AccountResponse (API Response Model):**
```python
class AccountResponse(BaseModel):
    """Response after adding or retrieving account"""
    account_id: str
    email: str
    connection_status: str
    imap_host: str
    smtp_host: str
    created_at: datetime
    # Password excluded (security)
```

**AccountSummary (List Response Model):**
```python
class AccountSummary(BaseModel):
    """Summary for account listing"""
    account_id: str
    email: str
    connection_status: str
    created_at: datetime
```

**StateManager Account Storage:**
```python
# In-memory structure (not persisted)
{
    "acc_a1b2c3d4": AccountCredentials(...),
    "acc_e5f6g7h8": AccountCredentials(...),
}
# Protected by asyncio.Lock for thread-safety
```

### APIs and Interfaces

**REST API Endpoints:**

**1. POST /accounts - Add Email Account**

Request:
```json
{
  "email": "user@gmail.com",
  "password": "app-password-here",
  "imap_host": "imap.gmail.com",  // Optional override
  "smtp_host": "smtp.gmail.com"   // Optional override
}
```

Response (201 Created):
```json
{
  "data": {
    "account_id": "acc_a1b2c3d4",
    "email": "user@gmail.com",
    "connection_status": "connected",
    "imap_host": "imap.gmail.com",
    "smtp_host": "smtp.gmail.com",
    "created_at": "2025-12-04T10:30:45Z"
  },
  "meta": {
    "request_id": "req_xyz123",
    "timestamp": "2025-12-04T10:30:46Z"
  }
}
```

Error (503 Service Unavailable - Connection Failed):
```json
{
  "error": {
    "code": "IMAP_CONNECTION_FAILED",
    "message": "Unable to connect to IMAP server imap.gmail.com:993",
    "details": {
      "hint": "Check hostname and port. Verify firewall allows outbound connections on port 993."
    }
  },
  "meta": {
    "request_id": "req_xyz124",
    "timestamp": "2025-12-04T10:30:47Z"
  }
}
```

**2. GET /accounts - List All Accounts**

Response (200 OK):
```json
{
  "data": [
    {
      "account_id": "acc_a1b2c3d4",
      "email": "user@gmail.com",
      "connection_status": "connected",
      "created_at": "2025-12-04T10:30:45Z"
    }
  ],
  "meta": {
    "request_id": "req_xyz125",
    "timestamp": "2025-12-04T10:31:00Z"
  }
}
```

**3. GET /accounts/{account_id} - Get Account Details**

Response (200 OK):
```json
{
  "data": {
    "account_id": "acc_a1b2c3d4",
    "email": "user@gmail.com",
    "connection_status": "connected",
    "imap_host": "imap.gmail.com",
    "imap_port": 993,
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "created_at": "2025-12-04T10:30:45Z"
  },
  "meta": {
    "request_id": "req_xyz126",
    "timestamp": "2025-12-04T10:31:05Z"
  }
}
```

Error (404 Not Found):
```json
{
  "error": {
    "code": "ACCOUNT_NOT_FOUND",
    "message": "Account acc_invalid not found"
  },
  "meta": {
    "request_id": "req_xyz127",
    "timestamp": "2025-12-04T10:31:10Z"
  }
}
```

**4. DELETE /accounts/{account_id} - Remove Account**

Response (204 No Content)
- Empty body, successful deletion indicated by status code

Error (404 Not Found):
```json
{
  "error": {
    "code": "ACCOUNT_NOT_FOUND",
    "message": "Account acc_invalid not found"
  },
  "meta": {
    "request_id": "req_xyz128",
    "timestamp": "2025-12-04T10:31:15Z"
  }
}
```

**CLI Interface:**

```bash
# Auto-detect Gmail (zero-config)
mailreactor start --account you@gmail.com
# Prompts: "Password: " (hidden input)
# Output: "[INFO] Provider detected provider=Gmail"
# Output: "[INFO] Account connected ✓ email=you@gmail.com"

# Manual override for custom server
mailreactor start --account you@custom.com \
  --imap-host imap.custom.com \
  --smtp-host smtp.custom.com
# Prompts: "Password: "
# Output: "[INFO] Using manual configuration"
# Output: "[INFO] Account connected ✓ email=you@custom.com"

# Start without account (configure later via API)
mailreactor start
# Output: "[INFO] No account configured (add with --account or POST /accounts)"
```

### Workflows and Sequencing

**Account Addition Flow (Detailed):**

```
1. User invokes: CLI (--account flag) OR API (POST /accounts)
   ↓
2. Parse email address, extract domain
   ↓
3. Auto-Detection Cascade:
   a) Check local providers.yaml
      - Match: gmail.com → Gmail config
      - Match: outlook.com/hotmail.com → Outlook config
      - Match: yahoo.com → Yahoo config
      - Match: icloud.com/me.com → iCloud config
      - No match → Continue to (b)
   ↓
   b) Mozilla Autoconfig Lookup (async HTTP)
      - Query: https://autoconfig.thunderbird.net/v1.1/{domain}
      - Parse XML: <incomingServer type="imap">, <outgoingServer type="smtp">
      - Success → Return ProviderConfig
      - Failure/Timeout → Continue to (c)
   ↓
   c) ISP-Hosted Autoconfig (async HTTP)
      - Query: http://autoconfig.{domain}/mail/config-v1.1.xml
      - Parse XML if found
      - Success → Return ProviderConfig
      - Failure → Continue to (d)
   ↓
   d) Manual Configuration Required
      - Return None from auto-detection
      - If manual overrides provided → Use them
      - If no manual overrides → Return 400 error with guidance
   ↓
4. Merge Configuration:
   - Start with auto-detected config (if found)
   - Apply manual overrides (if provided)
   - Result: Complete IMAP/SMTP configuration
   ↓
5. Connection Validation (Parallel):
   a) IMAP Connection Test (asyncio executor)
      - Connect to imap_host:imap_port with SSL
      - Attempt login(email, password)
      - Timeout: 10 seconds
      - Success: Continue
      - Failure: Raise IMAPConnectionError or IMAPAuthenticationError
   ↓
   b) SMTP Connection Test (async)
      - Connect to smtp_host:smtp_port with STARTTLS
      - Attempt authenticate(email, password)
      - Timeout: 10 seconds
      - Success: Continue
      - Failure: Raise SMTPConnectionError or SMTPAuthenticationError
   ↓
6. Store Account (if validation succeeded):
   - Generate account_id: acc_{uuid4().hex[:8]}
   - Create AccountCredentials instance
   - state_manager.add_account(account_id, credentials)
   - Set connection_status = "connected"
   ↓
7. Return Success Response:
   - API: HTTP 201 Created with AccountResponse
   - CLI: Console output "✓ Account connected"
   ↓
8. Logging:
   - INFO: Account {account_id} connected successfully
   - Bind context: account_id, email, provider
```

**Error Path - Auto-Detection Failed:**
```
Auto-detection returns None (domain not in providers.yaml, Mozilla failed, ISP failed)
   ↓
Check if manual overrides provided
   ↓
IF manual overrides present:
   - Use manual config
   - Proceed to connection validation
ELSE:
   - Return HTTP 400 Bad Request
   - Message: "Unable to auto-detect settings for {domain}"
   - Hint: "Please provide imap_host and smtp_host manually"
   - Example: Include curl command with manual flags
   ↓
User retries with manual configuration
```

**Error Path - Connection Validation Failed:**
```
IMAP or SMTP connection test fails
   ↓
Determine error type:
   - Network timeout → "Connection timeout after 10s"
   - Connection refused → "Unable to connect to server {host}:{port}"
   - Authentication failed → "Authentication failed. Check credentials."
   - SSL certificate error → "SSL certificate verification failed"
   ↓
Add provider-specific hints:
   - Gmail: "For Gmail with 2FA, use App Password: https://support.google.com/accounts/answer/185833"
   - Outlook: "For Outlook with 2FA, use App Password or enable OAuth2"
   - Generic: "Verify credentials and check firewall/network settings"
   ↓
Return HTTP 503 Service Unavailable with error details
   ↓
Log: ERROR "Account connection failed" with full context
   ↓
User investigates error, corrects issue, retries
```

---

## Non-Functional Requirements

### Performance

**NFR-P1: Startup Time**
- Account validation must complete within 5 seconds (IMAP 10s + SMTP 10s with parallel execution)
- Total startup time (with account) under 5 seconds remains achievable with async validation
- Strategy: Run IMAP and SMTP validation concurrently using `asyncio.gather()`

**NFR-P2: Auto-Detection Latency**
- Local providers.yaml lookup: <1ms (in-memory dict lookup)
- Mozilla Autoconfig query: <5s (HTTP timeout enforced)
- ISP autoconfig query: <5s (HTTP timeout enforced)
- Cache hit: <1ms (in-memory cache lookup)
- Total auto-detection (worst case): <15s (cascade, but typically <1s for common providers)

**NFR-P4: Memory Footprint**
- AccountCredentials per account: ~500 bytes (email, hosts, ports, timestamp)
- Mozilla Autoconfig cache: ~10KB for 100 domains cached
- StateManager overhead: <1MB for 100 accounts
- Target: 100MB RAM for single account remains achievable

**NFR-P6: Connection Stability**
- Connection validation timeout: 10s per service (IMAP, SMTP)
- Retry strategy: None in MVP (fail fast, user retries)
- Connection pool: Deferred to Phase 2 (out of scope for Epic 2)

### Security

**NFR-S1: Credential Storage**
- ✅ Passwords stored in memory only (AccountCredentials in StateManager dict)
- ✅ Never written to disk (stateless architecture)
- ✅ Pydantic `exclude=True` on password field prevents serialization
- ✅ Never logged (structlog filters sensitive fields)
- ⚠️ Vulnerability: Memory dump could expose passwords (acceptable for MVP, self-hosted)

**NFR-S2: API Key Security**
- Not applicable to Epic 2 (API key authentication is Epic 5)
- Account endpoints do NOT require authentication in MVP (localhost-only assumption)

**NFR-S3: Network Security**
- ✅ IMAP connections use SSL by default (port 993)
- ✅ SMTP connections use STARTTLS by default (port 587)
- ✅ TLS certificate verification enabled (can be disabled per-account if needed)
- ⚠️ Mozilla Autoconfig queries over HTTP (Mozilla's database, no sensitive data transmitted)

**NFR-S4: Dependency Security**
- httpx: MIT licensed, maintained, used for Mozilla Autoconfig queries
- IMAPClient: BSD-3 licensed, production-stable
- aiosmtplib: MIT licensed, actively maintained
- PyYAML: MIT licensed, for providers.yaml parsing
- All dependencies vetted in ADR decisions

**NFR-S5: Data Privacy**
- ✅ No telemetry in MVP
- ✅ Passwords never leave localhost (IMAP/SMTP connection goes directly to email servers)
- ✅ Mozilla Autoconfig query only sends domain (no email address, no credentials)

### Reliability/Availability

**NFR-R1: Connection Resilience**
- Auto-detection failures gracefully fall back to manual configuration
- Connection validation failures provide clear error messages with remediation hints
- Network timeouts (5s for auto-detection, 10s for validation) prevent indefinite hangs
- Provider-specific error guidance (Gmail App Passwords, Outlook 2FA hints)

**NFR-R2: Error Handling**
- ✅ IMAPConnectionError, IMAPAuthenticationError with context (host, port, email)
- ✅ SMTPConnectionError, SMTPAuthenticationError with context
- ✅ Validation errors before storing account (fail fast)
- ✅ HTTP 400 for invalid input, 503 for connection failures, 404 for not found

**NFR-R3: State Recovery**
- Not applicable (stateless design - state lost on restart by design)
- Accounts must be re-added on restart (acceptable for MVP)

**NFR-R4: Graceful Degradation**
- Mozilla Autoconfig failure → fall back to ISP autoconfig
- ISP autoconfig failure → fall back to manual configuration
- Connection validation failure → clear error, don't store account

### Observability

**NFR-O1: Logging**
- ✅ Structured logging with structlog (JSON-capable)
- Log events:
  - INFO: Account addition started (email, domain)
  - INFO: Auto-detection result (provider detected or failed)
  - INFO: Connection validation started (IMAP, SMTP)
  - INFO: Account connected successfully (account_id, email)
  - ERROR: Connection validation failed (error type, host, port, hint)
- Context binding: account_id, email, provider, domain
- Sensitive data filtering: passwords never logged

---

## Dependencies and Integrations

### External Dependencies

| Dependency | Version | License | Purpose | Justification |
|-----------|---------|---------|---------|---------------|
| FastAPI | 0.122.0 | MIT | REST API framework | Auto OpenAPI docs, async support, Pydantic integration (ADR-001) |
| IMAPClient | 3.0.1 | BSD-3 | IMAP connection validation | Production-stable, BSD-3 compatible with MIT (ADR-002) |
| aiosmtplib | 5.0.0 | MIT | SMTP connection validation | Native async, MIT licensed, production-ready |
| httpx | latest | BSD-3 | Mozilla Autoconfig HTTP queries | Async HTTP client, FastAPI ecosystem standard |
| PyYAML | latest | MIT | Parse providers.yaml | Standard YAML library, human-readable configs |
| Pydantic | v2 | MIT | Data validation | Bundled with FastAPI, type-safe models |
| structlog | latest | MIT | Structured logging | Production-ready, async-safe (ADR-006) |
| Typer | 0.20.0 | MIT | CLI framework | FastAPI sibling, intuitive DX (ADR-005) |

**Dependency Version Constraints:**
```toml
# pyproject.toml
[project.dependencies]
fastapi = "^0.122.0"
imapclient = "^3.0.1"
aiosmtplib = "^5.0.0"
httpx = "^0.27.0"
pyyaml = "^6.0.1"
pydantic = "^2.0"
structlog = "^24.0"
typer = "^0.20.0"
```

### Integration Points

**StateManager Integration:**
- Epic 1 created basic StateManager (FR-027: health check access to uptime)
- Epic 2 enhances with account CRUD methods
- Interface:
  ```python
  async def add_account(account_id: str, credentials: AccountCredentials)
  async def get_account(account_id: str) -> Optional[AccountCredentials]
  async def get_all_accounts() -> List[AccountCredentials]
  async def remove_account(account_id: str) -> None
  ```
- Thread-safety: asyncio.Lock protects account dictionary

**CLI Integration:**
- Epic 1 created `mailreactor start` command
- Epic 2 adds CLI flags: `--account`, `--imap-host`, `--smtp-host`, etc.
- Password input via `getpass.getpass()` (no echo to terminal)
- Interactive validation feedback with console output and spinners (via `rich`)

**API Router Integration:**
- New router: `accounts_router = APIRouter(prefix="/accounts", tags=["accounts"])`
- Registered in `main.py`: `app.include_router(accounts_router)`
- Follows Epic 1 patterns: response envelopes, error handling, request ID middleware

**Mozilla Autoconfig External Service:**
- URL: `https://autoconfig.thunderbird.net/v1.1/{domain}`
- Format: XML (parsed with xml.etree.ElementTree)
- Rate limiting: None enforced by Mozilla (use responsibly)
- Fallback: ISP autoconfig at `http://autoconfig.{domain}/mail/config-v1.1.xml`
- Caching: In-memory cache (24h TTL for success, 1h for failure)

---

## Acceptance Criteria (Authoritative)

**AC-2.1: Local Provider Auto-Detection**
1. Given an email address with a known domain (gmail.com, outlook.com, yahoo.com, icloud.com)
2. When `detect_provider(email)` is called
3. Then IMAP/SMTP settings are returned from providers.yaml within <1ms
4. And no network calls are made (offline-first)

**AC-2.2: Mozilla Autoconfig Fallback**
1. Given an email address with an unknown domain (not in providers.yaml)
2. When `detect_provider(email)` is called
3. Then Mozilla Autoconfig is queried via HTTPS
4. And XML response is parsed to extract IMAP/SMTP settings
5. And result is cached for 24 hours (success) or 1 hour (failure)

**AC-2.3: Manual Configuration Override**
1. Given auto-detection succeeds with settings
2. When user provides manual override flags (--imap-host, --smtp-host)
3. Then manual values replace auto-detected values
4. And connection validation uses merged configuration

**AC-2.4: Connection Validation**
1. Given IMAP/SMTP settings (auto-detected or manual)
2. When account is added (API or CLI)
3. Then IMAP connection is attempted with SSL
4. And IMAP authentication is validated (login with email/password)
5. And SMTP connection is attempted with STARTTLS
6. And SMTP authentication is validated
7. And account is stored only if both validations succeed
8. And connection failures return HTTP 503 with clear error message

**AC-2.5: Account REST API**
1. Given no accounts exist
2. When `POST /accounts` is called with valid credentials
3. Then account is added to StateManager
4. And HTTP 201 Created is returned with account_id
5. And `GET /accounts` returns list containing the new account
6. And `GET /accounts/{account_id}` returns account details (no password)
7. And `DELETE /accounts/{account_id}` removes the account and returns HTTP 204

**AC-2.6: CLI Account Configuration**
1. Given `mailreactor start --account you@gmail.com` is invoked
2. When password is entered (interactive prompt)
3. Then auto-detection identifies Gmail provider
4. And IMAP/SMTP connections are validated
5. And account is stored in StateManager
6. And server starts with account pre-configured
7. And console displays "[INFO] Account connected ✓ email=you@gmail.com"

**AC-2.7: Error Handling and User Guidance**
1. Given auto-detection fails (unknown domain, no manual config)
2. When account addition is attempted
3. Then HTTP 400 is returned with error message
4. And error includes hint: "Please provide imap_host and smtp_host manually"
5. And error includes example curl command with manual flags

**AC-2.8: Provider-Specific Hints**
1. Given IMAP authentication fails for gmail.com domain
2. When error response is generated
3. Then hint includes: "For Gmail with 2FA, use App Password"
4. And hint includes link to Google App Passwords setup page

**AC-2.9: Security - Password Exclusion**
1. Given account is stored in StateManager
2. When `GET /accounts/{account_id}` is called
3. Then response includes email, imap_host, smtp_host
4. And response does NOT include password field
5. And password is never logged in application logs

**AC-2.10: Stateless Operation**
1. Given account is added during runtime
2. When server is restarted
3. Then account is lost from StateManager (stateless design)
4. And account must be re-added (via API or CLI flag)

---

## Traceability Mapping

| Acceptance Criteria | Spec Section | Component | Test Strategy |
|---------------------|--------------|-----------|---------------|
| AC-2.1: Local provider auto-detection | Data Models, Workflows | `provider_detector.py`, `providers.yaml` | Unit test: mock providers.yaml, assert config returned |
| AC-2.2: Mozilla Autoconfig fallback | Workflows, Dependencies | `provider_detector.py`, httpx | Integration test: mock httpx response, verify XML parsing |
| AC-2.3: Manual override | APIs, Workflows | `accounts.py`, `server.py` CLI | Unit test: merge auto-detected + manual, assert override |
| AC-2.4: Connection validation | Workflows, NFR-R1 | IMAPClient, aiosmtplib | Integration test: mock IMAP/SMTP servers, test validation |
| AC-2.5: Account REST API | APIs, Data Models | `accounts.py`, `state_manager.py` | API test: TestClient, verify CRUD operations |
| AC-2.6: CLI account configuration | APIs (CLI), Workflows | `server.py`, `state_manager.py` | Integration test: invoke CLI, mock getpass, verify account stored |
| AC-2.7: Error handling | NFR-R2, Workflows | `accounts.py`, exception handlers | Unit test: trigger error paths, assert error messages |
| AC-2.8: Provider-specific hints | NFR-R2, Workflows | Error handling logic | Unit test: trigger Gmail auth failure, assert hint present |
| AC-2.9: Password exclusion | NFR-S1, Data Models | Pydantic `exclude=True` | Unit test: serialize AccountCredentials, assert password absent |
| AC-2.10: Stateless operation | System Arch, NFR-R3 | `state_manager.py` | Integration test: add account, restart StateManager, assert empty |

**FR Coverage:**
- FR-001: AC-2.1, AC-2.2 (auto-detection)
- FR-002: AC-2.6 (CLI with --account flag)
- FR-003: AC-2.5 (POST /accounts API)
- FR-004: AC-2.9, AC-2.10 (in-memory storage, security)
- FR-005: AC-2.4 (IMAP connection validation)
- FR-006: AC-2.4 (SMTP connection validation)
- FR-007: AC-2.3 (manual override)
- FR-008: AC-2.4, AC-2.7, AC-2.8 (validation with clear errors)
- FR-009: AC-2.5 (GET /accounts list)
- FR-010: AC-2.5 (GET /accounts/{id} details)

---

## Risks, Assumptions, Open Questions

### Risks

**R1: Mozilla Autoconfig Availability**
- Risk: Mozilla's autoconfig service could be unavailable or slow
- Probability: Low (stable service, used by Thunderbird)
- Impact: Medium (fallback to ISP autoconfig or manual config)
- Mitigation: 5-second timeout, in-memory caching (24h), ISP fallback

**R2: Provider Configuration Accuracy**
- Risk: Hardcoded providers.yaml settings could become outdated
- Probability: Medium (providers occasionally change servers)
- Impact: Medium (connection validation would fail, user must manual override)
- Mitigation: Document provider configs, accept community PRs for updates, Mozilla fallback

**R3: Memory-Only State Loss**
- Risk: Server restart loses all accounts (by design, but user frustration)
- Probability: High (restarts are common)
- Impact: Low (MVP assumption, documented behavior, CLI flag makes re-add easy)
- Mitigation: Clear documentation, CLI `--account` flag for quick re-add, Phase 2: IMAP-as-database

**R4: Connection Validation False Positives**
- Risk: Connection succeeds but subsequent operations fail (rate limiting, quota)
- Probability: Low (validation is basic connect+auth, not full operation test)
- Impact: Medium (user gets false confidence, later operations fail)
- Mitigation: Log warnings, document limitations, Epic 3/4 will test actual operations

**R5: Provider-Specific Quirks**
- Risk: Some providers have non-standard IMAP/SMTP behavior
- Probability: Medium (Office365 throttling, Gmail special labels)
- Impact: Low (handled in Epic 3/4, not Epic 2 concern)
- Mitigation: Test with major providers (Gmail, Outlook, Yahoo), document known issues

### Assumptions

**A1: Localhost Deployment (MVP)**
- Assumption: Mail Reactor runs on localhost (127.0.0.1) or trusted network
- Justification: MVP scope, no authentication required
- Impact: Account endpoints have no auth (deferred to Epic 5)

**A2: Single Account Primary Use Case**
- Assumption: Most MVP users will configure one account
- Justification: Multi-account is Phase 2 feature
- Impact: StateManager supports multiple accounts, but UX optimized for single

**A3: App Passwords for 2FA Providers**
- Assumption: Users with Gmail/Outlook 2FA will use App Passwords (not OAuth2)
- Justification: OAuth2 is Phase 2 (Epic TBD)
- Impact: Error messages guide users to App Password setup

**A4: Network Connectivity**
- Assumption: Server has outbound internet access for Mozilla Autoconfig queries
- Justification: Self-hosted deployment typically has internet
- Impact: Auto-detection fails gracefully if offline (use manual config)

**A5: English Error Messages**
- Assumption: Error messages in English (MVP)
- Justification: International support is Phase 2+
- Impact: Non-English users may need translation (future i18n)

### Open Questions

**Q1: Mozilla Autoconfig Rate Limiting**
- Question: Does Mozilla enforce rate limits on autoconfig queries?
- Status: Unknown (not documented publicly)
- Action: Implement caching (24h TTL) to minimize queries, monitor in production

**Q2: Certificate Verification Override**
- Question: Should we allow disabling SSL certificate verification for self-hosted servers?
- Status: Deferred to story implementation
- Action: Add `imap_ssl_verify` and `smtp_ssl_verify` optional flags if needed

**Q3: Connection Keep-Alive**
- Question: Should validated connections be kept alive or closed immediately?
- Status: Deferred to Phase 2 (connection pooling)
- Action: MVP closes connections after validation (simpler, stateless)

**Q4: Account ID Collision**
- Question: What's the probability of account_id collision (8-char hex UUID)?
- Status: Low risk (256^8 possibilities, MVP single-user)
- Action: Monitor in production, extend to 16-char if needed in Phase 2

**Q5: ISP Autoconfig HTTP (not HTTPS)**
- Question: Is it secure to query ISP autoconfig over HTTP?
- Status: Acceptable (no sensitive data transmitted, only domain)
- Action: Document in security notes, consider HTTPS fallback if ISP supports

---

## Test Strategy Summary

### Unit Tests (Story-Level)

**provider_detector.py:**
- Test local providers.yaml lookup (gmail, outlook, yahoo, icloud)
- Test domain extraction (gmail.com, outlook.com, custom domains)
- Test Mozilla Autoconfig XML parsing (mock httpx response)
- Test cache hit/miss logic (in-memory cache)
- Test error handling (network timeout, invalid XML)

**state_manager.py:**
- Test add_account (generates account_id, stores credentials)
- Test get_account (retrieves by account_id)
- Test get_all_accounts (returns list)
- Test remove_account (deletes from dict)
- Test thread-safety (asyncio.Lock prevents race conditions)

**accounts.py (API):**
- Test POST /accounts (success: auto-detected config)
- Test POST /accounts (success: manual config)
- Test POST /accounts (failure: no config found, no manual override)
- Test POST /accounts (failure: connection validation failed)
- Test GET /accounts (list accounts)
- Test GET /accounts/{id} (retrieve details, password excluded)
- Test DELETE /accounts/{id} (remove account)
- Test error responses (400, 404, 503)

**server.py (CLI):**
- Test --account flag parsing
- Test auto-detection invoked from CLI
- Test manual override flags (--imap-host, --smtp-host)
- Test getpass integration (mock password input)
- Test console output (success, failure messages)

### Integration Tests (Epic-Level)

**End-to-End Account Addition (API):**
1. POST /accounts with gmail.com (auto-detect)
2. Verify account stored in StateManager
3. GET /accounts returns account
4. GET /accounts/{id} returns details (no password)
5. DELETE /accounts/{id} removes account
6. GET /accounts returns empty list

**End-to-End Account Addition (CLI):**
1. Invoke `mailreactor start --account test@gmail.com`
2. Mock password input (getpass)
3. Mock IMAP/SMTP connection (success)
4. Verify account in StateManager
5. Verify server starts successfully

**Mozilla Autoconfig Integration:**
1. Mock httpx to return valid XML
2. Call detect_provider with unknown domain
3. Verify XML parsed correctly
4. Verify ProviderConfig returned
5. Test cache hit (second call, no httpx)

**Connection Validation:**
1. Mock IMAPClient to succeed
2. Mock aiosmtplib to succeed
3. Add account, verify stored
4. Mock IMAPClient to fail
5. Add account, verify HTTP 503 returned

### Performance Tests

**Auto-Detection Latency:**
- Measure local providers.yaml lookup (<1ms)
- Measure Mozilla Autoconfig query (<5s with 5s timeout)
- Measure cache hit latency (<1ms)

**Connection Validation Timing:**
- Measure IMAP validation (target <10s)
- Measure SMTP validation (target <10s)
- Measure parallel validation (target <10s, not 20s)

**Memory Footprint:**
- Measure StateManager size with 100 accounts
- Measure Mozilla cache size with 100 domains
- Target: <10MB for Epic 2 components

### Security Tests

**Password Exclusion:**
- Verify password not in GET /accounts response
- Verify password not in application logs
- Verify Pydantic excludes password on serialization

**Credential Storage:**
- Verify passwords only in StateManager memory
- Verify no disk writes (stateless check)
- Verify state cleared on account removal

### Test Coverage Goals

- Unit test coverage: 85%+ for core modules (provider_detector, state_manager)
- API test coverage: 90%+ for accounts.py endpoints
- Integration test coverage: Key user flows (add account, list accounts, remove account)
- Error path coverage: All error codes tested (400, 404, 503)

---

**Document Status:** Draft  
**Next Review:** Post-implementation (after Story 2.8 completion)  
**Change Log:**
- 2025-12-04: Initial draft created from PRD, Architecture, and Epics documents
