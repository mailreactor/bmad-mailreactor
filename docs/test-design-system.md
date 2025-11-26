# System-Level Test Design - Mail Reactor

**Date:** 2025-11-26  
**Author:** HC (TEA Agent - Test Architect)  
**Project Phase:** Solutioning (Phase 3)  
**Assessment Type:** System-Level Testability Review  
**Status:** Draft for Implementation Readiness Gate Review

---

## Executive Summary

This document provides a system-level testability assessment of Mail Reactor's architecture prior to implementation. The architecture demonstrates **PASS** testability with minor **CONCERNS** in specific areas requiring Sprint 0 setup.

**Testability Summary:**

- **Controllability:** PASS (stateless architecture, dependency injection patterns, async executor enables mocking)
- **Observability:** PASS (structlog structured logging, health endpoints, clear error messages)
- **Reliability:** CONCERNS (IMAP connection resilience needs test infrastructure, experimental IMAP-as-database persistence)

**Critical Recommendations:**

1. **Sprint 0 Priority:** Set up mock IMAP/SMTP servers for integration testing before Epic 1 implementation
2. **Phase 2 Gating:** IMAP-as-database persistence (Epic 6) requires extended validation - recommend deferral to Phase 2
3. **NFR Testing:** Performance (NFR-P1: 3-second startup) and security (credential handling) require dedicated test infrastructure
4. **Development Practices:** All developers MUST use TDD (test-first) and Nix flakes for reproducible environments - see `docs/development-practices.md`

**Key Strengths:**

- ✅ **Stateless-first design** makes tests isolated and parallelizable
- ✅ **Async executor pattern** enables clean IMAP client mocking without network calls
- ✅ **FastAPI + Pydantic** provides automatic request validation and OpenAPI test generation
- ✅ **Minimal external dependencies** reduces integration complexity and test flakiness

**Key Concerns:**

- ⚠️ **IMAP protocol complexity** requires mock server infrastructure (not just stubs)
- ⚠️ **Credential security testing** needs dedicated fixtures (no real passwords in tests)
- ⚠️ **Performance validation** for 3-second startup needs CI benchmarking
- ⚠️ **IMAP-as-database** experimental feature has unknown provider compatibility

---

## Testability Assessment

### Controllability: PASS

**Definition:** Can we control system state for testing?

**Assessment:** ✅ **PASS** - Architecture enables effective test control

**Evidence:**

1. **Stateless Architecture (NFR-R3, FR-046)**
   - In-memory state management (`StateManager`) uses Python dictionaries
   - No database dependencies = instant reset between tests
   - Full state reconstruction from IMAP in <5 seconds
   - **Testability Impact:** Each test can start with clean slate, no teardown complexity

2. **Dependency Injection Ready**
   - FastAPI's dependency injection system (`Depends()`) enables mock substitution
   - `AccountCredentials` passed as dependencies to endpoints
   - IMAP/SMTP clients initialized per-request (not global singletons)
   - **Testability Impact:** Can inject mock clients without touching production code

3. **Async Executor Pattern (ADR-002)**
   - `asyncio.run_in_executor()` wraps synchronous IMAPClient
   - Executor can be replaced with mock for tests
   - Network calls isolated in executor functions
   - **Testability Impact:** Unit tests avoid real IMAP connections entirely

4. **Provider Auto-Detection Configurable (FR-001, FR-007)**
   - IMAP/SMTP settings loaded from `providers.yaml`
   - Manual override via CLI flags and API
   - **Testability Impact:** Test mode can use localhost mock servers

**Controllability Strengths:**

- ✅ State reset via in-memory dict clearing (instant)
- ✅ Dependency injection for all external services
- ✅ No global state (each request isolated)
- ✅ Configurable providers (test mode uses mocks)

**Controllability Concerns:**

- ⚠️ **IMAP Connection Pooling (Phase 2):** If implemented, needs pool draining in tests
- ⚠️ **IMAP-as-database State (Epic 6):** Writing to real IMAP requires dedicated test accounts

**Mitigation for Concerns:**

- Create mock IMAP server (e.g., `greenmail`, `fake-imap-server`) for integration tests
- Use ephemeral test accounts on self-hosted IMAP (Dovecot container) for E2E tests
- Document test account setup in `tests/README.md`

---

### Observability: PASS

**Definition:** Can we inspect system state and validate outcomes?

**Assessment:** ✅ **PASS** - Strong observability for test assertions

**Evidence:**

1. **Structured Logging (NFR-O1, Story 1.3)**
   - `structlog` with context binding (account_id, request_id)
   - JSON logs for CI/aggregation, console logs for local dev
   - Clear event names: `email_sent`, `imap_connection_failed`, `account_connected`
   - **Testability Impact:** Tests can capture logs and assert on events

2. **Health Check Endpoint (FR-027, Story 1.5)**
   - `/health` returns status, version, uptime
   - Always accessible (no auth required)
   - Response time <50ms p95 (NFR-P2)
   - **Testability Impact:** Smoke tests verify server operational state

3. **Error Response Format (FR-058, Story 1.7)**
   - Consistent `ErrorResponse` model: `{"detail": str, "error_code": str, "request_id": str}`
   - HTTP status codes map to exception types
   - No sensitive data in errors (passwords, stack traces)
   - **Testability Impact:** Error assertions use predictable structure

4. **OpenAPI Documentation (FR-060, FR-061, Story 1.6)**
   - Auto-generated from FastAPI + Pydantic models
   - Interactive testing at `/docs` (Swagger UI)
   - Request/response schemas for validation
   - **Testability Impact:** Contract testing uses OpenAPI spec as source of truth

**Observability Strengths:**

- ✅ Structured logs enable event-driven assertions
- ✅ Health endpoint for liveness checks
- ✅ Clear error messages aid debugging
- ✅ OpenAPI spec enables contract testing

**Observability Concerns:**

- ⚠️ **Password Logging Risk:** Need automated checks that passwords never appear in logs
- ⚠️ **IMAP Operation Visibility:** IMAP commands/responses not directly observable (inside executor)

**Mitigation for Concerns:**

- Security test: Scan all logs for credential patterns (regex: password, api_key)
- Integration tests: Mock IMAP client should log commands for debugging
- Add structured logging inside `AsyncIMAPClient` methods (before executor call)

---

### Reliability: CONCERNS

**Definition:** Can tests run reliably without flakiness?

**Assessment:** ⚠️ **CONCERNS** - Requires careful test infrastructure setup

**Evidence:**

1. **Async Testing Complexity**
   - FastAPI async endpoints with `pytest-asyncio`
   - IMAPClient wrapped in executor (sync → async conversion)
   - **Testability Impact:** Async test patterns required, potential for timing issues

2. **IMAP Connection Resilience (NFR-R1)**
   - Auto-reconnect with exponential backoff
   - Graceful degradation to send-only mode
   - **Testability Impact:** Connection failure scenarios need mock server control

3. **State Recovery (NFR-R3)**
   - Stateless mode: instant recovery
   - IMAP persistence mode: 5-second recovery window
   - Corrupted state fallback logic
   - **Testability Impact:** Recovery tests need corrupted state injection

4. **Experimental IMAP-as-Database (Epic 6, FR-048-054)**
   - Write state to IMAP folders (`.mailreactor-state`)
   - Provider compatibility unknown (Gmail, Outlook quirks)
   - State recovery on restart
   - **Testability Impact:** Requires real IMAP servers with folder creation support

**Reliability Strengths:**

- ✅ Stateless default avoids state corruption risks
- ✅ Async executor pattern is well-understood (standard Python)
- ✅ Minimal external dependencies reduce flakiness surface area

**Reliability Concerns:**

- ⚠️ **Mock IMAP Server Required:** Unit tests need fake IMAP responses
- ⚠️ **IMAP-as-Database Unknown Risks:** Experimental feature may fail on some providers
- ⚠️ **Connection Timeout Testing:** Requires network delay simulation
- ⚠️ **Concurrent Request Testing:** Need to validate async safety (10 concurrent API calls per NFR-P6)

**Mitigation for Concerns:**

- **Sprint 0:** Set up `greenmail` or equivalent mock IMAP/SMTP server
- **Epic 6 Gating:** IMAP-as-database requires multi-provider validation (Gmail, Outlook, Dovecot)
- **Performance Tests:** Use pytest benchmarking plugin for startup time validation
- **Concurrency Tests:** Locust or pytest-xdist for concurrent load testing

---

## Architecturally Significant Requirements (ASRs)

ASRs are quality requirements that drive architecture decisions and pose testing challenges. Scored using **Probability × Impact** matrix (1-9 scale).

### High-Priority ASRs (Score ≥6)

#### ASR-001: 3-Second Startup Time (NFR-P1)

**Category:** PERF  
**Description:** System must start and become operational within 3 seconds  
**Probability:** 2 (Possible - stateless design helps, but IMAP connection adds latency)  
**Impact:** 3 (Critical - core developer experience differentiator)  
**Score:** 6 (MITIGATE)

**Architecture Impact:**
- Drives stateless design (no database initialization)
- Requires async IMAP connection (non-blocking)
- Lazy loading of provider configurations

**Testability Challenges:**
- Performance testing infrastructure needed (CI benchmarks)
- Cold start measurement must be consistent across environments
- IMAP mock server response time affects test validity

**Testing Approach:**
- **Unit:** Measure individual component init times (FastAPI app, config loading)
- **Integration:** Mock IMAP server with controlled latency
- **E2E:** Real startup timing on CI runner with baseline threshold
- **Tools:** `pytest-benchmark`, GitHub Actions timing annotations

**Mitigation Plan:**
- Sprint 0: Establish baseline startup time on CI (target: 2.5s with buffer)
- Per-commit: Automated benchmark regression detection (fail if >3.5s)
- Optimization: Profile startup with `cProfile` if threshold breached

---

#### ASR-002: Credential Security (NFR-S1)

**Category:** SEC  
**Description:** Email credentials stored in-memory only, never logged or exposed  
**Probability:** 2 (Possible - many code paths handle credentials)  
**Impact:** 3 (Critical - security breach would destroy trust)  
**Score:** 6 (MITIGATE)

**Architecture Impact:**
- Credentials marked `exclude=True` in Pydantic models
- No credential persistence to disk (stateless)
- TLS required for IMAP/SMTP transmission

**Testability Challenges:**
- Need to verify credentials NEVER appear in logs, responses, errors
- Cannot use real passwords in tests (security risk)
- Mock credentials must be realistic but fake

**Testing Approach:**
- **Unit:** Validate Pydantic `exclude=True` serialization
- **Integration:** Log scanner checks for credential patterns
- **E2E:** Intentional auth failure → verify error doesn't leak password
- **Security:** Automated secret scanning (pre-commit hooks)

**Mitigation Plan:**
- Test fixtures: Use `fake-credentials-do-not-use-in-prod` pattern
- Pre-commit hook: `detect-secrets` or `trufflehog` scanner
- Integration test: Capture all logs, assert no password regex matches
- Security review: Manual code audit before Phase 1 release

---

#### ASR-003: IMAP Connection Resilience (NFR-R1, NFR-P6)

**Category:** TECH  
**Description:** Auto-reconnect with exponential backoff, maintain 24-hour stability  
**Probability:** 3 (Likely - network instability is common)  
**Impact:** 2 (Degraded - feature impaired but workaround exists)  
**Score:** 6 (MITIGATE)

**Architecture Impact:**
- Retry logic in `AsyncIMAPClient`
- Connection health monitoring
- Graceful degradation to send-only mode

**Testability Challenges:**
- Network failure simulation required
- Timing-dependent (exponential backoff delays)
- 24-hour stability test impractical in CI

**Testing Approach:**
- **Unit:** Mock connection failures, verify retry count and backoff timing
- **Integration:** Mock IMAP server drops connection after N commands
- **E2E:** Real IMAP connection with network partition (Docker network control)
- **Soak Test:** 4-hour stability test (nightly CI) as proxy for 24-hour

**Mitigation Plan:**
- Sprint 0: Mock IMAP server with failure injection API
- Integration tests: Verify 5 retries with exponential backoff timing
- E2E tests: Docker Compose network disconnect/reconnect simulation
- Nightly: 4-hour soak test with health checks every 30s

---

### Medium-Priority ASRs (Score 3-5)

#### ASR-004: Multi-Provider Compatibility (NFR-C2)

**Category:** TECH  
**Description:** Support Gmail, Outlook, Yahoo, iCloud, self-hosted IMAP/SMTP  
**Probability:** 2 (Possible - each provider has quirks)  
**Impact:** 2 (Degraded - some providers may fail)  
**Score:** 4 (MONITOR)

**Testing Approach:**
- Contract tests per provider (mock responses from real IMAP captures)
- Integration tests with real test accounts (Gmail, Outlook)
- Document provider quirks in `docs/provider-compatibility.md`

---

#### ASR-005: API Response Latency (NFR-P2)

**Category:** PERF  
**Description:** API responses <200ms p95 (excluding SMTP/IMAP latency)  
**Probability:** 2 (Possible - depends on IMAP server speed)  
**Impact:** 2 (Degraded - slow API frustrates users)  
**Score:** 4 (MONITOR)

**Testing Approach:**
- Mocked IMAP/SMTP clients for API latency isolation
- Pytest-benchmark with p95 assertion
- Locust load testing (Phase 2)

---

#### ASR-006: IMAP-as-Database Persistence (Epic 6, FR-048-054)

**Category:** DATA  
**Description:** Experimental state persistence using IMAP folders  
**Probability:** 3 (Likely - unknown provider compatibility)  
**Impact:** 1 (Minor - optional feature, fallback to stateless)  
**Score:** 3 (DOCUMENT)

**Testing Approach:**
- Multi-provider validation (Gmail, Outlook, Dovecot)
- Corrupted state recovery tests
- State write failure degradation tests
- **Recommendation:** Defer to Phase 2 pending validation

---

### Low-Priority ASRs (Score 1-2)

#### ASR-007: OpenAPI Documentation Accuracy (NFR-M2)

**Category:** BUS  
**Description:** Auto-generated docs always match implementation  
**Probability:** 1 (Unlikely - FastAPI auto-generation is reliable)  
**Impact:** 2 (Degraded - outdated docs harm DX)  
**Score:** 2 (DOCUMENT)

**Testing Approach:**
- OpenAPI spec validation in CI (schema checks)
- Contract tests use `/openapi.json` as source of truth

---

## Test Levels Strategy

### Recommended Test Distribution

Based on Mail Reactor's **API Backend** architecture (FastAPI + async Python + external IMAP/SMTP):

| Test Level | Percentage | Rationale | Primary Focus |
|-----------|-----------|-----------|---------------|
| **Unit** | 50% | Pure Python business logic, Pydantic models, utility functions | Account logic, message parsing, provider detection |
| **Integration** | 35% | API endpoints with mocked IMAP/SMTP, database-less architecture | FastAPI routes, async executor pattern, error handling |
| **E2E** | 15% | Critical paths with real IMAP/SMTP servers | Account connection, send email, retrieve email |

**Rationale for Distribution:**

- **50% Unit:** Heavy business logic (provider auto-detection, IMAP search query building, message parsing)
- **35% Integration:** API-centric architecture benefits from endpoint testing with mocked external services
- **15% E2E:** Stateless design reduces need for extensive E2E (no complex state transitions)

**Comparison to Typical Distributions:**

- **UI-Heavy (40/30/30):** Mail Reactor is headless - no UI tests needed
- **Microservices (40/40/20):** Higher integration % for service contracts - not applicable here
- **Data-Heavy (60/30/10):** Mail Reactor is stateless - lower E2E need

---

### Test Level Selection Guidelines

#### Use Unit Tests For:

✅ **Business Logic:**
- Provider auto-detection (Gmail domain → IMAP/SMTP settings)
- IMAP search query construction (`UNSEEN FROM addr SINCE date`)
- Email message parsing (headers, body, attachments)
- Error classification (IMAPException → MailReactorException)

✅ **Data Validation:**
- Pydantic model validation (AccountCredentials, Message, Envelope)
- Configuration loading (environment variables, settings)
- Input sanitization (email addresses, folder names)

✅ **Utilities:**
- Async executor wrappers
- Logging configuration
- Timestamp formatting (ISO 8601)

**Characteristics:**
- Fast (<1ms per test)
- No network, no file I/O
- Mocks for external dependencies
- High coverage (80%+ for core modules per NFR-M1)

---

#### Use Integration Tests For:

✅ **API Endpoints:**
- `POST /accounts` with mock IMAP connection
- `GET /messages?filter=UNSEEN` with mock IMAP search
- `POST /messages` (send email) with mock SMTP client
- `/health` endpoint (no mocks - real health check)

✅ **Error Handling:**
- IMAP authentication failure → 401 response
- SMTP send failure → 500 with error details
- Invalid request body → 400 with field errors

✅ **Async Patterns:**
- Async executor correctness (sync IMAPClient → async wrapper)
- Concurrent API requests (10 simultaneous calls per NFR-P6)

**Characteristics:**
- Moderate speed (~100ms per test)
- FastAPI TestClient (in-memory HTTP)
- Mocked IMAP/SMTP clients
- Focus on API contracts and error paths

**Tools:**
- `pytest` with `pytest-asyncio`
- `httpx.AsyncClient` (FastAPI test client)
- Mock IMAP responses from fixtures
- OpenAPI spec validation

---

#### Use E2E Tests For:

✅ **Critical User Journeys:**
- Add Gmail account → auto-detect settings → connect → verify
- Send email → SMTP transmission → message ID returned
- Retrieve unread emails → IMAP search → structured JSON response
- Health check → startup → operational → graceful shutdown

✅ **Provider Compatibility:**
- Gmail connection (real OAuth2 test account)
- Outlook connection (real test account)
- Self-hosted IMAP (Dovecot container)

✅ **NFR Validation:**
- Startup time <3 seconds (NFR-P1)
- API response <200ms p95 (NFR-P2)
- 4-hour stability test (NFR-P6)

**Characteristics:**
- Slow (~5s per test due to IMAP connection)
- Real IMAP/SMTP servers (mock servers or test accounts)
- Full application lifecycle (startup → operation → shutdown)
- Focus on happy paths and critical risks

**Tools:**
- Docker Compose for IMAP/SMTP servers
- `greenmail` or `mailhog` for testing
- Ephemeral test accounts (auto-cleanup)
- Playwright for TUI testing (Phase 2)

---

### Test Environment Requirements

#### Local Development:
- Python 3.10+ virtual environment
- Mock IMAP/SMTP fixtures (in-memory)
- Fast feedback (<10s for unit + integration)

#### CI Pipeline:
- Docker Compose with `greenmail` IMAP/SMTP server
- Pytest with coverage reporting (80% minimum per NFR-M1)
- OpenAPI spec validation
- Performance benchmarks (startup time)

#### Staging (Phase 2):
- Real Gmail/Outlook test accounts
- Self-hosted Dovecot IMAP server
- 4-hour soak tests (nightly)

---

## NFR Testing Approach

### Security (NFR-S1 to NFR-S5)

**NFRs Covered:**
- NFR-S1: Credential storage (in-memory only, no disk persistence)
- NFR-S2: API key security (bcrypt hashing, no plaintext)
- NFR-S3: Network security (localhost default, TLS for IMAP/SMTP)
- NFR-S4: Dependency security (vulnerability scanning)
- NFR-S5: Data privacy (no telemetry, opt-in only)

**Testing Approach:**

#### 1. Credential Handling Security Tests

**Unit Tests:**
```python
# tests/unit/test_credential_security.py
def test_credentials_excluded_from_serialization():
    """Verify passwords never appear in JSON responses"""
    creds = AccountCredentials(
        email="test@example.com",
        password="secret123",
        imap_host="imap.example.com"
    )
    json_data = creds.model_dump_json()
    assert "secret123" not in json_data
    assert "password" not in json_data

def test_credentials_excluded_from_logs(caplog):
    """Verify passwords never appear in logs"""
    logger.info("account_connected", credentials=creds)
    assert "secret123" not in caplog.text
```

**Integration Tests:**
```python
# tests/integration/test_security.py
@pytest.mark.asyncio
async def test_auth_error_does_not_leak_password(client):
    """Failed auth returns generic error, no password exposure"""
    response = await client.post("/accounts", json={
        "email": "test@example.com",
        "password": "WrongPassword123!"
    })
    assert response.status_code == 401
    assert "WrongPassword123!" not in response.text
    assert "Invalid credentials" in response.json()["detail"]
```

**Security Scanning:**
- Pre-commit hook: `detect-secrets` scan
- CI: `safety check` for vulnerable dependencies
- Weekly: `pip-audit` for supply chain vulnerabilities

---

#### 2. API Key Authentication Tests (Epic 5)

**Unit Tests:**
- Verify bcrypt hashing (API keys never stored plaintext)
- Verify bearer token parsing
- Verify 401 response for missing/invalid tokens

**Integration Tests:**
- Auth disabled: No 401 errors (localhost mode)
- Auth enabled: All endpoints require valid bearer token
- Auth enabled: Invalid token → 401 with clear error message

**Tools:**
- `pytest-asyncio` for async endpoint tests
- `httpx.AsyncClient` with custom headers

---

#### 3. Network Security Tests

**E2E Tests:**
- Verify default binding to 127.0.0.1 (not 0.0.0.0)
- Verify IMAP SSL connection (port 993)
- Verify SMTP STARTTLS connection (port 587)

**Negative Tests:**
- Attempt plaintext IMAP → connection rejected
- Attempt unencrypted SMTP → connection rejected

**Tools:**
- Docker network isolation
- SSL certificate validation

---

### Performance (NFR-P1 to NFR-P6)

**NFRs Covered:**
- NFR-P1: Startup time <3 seconds
- NFR-P2: API response <200ms p95
- NFR-P3: IMAP search <2 seconds
- NFR-P4: Memory <100MB (stateless)
- NFR-P5: Throughput 100 emails/hour
- NFR-P6: 24-hour connection stability

**Testing Approach:**

#### 1. Startup Time Benchmarking (NFR-P1)

**Performance Test:**
```python
# tests/performance/test_startup.py
import time
import pytest

@pytest.mark.benchmark
def test_startup_time_under_3_seconds(benchmark):
    """Measure cold start time from import to operational"""
    def startup():
        # Import and initialize FastAPI app
        from mailreactor.main import app
        # Trigger startup events
        return app
    
    result = benchmark(startup)
    assert benchmark.stats.median < 3.0  # Median under 3s
    assert benchmark.stats.max < 3.5      # Max under 3.5s (buffer)
```

**CI Integration:**
- GitHub Actions: Record benchmark results as annotations
- Fail build if startup time >3.5 seconds
- Track trend over time (detect regressions)

---

#### 2. API Response Latency (NFR-P2)

**Performance Test:**
```python
# tests/performance/test_api_latency.py
@pytest.mark.asyncio
async def test_health_endpoint_latency(client):
    """Health check responds within 50ms p95"""
    latencies = []
    for _ in range(100):
        start = time.perf_counter()
        response = await client.get("/health")
        latencies.append((time.perf_counter() - start) * 1000)
        assert response.status_code == 200
    
    p95 = sorted(latencies)[94]  # 95th percentile
    assert p95 < 50  # Under 50ms per NFR-P2
```

**Tools:**
- `pytest-benchmark` for automated performance tracking
- `locust` for load testing (Phase 2)
- Grafana dashboards for trend visualization (Production Pack)

---

#### 3. Memory Footprint (NFR-P4)

**Resource Test:**
```python
# tests/performance/test_memory.py
import psutil
import os

def test_memory_footprint_under_100mb():
    """Stateless mode uses <100MB RAM"""
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / 1024 / 1024  # MB
    
    # Simulate 1000 cached emails
    state_manager.cache_emails([mock_email() for _ in range(1000)])
    
    mem_after = process.memory_info().rss / 1024 / 1024  # MB
    assert mem_after < 100  # Under 100MB per NFR-P4
```

---

#### 4. Stability/Soak Testing (NFR-P6)

**Soak Test (Nightly CI):**
```python
# tests/stability/test_soak.py
@pytest.mark.soak
@pytest.mark.asyncio
async def test_4_hour_stability():
    """24-hour proxy: 4-hour soak test with health checks"""
    start = time.time()
    duration = 4 * 60 * 60  # 4 hours
    
    while time.time() - start < duration:
        # Health check every 30s
        response = await client.get("/health")
        assert response.status_code == 200
        await asyncio.sleep(30)
    
    # No crashes, memory leaks, or connection drops
```

**CI Configuration:**
- Nightly GitHub Actions workflow
- 4-hour timeout
- Memory profiling enabled
- Alert on failure (Slack/email)

---

### Reliability (NFR-R1 to NFR-R5)

**NFRs Covered:**
- NFR-R1: Connection resilience (auto-reconnect)
- NFR-R2: Error handling (meaningful messages)
- NFR-R3: State recovery (<5 seconds)
- NFR-R4: Graceful degradation
- NFR-R5: 99.9% uptime (Production Pack)

**Testing Approach:**

#### 1. Connection Resilience Tests (NFR-R1)

**Integration Test:**
```python
# tests/integration/test_resilience.py
@pytest.mark.asyncio
async def test_imap_auto_reconnect_on_failure():
    """IMAP connection loss triggers auto-reconnect"""
    mock_imap = MockIMAPServer()
    
    # First connection succeeds
    client = AsyncIMAPClient(host=mock_imap.host)
    await client.connect()
    
    # Simulate connection drop
    mock_imap.disconnect()
    
    # Next operation triggers reconnect
    with pytest.raises(IMAPConnectionError):
        await client.search(["UNSEEN"])
    
    # Reconnect succeeds after backoff
    mock_imap.reconnect()
    await asyncio.sleep(1)  # Wait for backoff
    result = await client.search(["UNSEEN"])
    assert result is not None
```

**Retry Logic Validation:**
```python
def test_exponential_backoff_timing():
    """Verify retry delays: 1s, 2s, 4s, 8s, 16s"""
    retry_delays = []
    
    @retry_with_backoff(max_retries=5)
    def failing_operation():
        retry_delays.append(time.time())
        raise ConnectionError()
    
    with pytest.raises(ConnectionError):
        failing_operation()
    
    # Calculate actual delays
    delays = [retry_delays[i+1] - retry_delays[i] 
              for i in range(len(retry_delays)-1)]
    
    # Verify exponential backoff (with tolerance)
    assert 0.9 < delays[0] < 1.1  # ~1s
    assert 1.9 < delays[1] < 2.1  # ~2s
    assert 3.9 < delays[2] < 4.1  # ~4s
```

---

#### 2. Error Handling Tests (NFR-R2)

**Integration Test:**
```python
@pytest.mark.asyncio
async def test_clear_error_messages():
    """Errors include actionable troubleshooting info"""
    response = await client.post("/accounts", json={
        "email": "invalid-email",
        "password": "test123"
    })
    
    assert response.status_code == 400
    error = response.json()
    
    # Meaningful error message
    assert "Invalid email format" in error["detail"]
    
    # Suggested remediation
    assert "email" in error["details"]
    assert "valid email address" in error["details"]["email"]
```

---

#### 3. State Recovery Tests (NFR-R3)

**Unit Test (Stateless Mode):**
```python
def test_stateless_instant_recovery():
    """Stateless mode recovers instantly"""
    state_manager = StateManager()
    state_manager.add_account("acc1", credentials)
    
    # Simulate crash
    state_manager._accounts.clear()
    
    # Recovery: rebuild from IMAP (mocked)
    start = time.time()
    state_manager.recover_from_imap(mock_imap_client)
    recovery_time = time.time() - start
    
    assert recovery_time < 5.0  # Under 5s per NFR-R3
    assert "acc1" in state_manager._accounts
```

**Integration Test (IMAP Persistence):**
```python
@pytest.mark.asyncio
async def test_imap_persistence_recovery():
    """IMAP-as-database recovers state in <5s"""
    # Write state to IMAP
    await state_manager.flush_to_imap(imap_client)
    
    # Simulate restart
    new_state_manager = StateManager()
    
    # Recover state
    start = time.time()
    await new_state_manager.recover_from_imap(imap_client)
    recovery_time = time.time() - start
    
    assert recovery_time < 5.0
    assert new_state_manager.state_equals(state_manager)
```

---

### Maintainability (NFR-M1 to NFR-M4)

**NFRs Covered:**
- NFR-M1: Code quality (PEP 8, type hints, 80% coverage)
- NFR-M2: Documentation currency (auto-generated OpenAPI)
- NFR-M3: Versioning (semantic versioning)
- NFR-M4: Plugin stability (Phase 2)

**Testing Approach:**

#### 1. Code Quality Gates (NFR-M1)

**CI Checks:**
- `ruff check .` (linting, fail on error)
- `mypy src/` (type checking, strict mode)
- `pytest --cov=src --cov-report=term --cov-fail-under=80`

**Pre-commit Hooks:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    hooks:
      - id: mypy
```

---

#### 2. OpenAPI Contract Tests (NFR-M2)

**Contract Test:**
```python
# tests/contract/test_openapi.py
@pytest.mark.asyncio
async def test_openapi_spec_valid():
    """OpenAPI spec matches implementation"""
    response = await client.get("/openapi.json")
    spec = response.json()
    
    # Validate OpenAPI 3.0+ schema
    validate_spec(spec)
    
    # Verify critical endpoints documented
    assert "/health" in spec["paths"]
    assert "/accounts" in spec["paths"]
    assert "/accounts/{account_id}/messages" in spec["paths"]
```

**Response Schema Validation:**
```python
@pytest.mark.asyncio
async def test_health_response_matches_openapi():
    """Health endpoint response matches OpenAPI schema"""
    openapi_spec = await client.get("/openapi.json")
    health_schema = openapi_spec["paths"]["/health"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    
    response = await client.get("/health")
    
    # Validate response against schema
    jsonschema.validate(response.json(), health_schema)
```

---

## Test Environment Requirements

### Local Development

**Requirements:**
- Python 3.10+ with virtual environment
- `pytest`, `pytest-asyncio`, `pytest-cov`
- `httpx` for API testing
- Mock IMAP/SMTP fixtures (in-memory)

**Setup:**
```bash
pip install -e ".[dev]"
pytest tests/unit tests/integration
```

**Characteristics:**
- Fast feedback (<10s for unit + integration)
- No external services required
- Isolated test runs (parallel-safe)

---

### CI Pipeline (GitHub Actions)

**Requirements:**
- Docker Compose with `greenmail` IMAP/SMTP server
- Python 3.10, 3.11, 3.12 matrix testing
- Coverage reporting (Codecov integration)
- Performance benchmarks

**Docker Compose:**
```yaml
# tests/docker-compose.test.yml
services:
  greenmail:
    image: greenmail/standalone:latest
    ports:
      - "3143:3143"  # IMAP
      - "3025:3025"  # SMTP
    environment:
      GREENMAIL_OPTS: "-Dgreenmail.setup.test.all -Dgreenmail.hostname=0.0.0.0 -Dgreenmail.auth.disabled"
```

**CI Workflow:**
```yaml
# .github/workflows/test.yml
- name: Start Mock IMAP/SMTP
  run: docker-compose -f tests/docker-compose.test.yml up -d

- name: Run Tests
  run: pytest tests/ --cov=src --cov-report=xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
```

---

### Staging Environment (Phase 2)

**Requirements:**
- Real Gmail test account (OAuth2)
- Real Outlook test account
- Self-hosted Dovecot IMAP server (Docker)
- 4-hour soak tests (nightly)

**Test Accounts:**
- `mailreactor-test-gmail@gmail.com` (OAuth2 app password)
- `mailreactor-test-outlook@outlook.com` (OAuth2)
- Ephemeral accounts on Dovecot (auto-created, auto-deleted)

---

## Testability Concerns

### Critical Concerns (Must Address in Sprint 0)

#### CONCERN-001: Mock IMAP Server Infrastructure Missing

**Issue:** Unit and integration tests need mock IMAP server, but none configured yet

**Impact:**
- Cannot test IMAP operations without real servers
- E2E tests would require live credentials (security risk)
- Integration tests would be slow and flaky

**Mitigation:**
- **Sprint 0 Task:** Set up `greenmail` or equivalent mock IMAP/SMTP server
- Create Docker Compose config for local development
- Document mock server usage in `tests/README.md`

**Acceptance Criteria:**
- Mock IMAP server responds to CONNECT, LOGIN, SEARCH, FETCH
- Mock SMTP server accepts SEND commands
- Integration tests use mock server (no real credentials)

---

#### CONCERN-002: Performance Benchmark Infrastructure Missing

**Issue:** NFR-P1 (3-second startup) and NFR-P2 (200ms API latency) need automated validation

**Impact:**
- Performance regressions undetected until production
- No baseline for optimization efforts
- Manual testing is inconsistent

**Mitigation:**
- **Sprint 0 Task:** Configure `pytest-benchmark` for startup time
- Create GitHub Actions workflow for benchmark tracking
- Fail CI build if startup time >3.5 seconds

**Acceptance Criteria:**
- Automated startup time benchmark on every commit
- Automated API latency benchmark for health endpoint
- Trend visualization in CI logs

---

### Medium Concerns (Address Before Epic Implementation)

#### CONCERN-003: IMAP-as-Database Provider Compatibility Unknown

**Issue:** Epic 6 (IMAP persistence) experimental - unknown if Gmail/Outlook support folder creation

**Impact:**
- Feature may fail on major providers
- State corruption risk if provider rejects writes
- Recovery logic untested

**Mitigation:**
- **Epic 6 Gating:** Multi-provider validation required before implementation
- Create test matrix: Gmail, Outlook, Yahoo, Dovecot, Exchange
- Document provider compatibility in `docs/provider-compatibility.md`

**Recommendation:** Defer Epic 6 to Phase 2 pending validation

---

#### CONCERN-004: Credential Security Testing Gaps

**Issue:** No automated scanning for password leaks in logs/responses

**Impact:**
- Passwords could accidentally appear in logs (human error)
- Compliance risk (PCI-DSS, GDPR)

**Mitigation:**
- **Sprint 0 Task:** Set up `detect-secrets` pre-commit hook
- Create integration test: Scan all logs for credential patterns
- Security review: Manual code audit before Phase 1 release

**Acceptance Criteria:**
- Pre-commit hook blocks commits with secrets
- Integration test fails if password regex matches in logs
- CI pipeline includes `safety check` for vulnerable dependencies

---

### Low Concerns (Monitor During Development)

#### CONCERN-005: Async Test Flakiness Risk

**Issue:** Async tests with timing dependencies can be flaky

**Mitigation:**
- Use deterministic waits (not `asyncio.sleep`)
- Mock clock for time-dependent tests
- Document async testing best practices

---

#### CONCERN-006: OpenAPI Spec Drift Risk

**Issue:** Manual documentation updates could drift from code

**Mitigation:**
- Already mitigated: FastAPI auto-generates OpenAPI spec
- Add contract tests to validate spec accuracy

---

## Recommendations for Sprint 0

Sprint 0 prepares the development environment and test infrastructure. **Environment setup MUST be verified first before any other work.**

### 🔴 CRITICAL Task #1: Environment Setup & Verification (BLOCKING)

**Priority:** MUST complete and verify before ANY other Sprint 0 tasks.

**Subtasks:**

1. **Create Development Environment Configurations**
   - Create `flake.nix` with Python 3.10+ and uv package manager
   - Create `.envrc` for direnv auto-activation
   - Create `pyproject.toml` with project metadata and dependencies
   - Create `.gitignore` (ignore .venv, .direnv, etc.)
   - **Estimated Effort:** 3 hours

2. **Write Environment Setup Documentation**
   - Complete `docs/environment-setup-guide.md` (both Nix and manual methods)
   - Update `README.md` with quick start for both methods
   - Document troubleshooting for common issues
   - **Estimated Effort:** 2 hours

3. **Verify Nix Setup (macOS + Linux)**
   - Test direnv auto-activation
   - Verify Python 3.10 from Nix
   - Verify uv package manager works
   - Run through complete verification checklist
   - **Estimated Effort:** 2 hours (1h per platform)
   - **Tester:** Team member(s)

4. **Verify Manual Setup (Windows)**
   - Test Python 3.10+ installation
   - Test venv creation and activation
   - Test uv installation and package management
   - Run through complete verification checklist
   - **Estimated Effort:** 1 hour
   - **Tester:** HC

5. **Verify Manual Setup (WSL2)**
   - Test Python 3.10+ installation
   - Test venv creation and activation
   - Test uv installation and package management
   - Run through complete verification checklist
   - **Estimated Effort:** 1 hour
   - **Tester:** HC

6. **Verify Manual Setup (Linux without Nix)**
   - Test Python 3.10+ installation
   - Test venv creation and activation
   - Test uv installation and package management
   - Run through complete verification checklist
   - **Estimated Effort:** 1 hour
   - **Tester:** Team member

7. **Fix Issues and Iterate**
   - Address any verification failures
   - Update documentation with fixes
   - Re-verify all platforms
   - **Estimated Effort:** 2 hours

**Task #1 Total Effort:** ~13 hours (~1.5-2 days)

**Success Criteria:**
- ✅ HC confirms: "Windows setup works perfectly"
- ✅ HC confirms: "WSL2 setup works perfectly"
- ✅ Team confirms: "Nix setup works on macOS"
- ✅ Team confirms: "Nix setup works on Linux"
- ✅ Team confirms: "Manual Linux (no Nix) works"
- ✅ All verification checklists pass (see `docs/environment-setup-guide.md`)
- ✅ Both methods produce identical Python environments

**BLOCKING:** No other Sprint 0 tasks begin until Task #1 is 100% verified.

**Reference:** See `docs/environment-setup-guide.md` for complete verification checklists.

---

### High-Priority Tasks (After Task #1 Complete)

2. **TDD Infrastructure and Documentation (REQUIRED)**
   - Create `docs/tdd-guide.md` with red-green-refactor examples
   - Add test templates to `tests/templates/` directory
   - Configure pre-commit hook for test coverage enforcement (80% minimum)
   - Create code review checklist for TDD compliance
   - **Estimated Effort:** 2 hours
   - **Reference:** See `docs/development-practices.md` for TDD workflow

3. **Mock IMAP/SMTP Server Setup**
   - Install `greenmail` or equivalent
   - Create Docker Compose configuration
   - Document mock server API for test fixtures
   - **Estimated Effort:** 4 hours

4. **Test Project Structure**
   - Create `tests/` directory structure (unit, integration, e2e, performance, security)
   - Set up `conftest.py` with shared fixtures
   - Document testing philosophy in `tests/README.md`
   - **Estimated Effort:** 2 hours

5. **Security Scanning Setup**
   - Install `detect-secrets` pre-commit hook
   - Create integration test for log scanning
   - Configure `safety check` in CI
   - **Estimated Effort:** 2 hours

6. **Performance Benchmark Infrastructure**
   - Configure `pytest-benchmark` for startup time
   - Create GitHub Actions workflow for benchmark tracking
   - Set failure thresholds (3.5s startup, 50ms health check)
   - **Estimated Effort:** 3 hours

7. **CI Pipeline Configuration**
   - GitHub Actions workflow for unit + integration tests
   - Coverage reporting (Codecov)
   - Docker Compose integration for mock servers
   - Nix-based CI builds
   - **Estimated Effort:** 3 hours

**Tasks 2-7 Total Effort:** ~16 hours (~2 days)

**Total Sprint 0 Effort:** ~29 hours (~3.5-4 days with verification)

**Note on Cucumber/BDD:** After analysis, Cucumber is **NOT recommended** for Mail Reactor. Use Pytest with BDD-style test names and docstrings instead. See `docs/development-practices.md` Section 3 for detailed rationale.

**Note on UV vs PIP:** Use **uv** instead of pip for 10-100x faster package management. See `docs/environment-setup-guide.md` for details.

---

### Medium-Priority Tasks (Can Start During Epic 1)

6. **Epic 6 Multi-Provider Validation**
   - Create test accounts on Gmail, Outlook, Yahoo
   - Test IMAP folder creation on each provider
   - Document provider compatibility matrix
   - **Estimated Effort:** 8 hours

7. **Contract Testing Framework**
   - OpenAPI spec validation tests
   - Response schema validation
   - **Estimated Effort:** 4 hours

---

### Low-Priority Tasks (Phase 2)

8. **Soak Testing Infrastructure**
   - 4-hour stability test (nightly CI)
   - Memory profiling integration
   - **Estimated Effort:** 6 hours

9. **Load Testing Setup**
   - Locust configuration for throughput testing
   - Concurrent request testing (NFR-P6)
   - **Estimated Effort:** 8 hours

---

## Summary and Next Steps

### Testability Verdict

**Overall Assessment:** ✅ **PASS WITH CONCERNS**

Mail Reactor's architecture is **testable** with strong controllability and observability, but requires **Sprint 0 infrastructure setup** before implementation begins.

**Strengths:**
- Stateless architecture enables isolated, parallelizable tests
- FastAPI + Pydantic provide automatic validation and OpenAPI generation
- Async executor pattern enables clean IMAP client mocking
- Minimal external dependencies reduce test complexity

**Concerns:**
- Mock IMAP/SMTP infrastructure required (critical)
- Performance benchmark automation needed (critical)
- IMAP-as-database experimental feature needs multi-provider validation (medium)
- Security scanning automation needed (medium)

---

### Gate Check Recommendation

**Implementation Readiness:** ✅ **PROCEED WITH CONDITIONS**

**Conditions:**
1. ✅ **Complete Sprint 0 tasks** (14 hours, ~2 days) before Epic 1 implementation
2. ⚠️ **Defer Epic 6** (IMAP-as-database) to Phase 2 pending multi-provider validation
3. ⚠️ **NFR validation** for performance and security must be automated in CI

**If Conditions Met:**
- Architecture is sound and testable
- Proceed to Epic 1 implementation with confidence

**If Conditions Not Met:**
- Risk of flaky tests and undetected performance regressions
- Recommend addressing Sprint 0 concerns before implementation

---

### Next Workflows

After completing Sprint 0 and receiving gate approval:

1. **`/bmad:bmm:workflows:framework`** - Set up Playwright test framework (if TUI in Phase 2)
2. **`/bmad:bmm:workflows:atdd`** - Generate failing tests for P0 scenarios per epic
3. **`/bmad:bmm:workflows:ci`** - Configure CI pipeline stages (unit → integration → E2E)
4. **`/bmad:bmm:workflows:sprint-planning`** - Begin Sprint 1 with Epic 1 implementation

---

## Appendix

### Knowledge Base References

- `risk-governance.md` - Risk classification framework (6 categories: TECH, SEC, PERF, DATA, BUS, OPS)
- `probability-impact.md` - Risk scoring methodology (probability × impact matrix, 1-9 scale)
- `test-levels-framework.md` - Test level selection guidance (Unit vs Integration vs E2E)
- `test-priorities-matrix.md` - P0-P3 prioritization criteria
- `nfr-criteria.md` - NFR validation approach (security, performance, reliability)

### Related Documents

- **PRD:** `docs/prd.md` - Product requirements (98 FRs, 24 NFRs)
- **Architecture:** `docs/architecture.md` - Technical decisions and ADRs
- **Epics:** `docs/epics.md` - Epic breakdown (6 epics, 41 stories)
- **Workflow Status:** `docs/bmm-workflow-status.yaml` - Project phase tracking
- **Development Practices:** `docs/development-practices.md` - **REQUIRED** TDD workflow, Nix flakes setup, BDD/Cucumber guidance

---

**Generated by:** BMad TEA Agent - Test Architect Module  
**Workflow:** `.bmad/bmm/workflows/testarch/test-design`  
**Version:** 4.0 (BMad v6)  
**Date:** 2025-11-26
