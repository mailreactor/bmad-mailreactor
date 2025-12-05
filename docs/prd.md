# Mail Reactor - Product Requirements Document

**Author:** HC
**Date:** 2025-11-24
**Version:** 1.0

---

## Executive Summary

Mail Reactor is a self-hosted, open-source headless email client that transforms email integration from a painful multi-week engineering effort into a delightful five-minute experience. It provides a REST API abstraction over IMAP/SMTP protocols, enabling developers to send, receive, and react to emails without becoming email infrastructure experts.

The product targets independent developers and small teams building applications that need email capabilities (authentication flows, notifications, support ticket ingestion) who are caught between expensive cloud services (Sendgrid, Mailgun) with vendor lock-in, and low-level IMAP/SMTP protocols that waste weeks of development time.

Mail Reactor's open-core model (MIT-licensed foundation with commercial production-ready plugins) enables rapid adoption while building a sustainable business. The product differentiates through exceptional developer experience - zero-configuration deployment, installation measured in seconds, and debugging tools that make integration a joy rather than a burden.

### What Makes This Special

**Developer experience so good it becomes the reason people choose Mail Reactor.** 

Not just "easy to use" - but genuinely delightful. Installation takes seconds, not hours. Debugging feels like magic, not archaeology. The experience is so smooth that developers will recommend Mail Reactor to friends, write blog posts about it, and choose it even when they have budget for cloud services. DX is the moat, the differentiator, and the reason Mail Reactor wins.

---

## Project Classification

**Technical Type:** API Backend (with developer tooling ecosystem)

**Domain:** General Software

**Complexity:** Low

Mail Reactor is fundamentally a backend service that developers deploy and interact with via REST APIs. While it ships with developer tooling (CLI for management, future TUI for debugging, potential Web UI), the core product is a headless email API service. It sits between application code and email protocols, abstracting IMAP/SMTP complexity into simple HTTP endpoints.

The general software domain classification means standard software practices apply - no specialized regulatory requirements, no domain-specific compliance mandates. However, the product must handle security thoughtfully (email credentials, webhook signatures) and provide production-grade reliability through commercial plugins.

---

## Success Criteria

Success for Mail Reactor is measured by developer love, not just usage metrics. The product succeeds when:

**Developer Delight Indicators:**
- Developers complete their first successful email send/receive within 5 minutes of installation
- Users describe Mail Reactor as "the easiest email integration I've ever done"
- Developers voluntarily create content about Mail Reactor (blog posts, tutorials, demos)
- Community forms organically around the project (contributions, plugins, discussions)

**Adoption Milestones:**
- 500 GitHub stars within first 3 months (shows genuine interest, not just passing curiosity)
- 100 active production installations (defined as instances making API calls weekly)
- Sustained engagement: 75% of users who install continue using it beyond first week

**Commercial Validation:**
- 50+ paying customers for Production Pack within first year
- 5-10% free-to-paid conversion rate (validates value of commercial plugins)
- Customer testimonials explicitly mention "worth every penny" or equivalent

**Technical Excellence:**
- Zero-config success rate of 95%+ for Gmail/Outlook (auto-detection works)
- API response times under 200ms p95
- 99.9% uptime for installations using Production Pack
- Support request rate under 5% of user base (product is self-explanatory)

**The Non-Metric Success Signal:**
When developers say "I chose Mail Reactor because I wanted to, not because I had to" - that's when we've won.

---

## Product Scope

### MVP - Minimum Viable Product

**Goal:** Prove the core value proposition - email integration can be simple, fast, and delightful.

**Core Capabilities:**

1. **Zero-Configuration Account Connection**
   - Add email account via CLI: `mailreactor accounts add you@gmail.com`
   - Auto-detect IMAP/SMTP servers for major providers (Gmail, Outlook, Yahoo)
   - Persistent encrypted config file: `~/.config/mailreactor/config.toml`
   - Secure credential handling: Fernet encryption + PBKDF2 key derivation (100k+ iterations)
   - Master password from `MAILREACTOR_PASSWORD` env var or runtime prompt
   - Multiple accounts supported (email as account ID)
   - Hot reload: config changes detected within 5 seconds (no restart required)

2. **Simple Email Sending (SMTP Abstraction)**
   - REST API endpoint: `POST /accounts/{id}/messages`
   - JSON payload: to, subject, body, html, attachments
   - Synchronous fire-and-forget (no retry/queue in MVP)
   - HTML and plain text support
   - Basic file attachment support

3. **Email Retrieval with Server-Side Filtering (IMAP Abstraction)**
   - REST API endpoint: `GET /accounts/{id}/messages?filter=<IMAP_SEARCH>`
   - Support IMAP search syntax: UNSEEN, FROM, SINCE, SUBJECT, etc.
   - Return structured JSON (from, to, subject, date, body preview)
   - Pagination with cursor-based navigation
   - Server-side filtering (efficient - only matching emails transferred)

4. **Hybrid State Architecture**
   - No database required for email data - rebuild from IMAP on startup
   - Account credentials persisted to encrypted config file (secure, optional)
   - Fast restart (< 3 seconds to operational)
   - In-memory cache of recent emails (configurable timeframe)
   - Smart filtering to limit ingestion scope
   - Optional IMAP-as-database mode for advanced persistence (Epic 6)

5. **One-Command Installation and Startup**
   - PyPI package: `pipx install mailreactor` (API mode) or `pip install mailreactor` (library mode)
   - Single command to run: `mailreactor accounts add you@gmail.com` then `mailreactor start`
   - Config persisted - subsequent starts: `mailreactor start` (no re-configuration)
   - Zero system dependencies (pure Python)
   - Sensible defaults (port 8080, localhost binding)
   - Health check endpoint: `GET /health`

6. **Dual-Mode Usage (API and Library)**
   - **API Mode:** FastAPI HTTP server for REST API access (language-agnostic)
   - **Library Mode:** Direct Python import for embedded usage (no HTTP server)
   - Clean separation: `mailreactor.core` (library) + `mailreactor.api` (FastAPI layer)
   - Event-driven architecture: callbacks (library) or webhooks (API) for real-time notifications
   - Installation choice: `pip install mailreactor` (core only) vs `pip install mailreactor[api]` (includes FastAPI)

**MVP Success Criteria:**
- Developer can send first email within 5 minutes of installation
- Works reliably on macOS, Linux, and Windows
- Handles 100 emails/hour without performance degradation
- Zero crashes during 24-hour continuous operation

### Growth Features (Post-MVP)

**Phase 2 - Core Expansion:**
- Webhooks for real-time email notifications
- Multi-account support (manage multiple email accounts)
- OAuth2 authentication (Gmail, Outlook, Office365)
- IMAP IDLE for push notifications (vs polling)
- Plugin architecture and runtime framework
- Event sourcing implementation
- Basic TUI (Terminal User Interface) for debugging
- Distributed mode preparation (coordinator/worker separation)

**Phase 3 - Ecosystem Growth:**
- Advanced TUI with visual debugging (like k9s for Kubernetes)
- MCP (Model Context Protocol) plugin for AI agent integration
- Community plugin marketplace
- Template engine for email generation
- Advanced webhook features (replay, inspection, local dev mode)
- Multi-protocol exploration (JMAP, Matrix)
- Web UI for visual management

### Vision (Future)

**Enterprise & Scale:**
- Multi-tenancy with isolation and quotas (Scale Pack)
- Kubernetes operator for cloud-native deployment
- Advanced monitoring and observability
- Backup and disaster recovery tools
- High-availability clustering

**AI & Automation:**
- AI-powered email classification and routing
- Natural language CLI ("send password reset to user@example.com")
- Autonomous email agent capabilities via MCP
- Smart thread detection using ML (vs rule-based)

**Community & Ecosystem:**
- Plugin development framework and SDK
- Third-party integrations (Zapier, Make, n8n)
- Community-maintained provider templates
- Hosted debugging service (SaaS offering)

---

## Innovation & Novel Patterns

Mail Reactor explores an unconventional architectural pattern: **IMAP-as-Database** - using the email account itself not just as a data source, but as a persistent state store for lightweight system state.

### The Pattern

**Concept:** Instead of requiring an external database (Redis, PostgreSQL) for state persistence, Mail Reactor can optionally write certain state information back to the IMAP account via dedicated emails in hidden folders (e.g., `.mailreactor-state`).

**State Candidates:**
- Processing markers (last processed email UIDs, sync positions)
- Webhook delivery status (which emails triggered which webhooks, retry state)
- Runtime configuration (dynamic filters, account preferences)
- Alert state (rate limit warnings, connection health notifications)

**How It Works:**
- State kept in memory during operation (fast access)
- Periodically flushed to IMAP via structured emails (JSON payloads in email bodies)
- On restart: rebuild state from both regular emails AND state emails
- State emails marked with custom flags/labels for efficient retrieval

**Trade-offs:**
- ✅ Zero external dependencies for basic persistence
- ✅ State survives restarts without database setup
- ✅ State is portable (follows the email account)
- ❌ Limited write throughput (IMAP append is slower than database writes)
- ❌ Not suitable for high-volume state (logs, full event history)
- ❌ User could accidentally delete state (requires recovery mechanism)

### Validation Approach

**Status:** Optional and Experimental (MVP focuses on pure stateless, this is a Phase 2 exploration)

**Validation Strategy:**

1. **Provider Compatibility Testing**
   - Test IMAP folder creation, custom flags, message appending across providers
   - Validate: Gmail, Outlook.com, self-hosted (Dovecot, Postfix)
   - Document provider quirks and limitations

2. **State Recovery Testing**
   - Intentional state deletion tests
   - Recovery mechanisms: warn user, attempt state rebuild, send alert email to account owner
   - Graceful degradation: if state read fails, fall back to stateless mode

3. **Performance Benchmarking**
   - Measure IMAP write latency for state updates
   - Determine acceptable flush intervals (every 5 minutes? on specific events?)
   - Compare startup speed: stateless vs IMAP-persisted vs external DB

4. **User Experience Testing**
   - Does state-via-IMAP provide meaningful value over pure stateless?
   - Is complexity justified, or should we skip straight to external DB for Production Pack?
   - Beta user feedback: "clever innovation" or "unnecessary complexity"?

**Success Criteria for This Innovation:**
- IMAP state writes succeed on 95%+ of providers tested
- State recovery after restart is under 5 seconds for typical installations
- Beta users find value in IMAP persistence (vs indifference)
- No critical bugs where state corruption causes email loss

**Fallback Strategy:**
If IMAP-as-database proves unreliable or overly complex:
- Option 1: Skip to external DB in Production Pack (SQLite for simple, Postgres for scale)
- Option 2: Pure stateless remains the core, state is explicitly out of scope
- Option 3: Use local file-based state (JSON file) as middle ground

**Relationship to Production Pack:**
- Production Pack focuses on performance and scale (local caching, fast search, queue management)
- External database (SQLite/PostgreSQL) provides high-performance local cache
- IMAP-as-database (if successful) serves low-volume installations that want persistence without DB overhead
- Both modes can coexist: IMAP for lightweight state, DB for performance-critical operations

---

## API Backend Specific Requirements

Mail Reactor's core is a REST API that abstracts email protocols into developer-friendly HTTP endpoints. The API design prioritizes simplicity, predictability, and excellent developer experience.

### API Endpoint Specification

**Core Endpoints (MVP):**

1. **Health Check**
   - `GET /health` - System health status
   - Returns: `{"status": "healthy", "accounts": 1, "uptime": 3600}`

2. **Account Management**
   - `POST /accounts` - Add email account (alternative to CLI flag)
   - `GET /accounts` - List configured accounts
   - `GET /accounts/{id}` - Get account details
   - `DELETE /accounts/{id}` - Remove account (Phase 2)

3. **Email Sending**
   - `POST /accounts/{id}/messages` - Send email via SMTP
   - Request body: `{"to": ["addr"], "subject": "...", "body": "...", "html": "...", "attachments": [...]}`
   - Returns: `{"message_id": "...", "status": "sent"}`

4. **Email Retrieval**
   - `GET /accounts/{id}/messages?filter=<IMAP_SEARCH>` - Query emails with IMAP search syntax
   - Query params: `filter` (IMAP search), `limit` (page size), `cursor` (pagination)
   - Returns: `{"messages": [...], "next_cursor": "..."}`

5. **Message Details**
   - `GET /accounts/{id}/messages/{uid}` - Get full email details
   - Returns: Complete email structure (headers, body, attachments)

**Phase 2 Endpoints (Webhooks & Events):**
- `POST /accounts/{id}/webhooks` - Register webhook URL
- `GET /accounts/{id}/webhooks` - List webhooks
- `DELETE /accounts/{id}/webhooks/{id}` - Remove webhook
- `GET /accounts/{id}/events` - Query event history (requires Production Pack)

**API Design Principles:**
- RESTful resource modeling (accounts, messages, webhooks)
- Consistent JSON response format with `data` and `error` envelope
- Cursor-based pagination (not offset/limit - more reliable)
- Standard HTTP status codes (200, 201, 400, 401, 404, 500)
- Idempotency keys for send operations (Phase 2)
- Rate limit headers (`X-RateLimit-*`) when rate limiting active

### Authentication & Authorization Model

**MVP Approach (Local Development):**
- No authentication required
- Assumes localhost deployment (bind to 127.0.0.1 by default)
- API accessible only from local machine
- Warning logged on startup: "No authentication enabled - localhost only"

**Standard Plugin: API Key Authentication (Free/MIT Core)**
- Simple bearer token authentication
- Enable via CLI: `--api-key=<key>` or `--api-key-file=<path>`
- Auto-generate key on first run if `--api-key=auto`
- All API calls require: `Authorization: Bearer <api-key>`
- Single API key per instance (multi-key management in Production Pack)

**Production Pack: JWT Authentication**
- Token-based authentication with expiration
- Support for multiple API clients with different permissions
- Token refresh mechanism
- Integration with identity providers (OAuth2, OIDC)
- Webhook signature verification with JWT

**Authorization Scopes (Future):**
- For multi-account support: per-account access control
- For plugin system: plugin-specific permission scopes
- For multi-tenancy (Scale Pack): tenant isolation

### Data Formats & Standards

**Primary Format: JSON**
- All request/response bodies use JSON
- Content-Type: `application/json`
- UTF-8 encoding throughout

**Email Body Formats:**
- Plain text: `text/plain`
- HTML: `text/html`
- Both supported in send and retrieve operations
- Automatic MIME multipart handling

**Attachment Handling:**
- MVP: Base64-encoded inline in JSON (simple but size-limited)
- Phase 2: Multipart form-data for large files
- Scale Pack: Direct upload to S3/object storage with pre-signed URLs

**Error Response Format:**
```json
{
  "error": {
    "code": "invalid_request",
    "message": "Human-readable error description",
    "details": {"field": "validation error details"}
  }
}
```

**Timestamp Format:**
- ISO 8601 with timezone: `2025-11-24T19:30:00Z`
- All timestamps in UTC

### Rate Limiting & Throttling

**MVP Approach:**
- No rate limiting (trust model for localhost)
- Document recommended limits in Production Pack upgrade path

**Production Pack: Rate Limiting**
- Configurable rate limits per endpoint
- Default: 60 requests/minute for API calls, 10 sends/minute for SMTP
- Rate limit headers in responses:
  - `X-RateLimit-Limit: 60`
  - `X-RateLimit-Remaining: 45`
  - `X-RateLimit-Reset: 1732476000`
- HTTP 429 response when limit exceeded with `Retry-After` header

**Scale Pack: Advanced Throttling**
- Per-account rate limits (for multi-account setups)
- Per-API-key rate limits (for multi-client scenarios)
- Burst allowances (handle traffic spikes gracefully)
- Rate limit bypass for webhooks (internal traffic)

### API Versioning Strategy

**MVP Strategy:**
- No versioning in URLs (v1 is implicit)
- Breaking changes avoided during early development
- Additive changes only (new fields, new endpoints)

**Stable Release Strategy (Post-1.0):**
- Semantic versioning for the package (1.0.0, 1.1.0, 2.0.0)
- API version in URL path: `/v1/accounts`, `/v2/accounts`
- Version header optional: `X-API-Version: v1`
- Support N-1 versions (current + previous major version)
- Deprecation warnings in response headers: `X-API-Deprecation: v1 deprecated, migrate to v2 by 2026-01-01`

**Breaking Change Policy:**
- Minimum 6 months notice for deprecations
- Migration guides provided
- Dual-version support during transition period

### SDK & Client Libraries

**MVP:**
- No official SDKs (focus on API quality and documentation)
- OpenAPI/Swagger spec auto-generated from FastAPI
- Example code in docs: Python, JavaScript/Node.js, curl

**Phase 2: Official SDKs**
- Python SDK (first-class, since backend is Python)
- JavaScript/TypeScript SDK (Node.js and browser)
- Published to package managers (PyPI, npm)

**Community SDKs (Encouraged):**
- Go, Ruby, PHP, Rust - community maintained
- Official SDK template/generator to make community SDKs easier
- Recognition in docs for quality community SDKs

**SDK Design Principles:**
- Mirror API structure (accounts, messages, webhooks resources)
- Automatic retry with exponential backoff
- Built-in webhook signature verification helpers
- TypeScript types / Python type hints throughout
- Async/await support in languages that support it

### API Documentation Strategy

**MVP Documentation:**
- Auto-generated OpenAPI spec (Swagger UI at `/docs`)
- Interactive API explorer (FastAPI's built-in ReDoc at `/redoc`)
- Quick start guide with curl examples
- Hosted docs site (GitHub Pages or Read the Docs)

**Enhanced Documentation (Phase 2):**
- Code examples in multiple languages
- Use case guides (send password reset, process support tickets)
- Webhook integration tutorials
- Video walkthrough of key workflows
- Troubleshooting guide with common errors

**Documentation Quality Goals:**
- Developer can integrate without asking questions
- Every endpoint has example request/response
- Error codes explained with resolution steps
- Breaking changes highlighted prominently

---

## Functional Requirements

The following functional requirements define WHAT capabilities Mail Reactor must deliver. They are organized by capability area and numbered sequentially for traceability to epics and stories.

### Account Management

**FR-001:** System can auto-detect IMAP/SMTP server settings for common email providers (Gmail, Outlook, Yahoo, iCloud) based on email domain

**FR-002:** Users can add email account via CLI flag (`--account email@domain.com`) with interactive password prompt

**FR-003:** Users can add email account via REST API (`POST /accounts`) with email and credential payload

**FR-004:** System securely stores account credentials in memory for the duration of the session

**FR-005:** System can connect to IMAP server using auto-detected or user-provided settings

**FR-006:** System can connect to SMTP server using auto-detected or user-provided settings

**FR-007:** Users can manually override auto-detected IMAP/SMTP settings via CLI flags or API

**FR-008:** System validates account credentials on connection and reports clear error messages for failures

**FR-009:** Users can retrieve list of configured accounts via API (`GET /accounts`)

**FR-010:** Users can retrieve details of specific account via API (`GET /accounts/{id}`)

### Email Sending

**FR-011:** Users can send email via REST API with to, subject, and plain text body

**FR-012:** Users can send email with HTML body in addition to or instead of plain text

**FR-013:** Users can send email to multiple recipients (to, cc, bcc)

**FR-014:** Users can send email with file attachments (base64-encoded inline for MVP)

**FR-015:** System sends email via SMTP using configured account credentials

**FR-016:** System returns message ID and send status in API response

**FR-017:** System handles SMTP errors gracefully and returns meaningful error messages to user

**FR-018:** System supports common email headers (Reply-To, custom headers via API)

### Email Retrieval & Search

**FR-019:** Users can query emails using IMAP search syntax via REST API (`GET /accounts/{id}/messages?filter=...`)

**FR-020:** System supports standard IMAP search criteria: UNSEEN, FROM, TO, SUBJECT, SINCE, BEFORE, BODY

**FR-021:** System returns emails as structured JSON with from, to, subject, date, body preview, and UID

**FR-022:** Users can retrieve full email details including headers, complete body, and attachments via API (`GET /accounts/{id}/messages/{uid}`)

**FR-023:** System implements cursor-based pagination for email query results

**FR-024:** System performs server-side filtering (IMAP search executes on mail server, not locally)

**FR-025:** System caches recently retrieved emails in memory for fast re-access

**FR-026:** Users can configure time window for email ingestion (e.g., only last 30 days)

### System Health & Monitoring

**FR-027:** System provides health check endpoint (`GET /health`) returning status, account count, and uptime

**FR-028:** System logs startup sequence with configuration summary

**FR-029:** System logs IMAP/SMTP connection status (success/failure with details)

**FR-030:** System logs API requests and responses at configurable log level

**FR-031:** System provides clear error messages for common failure scenarios (wrong credentials, network issues, server unavailable)

### Installation & Deployment

**FR-032:** Users can install Mail Reactor via PyPI using `pipx install mailreactor`

**FR-033:** System has zero external system dependencies (pure Python, no database, no Redis)

**FR-034:** Users can start Mail Reactor with single command: `mailreactor start --account email@domain.com`

**FR-035:** System starts and becomes operational within 3 seconds

**FR-036:** System binds to localhost (127.0.0.1) by default for security

**FR-037:** Users can configure binding address and port via CLI flags (`--host`, `--port`)

**FR-038:** System displays startup message with API endpoint URL and basic usage instructions

### Authentication & Security (Core)

**FR-039:** System operates without authentication in MVP (localhost-only deployment model)

**FR-040:** System warns on startup when authentication is disabled

**FR-041:** Users can enable API key authentication via CLI flag (`--api-key=<key>`)

**FR-042:** System can auto-generate API key on first run if `--api-key=auto` specified

**FR-043:** When API key enabled, all API requests require `Authorization: Bearer <key>` header

**FR-044:** System returns 401 Unauthorized for API requests without valid authentication when auth enabled

**FR-045:** System stores API keys securely (hashed, not plaintext)

### State Management (Experimental)

**FR-046:** System operates statelessly by default (in-memory only, no persistence)

**FR-047:** System can rebuild operational state from IMAP on restart within 5 seconds

**FR-048:** System optionally supports IMAP-as-database persistence mode (experimental)

**FR-049:** In IMAP persistence mode, system writes state to dedicated IMAP folder (e.g., `.mailreactor-state`)

**FR-050:** State persisted to IMAP includes: processing markers, webhook delivery status, runtime configuration, alert state

**FR-051:** System periodically flushes in-memory state to IMAP (configurable interval)

**FR-052:** System reconstructs state from IMAP state emails on restart

**FR-053:** System detects missing or corrupted state in IMAP and falls back to stateless mode with warning

**FR-054:** System sends alert email to account owner if critical state is deleted by user

### API Design & Standards

**FR-055:** All API endpoints accept and return JSON with `Content-Type: application/json`

**FR-056:** All API responses use consistent envelope format with `data` and `error` fields

**FR-057:** System uses standard HTTP status codes (200, 201, 400, 401, 404, 500)

**FR-058:** Error responses include error code, human-readable message, and field-specific validation details

**FR-059:** All timestamps in API responses use ISO 8601 format with UTC timezone

**FR-060:** System auto-generates OpenAPI specification from API implementation

**FR-061:** System serves interactive API documentation at `/docs` endpoint (Swagger UI)

**FR-062:** System serves alternative API documentation at `/redoc` endpoint

### Plugin Architecture (Phase 2)

**FR-063:** System supports plugin registration and lifecycle management

**FR-064:** Plugins can extend core functionality (authentication, persistence, webhooks, protocols)

**FR-065:** API Key Authentication plugin is included as standard (free, MIT licensed)

**FR-066:** System loads plugins from configured plugin directory

**FR-067:** Plugins can register custom API endpoints

**FR-068:** Plugins can hook into email send/receive pipeline

### Webhook Support (Phase 2)

**FR-069:** Users can register webhook URLs via API (`POST /accounts/{id}/webhooks`)

**FR-070:** System delivers webhook events when new emails arrive matching configured filters

**FR-071:** Webhook payload includes complete email details (from, to, subject, body, headers)

**FR-072:** System delivers webhooks with retry logic (exponential backoff)

**FR-073:** Users can view webhook delivery history and status via API

**FR-074:** Users can manually replay webhook events via API

**FR-075:** System signs webhook payloads with HMAC signature for verification

**FR-076:** Users can test webhooks locally with special development mode

### Multi-Account Support (Phase 2)

**FR-077:** Users can add multiple email accounts to single Mail Reactor instance

**FR-078:** Each account operates independently with isolated state

**FR-079:** API endpoints accept account ID to specify which account to use

**FR-080:** System manages concurrent IMAP/SMTP connections for multiple accounts

**FR-081:** Users can remove accounts via API (`DELETE /accounts/{id}`)

### OAuth2 Authentication (Phase 2)

**FR-082:** Users can authenticate Gmail accounts using OAuth2 (no app password required)

**FR-083:** Users can authenticate Outlook/Office365 accounts using OAuth2

**FR-084:** System handles OAuth2 token refresh automatically

**FR-085:** System provides OAuth2 flow completion via web browser redirect

### Advanced Features (Growth)

**FR-086:** System supports IMAP IDLE for push-based email notifications (vs polling)

**FR-087:** Users can define server-side email filtering rules

**FR-088:** System implements event sourcing for complete audit trail (optional mode)

**FR-089:** System supports distributed deployment with coordinator/worker separation

**FR-090:** Terminal UI (TUI) provides visual debugging interface for email operations

**FR-091:** System exposes MCP (Model Context Protocol) interface for AI agent integration

**FR-092:** System supports email template engine with variable substitution

**FR-093:** Users can configure retry logic and delivery guarantees (Production Pack)

**FR-094:** System provides persistent storage with SQLite or PostgreSQL (Production Pack)

**FR-095:** System implements rate limiting per endpoint (Production Pack)

**FR-096:** System supports JWT authentication with token refresh (Production Pack)

**FR-097:** System provides thread detection and conversation grouping (Conversation Pack)

**FR-098:** System supports multi-tenancy with isolation and quotas (Scale Pack)

### Dual-Mode Usage (MVP Core Feature)

**FR-099:** System supports direct Python library import without FastAPI dependency, enabling embedded usage in user applications without HTTP server

**FR-100:** Users can register async callback functions for real-time email notifications using decorator pattern when using mailreactor as a library (library mode)

**FR-101:** Users can register webhook URLs via REST API to receive HTTP POST notifications when new emails arrive matching configured filters (API mode)

**FR-102:** System implements transport-agnostic event emitter that dispatches email events to registered handlers without knowledge of transport mechanism (callbacks vs webhooks)

---

## Non-Functional Requirements

### Performance

**NFR-P1: Startup Time**
- System must start and become operational within 3 seconds on typical hardware (4-core CPU, 8GB RAM)
- Rationale: Fast iteration cycles for developers, quick recovery from restarts

**NFR-P2: API Response Latency**
- Health check endpoint (`/health`) must respond within 50ms p95
- Email send operations (`POST /messages`) must respond within 200ms p95 (excludes SMTP transmission time)
- Email query operations (`GET /messages`) must respond within 200ms p95 for typical queries (up to 100 results)
- Rationale: Developer experience depends on snappy API interactions

**NFR-P3: IMAP Search Performance**
- Server-side IMAP search must return results within 2 seconds for mailboxes up to 10,000 emails
- Rationale: Developers expect fast search, leveraging IMAP server capabilities

**NFR-P4: Memory Footprint**
- System must operate within 100MB RAM for single account with 1,000 cached emails in stateless mode
- System may use up to 500MB RAM with IMAP persistence and larger caches
- Rationale: Lightweight deployment on developer machines and small VPS instances

**NFR-P5: Throughput**
- System must handle 100 emails/hour (send + receive combined) without performance degradation
- System with Production Pack must handle 1,000+ emails/hour
- Rationale: MVP targets small-scale use cases, commercial packs handle growth

**NFR-P6: Concurrent Connections**
- System must maintain stable IMAP/SMTP connections for at least 24 hours without reconnection
- System must handle concurrent API requests (up to 10 simultaneous requests for MVP)
- Rationale: Reliability for always-on deployment scenarios

### Security

**NFR-S1: Credential Storage**
- Email account credentials stored in memory only (not written to disk in MVP)
- Credentials never logged or exposed in API responses
- Credentials transmitted over secure connections only (TLS for IMAP/SMTP)
- Rationale: Developers trust Mail Reactor with email credentials - security is paramount

**NFR-S2: API Key Security**
- API keys stored using secure hashing (bcrypt or equivalent) when persistence enabled
- API keys never logged in plaintext
- API keys transmitted over HTTPS only (localhost HTTP acceptable for MVP)
- Rationale: Production deployments need secure authentication

**NFR-S3: Network Security**
- Default binding to localhost (127.0.0.1) prevents remote access without explicit configuration
- HTTPS support via reverse proxy (Nginx, Caddy) for remote deployments
- Webhook signatures (HMAC-SHA256) for payload verification (Phase 2)
- Rationale: Secure by default, explicit opt-in for network exposure

**NFR-S4: Dependency Security**
- All Python dependencies must be actively maintained (updates within last 6 months)
- Known vulnerabilities in dependencies addressed within 7 days of disclosure
- Automated dependency scanning in CI/CD pipeline
- Rationale: Supply chain security matters for tools handling credentials

**NFR-S5: Data Privacy**
- No telemetry or usage data collected without explicit user opt-in
- Opt-in telemetry anonymized and minimized (no email content, no credentials)
- Clear privacy policy for telemetry data handling
- Rationale: Developer trust requires transparency and respect for privacy

### Reliability

**NFR-R1: Connection Resilience**
- System automatically reconnects to IMAP/SMTP on connection loss (exponential backoff, max 5 retries)
- System continues operating with degraded functionality if IMAP unavailable (send-only mode)
- System logs connection failures with actionable troubleshooting information
- Rationale: Network hiccups shouldn't require manual intervention

**NFR-R2: Error Handling**
- All API endpoints return meaningful error messages (not generic "500 Internal Server Error")
- Errors include suggested remediation steps where applicable
- Errors never expose sensitive information (stack traces hidden in production mode)
- Rationale: Debugging is part of developer experience - errors should help, not frustrate

**NFR-R3: State Recovery**
- Stateless mode: system fully recovers from crash/restart by reconnecting to IMAP
- IMAP persistence mode: system recovers state from IMAP within 5 seconds of restart
- System detects corrupted state and falls back to clean slate with warning
- Rationale: Resilience to failures without data loss

**NFR-R4: Graceful Degradation**
- If auto-detection fails, system falls back to manual configuration with clear prompts
- If webhook delivery fails, system logs failure and continues processing (doesn't block)
- If IMAP persistence write fails, system continues in-memory mode with warning
- Rationale: Partial failures shouldn't cascade to complete system failure

**NFR-R5: Uptime (with Production Pack)**
- Production Pack deployments target 99.9% uptime (less than 9 hours downtime per year)
- Health check endpoint remains responsive even under load
- Scheduled maintenance communicated in advance via logs/alerts
- Rationale: Production users depend on Mail Reactor for critical email operations

### Compatibility

**NFR-C1: Platform Support**
- System must run on macOS (latest 2 major versions), Linux (Ubuntu 20.04+, Debian 11+), Windows 10+
- Python 3.10+ required (leverage modern async features)
- No platform-specific code outside clearly isolated modules
- Rationale: Developers use diverse platforms - must work everywhere

**NFR-C2: Email Provider Compatibility**
- System must support Gmail, Outlook.com, Yahoo Mail, iCloud (auto-detection and connection)
- System must support self-hosted IMAP/SMTP (Dovecot, Postfix, Zimbra, Exchange)
- System handles provider-specific quirks (Gmail's IMAP extensions, Outlook's throttling)
- Rationale: Universal email integration requires broad provider support

**NFR-C3: Python Ecosystem Compatibility**
- System installable via pip/pipx without compilation requirements (pure Python or wheels provided)
- Compatible with virtual environments, pyenv, conda
- Minimal dependency tree to reduce conflicts with user projects
- Rationale: Installation friction kills adoption - must be trivial to install

**NFR-C4: API Client Compatibility**
- REST API follows standard conventions (RESTful resources, standard HTTP verbs)
- API callable from any HTTP client (curl, Python requests, JavaScript fetch)
- CORS support for browser-based API clients (configurable, disabled by default)
- Rationale: Developers use diverse toolchains - API must be universally accessible

### Maintainability

**NFR-M1: Code Quality**
- Python code follows PEP 8 style guidelines
- Type hints throughout codebase (mypy strict mode passing)
- Test coverage minimum 80% for core modules (account, send, retrieve logic)
- Rationale: Open source success depends on contributors being able to understand code

**NFR-M2: Documentation Currency**
- API documentation auto-generated from code (OpenAPI spec always current)
- Breaking changes highlighted in changelog with migration guides
- Common issues documented in troubleshooting guide
- Rationale: Outdated docs erode trust - automation ensures currency

**NFR-M3: Versioning and Releases**
- Semantic versioning (MAJOR.MINOR.PATCH) with clear breaking change policy
- Pre-release versions for testing (alpha, beta, rc) with stability warnings
- Release notes for every version detailing changes, fixes, and breaking changes
- Rationale: Predictable releases help users plan upgrades

**NFR-M4: Plugin Stability**
- Plugin API versioned independently from core API
- Breaking changes in plugin API require 6-month deprecation notice
- Plugin compatibility matrix published (which plugins work with which core versions)
- Rationale: Plugin ecosystem health depends on stable interfaces

### Observability

**NFR-O1: Logging**
- Structured logging (JSON format) with configurable levels (DEBUG, INFO, WARN, ERROR)
- Request/response logging for all API calls (with sensitive data redacted)
- IMAP/SMTP connection events logged with success/failure details
- Rationale: Troubleshooting requires visibility into what happened

**NFR-O2: Metrics (Production Pack)**
- Prometheus-compatible metrics endpoint for monitoring integrations
- Key metrics: request latency, error rate, IMAP/SMTP connection status, email throughput
- Resource usage metrics: memory, CPU, open connections
- Rationale: Production monitoring requires metrics, not just logs

**NFR-O3: Tracing (Production Pack)**
- Request correlation IDs for tracing API calls through system
- IMAP/SMTP operation tracing (connect, search, send timings)
- Webhook delivery tracing (attempt timestamps, response codes)
- Rationale: Debugging production issues requires end-to-end visibility

---

## Summary

Mail Reactor's PRD captures a comprehensive vision for transforming email integration from a painful, multi-week engineering effort into a delightful, five-minute experience. With 98 functional requirements spanning MVP through growth phases, and rigorous non-functional requirements for performance, security, and reliability, this document provides the foundation for all downstream work.

**Key Strengths:**
- **Clear Differentiator:** Developer experience as the moat - not just easy, but genuinely delightful
- **Dual-Mode Architecture:** Both REST API (language-agnostic) AND Python library (embedded usage) from single codebase
- **Novel Innovation:** IMAP-as-database architecture for lightweight persistence without external dependencies
- **Strategic Scope:** MVP proves core value (stateless, simple), growth phases add webhooks and plugins, commercial packs provide production-grade reliability
- **Open Core Model:** MIT-licensed core with clear commercial plugin boundaries (Production Pack, Scale Pack, Conversation Pack)
- **Complete Coverage:** Every capability from product vision to API specifics captured as testable requirements

**What Makes Mail Reactor Special:**
Developer experience so good it becomes the reason people choose Mail Reactor. Zero-config deployment that works in seconds, debugging that feels like magic, and an API so intuitive that developers will write blog posts about how much they love using it. This isn't just another email API - it's the email API that makes developers happy.

**Requirements Summary:**
- **102 Functional Requirements** organized into 14 capability areas
- **22 Non-Functional Requirements** covering performance, security, reliability, compatibility, maintainability, and observability
- **MVP Scope:** 66 FRs focused on core email send/receive with stateless architecture and dual-mode usage
- **Phase 2 Expansion:** 23 FRs for webhooks, multi-account, OAuth2, and plugin foundation
- **Growth Features:** 13 FRs for advanced capabilities and commercial packs

**Next Steps:**
- **UX Design (Optional):** Not applicable for headless API backend - TUI and Web UI are separate frontends developed later
- **Architecture Workflow:** Technical design decisions, technology selection, system architecture
- **Epic Breakdown:** Transform these requirements into implementable epics and stories
- **Test Design:** Define testing strategy for API reliability and IMAP/SMTP compatibility

---

## References

**Source Documents:**
- Product Brief: `docs/product-brief-mail-reactor-2025-11-24.md`
- Brainstorming Session: `docs/brainstorming-session-results-2025-11-24.md`
- Research - Positioning: `docs/research-corrected-positioning-2025-11-24.md`
- Research - EmailEngine Competitor: `docs/research-emailengine-competitor-2025-11-24.md`
- Research - Inbound Email Webhooks: `docs/research-inbound-email-webhook-competitors-2025-11-24.md`
- Research - Technical Competitive: `docs/research-competitive-technical-2025-11-24.md`

**Project Classification:**
- Type: API Backend (with developer tooling ecosystem)
- Domain: General Software
- Complexity: Low
- Track: BMad Method (Greenfield)

---

_This PRD captures the complete requirements for Mail Reactor - a headless email client that makes email integration delightful for developers. It was created through systematic discovery and analysis, translating product vision into implementable requirements._

_The 98 functional requirements and 22 non-functional requirements form the complete capability contract for all downstream work. UX designers, architects, and developers will use this PRD to understand what to build, while the epic breakdown will define how to implement it._

_Mail Reactor succeeds when developers choose it because they want to, not because they have to._

