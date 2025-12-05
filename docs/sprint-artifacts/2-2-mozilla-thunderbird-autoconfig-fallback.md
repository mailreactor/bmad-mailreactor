# Story 2.2: Mozilla Thunderbird Autoconfig Fallback

Status: drafted

## Story

As a developer,  
I want Mail Reactor to use Mozilla's Thunderbird Autoconfig database for unknown providers,  
So that I can connect to a wider range of email providers without manual configuration.

## Acceptance Criteria

**Given** Story 2.1 provider detection foundation exists  
**When** extending for broader provider support via Mozilla Autoconfig  
**Then** `src/mailreactor/core/provider_detector.py` is enhanced with:
- `detect_via_mozilla_autoconfig(domain: str) -> Optional[ProviderConfig]` async function
- Queries Mozilla Autoconfig database via HTTP: `https://autoconfig.thunderbird.net/v1.1/{domain}`
- Parses XML response to extract IMAP/SMTP server settings (hostname, port, socketType)
- Falls back to trying `autoconfig.{domain}/mail/config-v1.1.xml` (ISP-hosted config)
- Returns `ProviderConfig` if successful, `None` if not found

**And** Detection strategy follows this cascade:
1. Check local providers.yaml (fast, offline)
2. If not found, try Mozilla Autoconfig (network call)
3. If not found, try ISP-hosted autoconfig (network call)
4. If all fail, return None (requires manual configuration)

**And** Mozilla Autoconfig responses are NOT cached in MVP:
- Each detection performs fresh lookup (stateless design)
- 5-second timeout prevents excessive delay
- Future: Epic 6 (IMAP-as-database) could add persistent cache

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
- Ignore `<username>` field (MVP rule: username = email always)

**And** MVP authentication rule (documented in Dev Notes):
- Username: Always equals email address (hardcoded rule, no overrides in MVP)
- Password: Same for IMAP and SMTP (unified authentication for Big 4)
- Applies to all auto-detected providers (Big 4 + Mozilla Autoconfig results)

**And** Credential environment variables (documented in Dev Notes):
- `MAILREACTOR_PASSWORD`: Default password for both IMAP and SMTP
- `MAILREACTOR_IMAP_PASSWORD`: Override for IMAP only (advanced scenarios)
- `MAILREACTOR_SMTP_PASSWORD`: Override for SMTP only (advanced scenarios)
- Password resolution: specific override → default → prompt
- `.env` file support via pydantic-settings (auto-loaded)

**Prerequisites:** Story 2.1 (basic provider detection exists)

## Tasks / Subtasks

- [ ] Add Mozilla Autoconfig async HTTP client (AC: httpx client, 5s timeout, User-Agent header)
  - [ ] Install httpx dependency if not present (add to pyproject.toml)
  - [ ] Create `_get_httpx_client()` helper with timeout and User-Agent configuration
  - [ ] User-Agent format: `MailReactor/{version}` (extract version from package metadata)
  - [ ] Timeout: 5 seconds (don't block startup, per NFR-P1)
  - [ ] Connection pooling: Use default httpx behavior (single client instance)

- [ ] Implement Mozilla Autoconfig XML parsing (AC: parse XML, extract IMAP/SMTP settings)
  - [ ] Create `_parse_autoconfig_xml(xml_content: str) -> Optional[ProviderConfig]` function
  - [ ] Use `xml.etree.ElementTree` (Python stdlib, no extra dependency)
  - [ ] Parse `<incomingServer type="imap">` section: extract hostname, port, socketType
  - [ ] Parse `<outgoingServer type="smtp">` section: extract hostname, port, socketType
  - [ ] Map socketType values: "SSL" → imap_ssl=True, "STARTTLS" → smtp_starttls=True
  - [ ] Ignore `<username>` field from XML (MVP rule: username = email always)
  - [ ] Handle missing/invalid fields gracefully: return None if required fields absent
  - [ ] Log DEBUG: Parsed IMAP/SMTP settings for troubleshooting

- [ ] Implement Mozilla Autoconfig network lookup (AC: async function, cascade logic, no caching)
  - [ ] Create `detect_via_mozilla_autoconfig(domain: str) -> Optional[ProviderConfig]` async function
  - [ ] Step 1: Query `https://autoconfig.thunderbird.net/v1.1/{domain}`
  - [ ] Step 2: If HTTP 404 or network error, try `http://autoconfig.{domain}/mail/config-v1.1.xml` (ISP fallback)
  - [ ] Step 3: If both fail, return None
  - [ ] Handle HTTP errors: 404 (not found), timeout, connection refused
  - [ ] Log INFO: Lookup attempt, success/failure for each URL
  - [ ] Return ProviderConfig with provider_name set to domain

- [ ] Integrate Mozilla fallback into detect_provider flow (AC: cascade local → Mozilla → ISP → None)
  - [ ] Modify `detect_provider(email: str)` to be async (network calls required)
  - [ ] Step 1: Try local providers.yaml (existing logic, <1ms)
  - [ ] Step 2: If None, try `await detect_via_mozilla_autoconfig(domain)`
  - [ ] Step 3: Return ProviderConfig if found, None if all sources fail
  - [ ] Breaking change documented: caller must now await detect_provider()
  - [ ] Note: Call sites updated in future stories (2.3+)

- [ ] Add structured logging for Mozilla Autoconfig (AC: INFO/DEBUG logs)
  - [ ] Log INFO: "mozilla_autoconfig_lookup", domain=domain, source="mozilla" or "isp"
  - [ ] Log INFO: "mozilla_autoconfig_success", domain=domain, imap_host=host
  - [ ] Log INFO: "mozilla_autoconfig_failed", domain=domain, reason="not_found" or "timeout"
  - [ ] Log DEBUG: "mozilla_autoconfig_xml", xml_content=xml (for troubleshooting)

- [ ] Write unit tests for XML parsing (AC: test valid/invalid XML, missing fields)
  - [ ] Test valid Mozilla Autoconfig XML: verify ProviderConfig extraction
  - [ ] Test XML with missing IMAP section: return None
  - [ ] Test XML with missing SMTP section: return None
  - [ ] Test XML with invalid socketType: graceful handling
  - [ ] Test XML with missing hostname/port: return None
  - [ ] Test malformed XML: return None (no crash)
  - [ ] Coverage target: 100% for `_parse_autoconfig_xml()` function

- [ ] Write unit tests for Mozilla Autoconfig network lookup (AC: mock httpx, test cascade, no caching)
  - [ ] Test Mozilla success: mock HTTP 200 with valid XML, verify ProviderConfig returned
  - [ ] Test Mozilla 404, ISP success: verify fallback to ISP autoconfig
  - [ ] Test both Mozilla and ISP fail: return None
  - [ ] Test network timeout: verify 5s timeout enforced
  - [ ] Test connection error: graceful handling, return None

- [ ] Write integration test for end-to-end autoconfig flow (AC: email → detect → ProviderConfig)
  - [ ] Test unknown domain (not in providers.yaml) → Mozilla success
  - [ ] Test unknown domain → Mozilla fail → ISP success
  - [ ] Test unknown domain → both fail → None
  - [ ] Verify all 3 detection sources work together: local → Mozilla → ISP → None

## Dev Notes

### Learnings from Previous Story

**From Story 2-1-provider-configuration-and-basic-auto-detection (Status: done)**

- **New Service Created**: `ProviderDetector` with `detect_provider()` method available at `mailreactor/src/mailreactor/core/provider_detector.py`
- **Files Created**: 
  - `provider_detector.py`: Detection logic with caching and logging
  - `providers.yaml`: Local provider configs (Gmail, Outlook, Yahoo, iCloud + 14 aliases)
  - `models/account.py`: Pydantic models (ProviderConfig, IMAPConfig, SMTPConfig, MailAccount)
- **Caching Pattern**: Module-level `_PROVIDERS_CACHE` global for YAML (load once at import)
- **Testing Strategy**: Behavior-focused tests (26 tests, 100% coverage, zero brittleness)
  - Don't hardcode provider values (Gmail IMAP host, etc.)
  - Test behavior, not configuration data
  - Use dynamic YAML validation via `loaded_providers` fixture
- **Technical Debt**: None noted
- **Pending Review Items**: None (story complete, status: done)

[Source: stories/2-1-provider-configuration-and-basic-auto-detection.md#Dev-Agent-Record]

### Product Decisions from Party Mode Session (2025-12-05)

**Credential Strategy (MVP - Single Account):**

1. **MVP Authentication Rule (Hardcoded, Forever):**
   - Username = email address (always, for all providers)
   - Password: Same for both IMAP and SMTP (unified authentication)
   - No username template system, no `--username` flags in MVP
   - Applies to: Big 4 + Mozilla Autoconfig results + manual configuration
   - Simple implementation: When creating IMAPConfig/SMTPConfig, use email as username

2. **Environment Variables (Password Only):**
   - `MAILREACTOR_PASSWORD`: Default password for both IMAP and SMTP
   - `MAILREACTOR_IMAP_PASSWORD`: Override for IMAP only (advanced: relay services)
   - `MAILREACTOR_SMTP_PASSWORD`: Override for SMTP only (advanced: relay services)
   - Password resolution: specific override → default → prompt if not set
   - `.env` file auto-loaded by pydantic-settings

3. **CLI Flags (All Config Except Passwords and Username):**
   - Required: `--account <email>`
   - Optional overrides: `--imap-host`, `--imap-port`, `--imap-ssl`
   - Optional overrides: `--smtp-host`, `--smtp-port`, `--smtp-starttls`
   - NO `--password` flag (security risk: shell history, process listings)
   - NO `--username` flags (MVP: username = email, hardcoded)

4. **No Caching in MVP:**
   - Auto-detection runs fresh each startup (stateless design)
   - Users re-run command with flags (shell history = easy UX)
   - 5-second timeout prevents excessive delay
   - Future: Epic 6 (IMAP-as-database) could add persistent cache

5. **No Config File in MVP:**
   - All configuration via CLI flags + env vars
   - Users manage `.env` files themselves (direnv, dotenv, etc.)
   - Stateless restart requires full config re-specification

**Rationale:**
- Shell history makes command reuse trivial (up arrow)
- `.env` files = user's responsibility (standard practice)
- Stateless design = clean, no hidden state
- YAGNI: Don't cache what doesn't need caching
- YAGNI: Don't template usernames when email works for 99% of cases

[Source: Party mode session 2025-12-05, HC + team architectural decisions]

### Architecture Patterns and Constraints

**Mozilla Autoconfig Integration (from Architecture):**

Architecture document (section "Provider Auto-Detection") and Tech Spec define the Mozilla Thunderbird Autoconfig integration:

**Detection Cascade Strategy:**
1. **Local providers.yaml** (Story 2.1): Fast, offline, covers 4 major providers + aliases
2. **Mozilla Autoconfig** (Story 2.2): Network call, covers 1000s of providers
3. **ISP-hosted autoconfig** (Story 2.2): Provider-specific fallback
4. **Manual configuration** (Story 2.3): Universal fallback

**Mozilla Autoconfig Specification:**
- URL format: `https://autoconfig.thunderbird.net/v1.1/{domain}`
- Response format: XML (documented by Mozilla Thunderbird project)
- Spec: https://wiki.mozilla.org/Thunderbird:Autoconfiguration
- ISP fallback: `http://autoconfig.{domain}/mail/config-v1.1.xml`

**XML Schema Example:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<clientConfig version="1.1">
  <emailProvider id="example.com">
    <domain>example.com</domain>
    <displayName>Example Provider</displayName>
    
    <incomingServer type="imap">
      <hostname>imap.example.com</hostname>
      <port>993</port>
      <socketType>SSL</socketType>
      <authentication>password-cleartext</authentication>
      <username>%EMAILADDRESS%</username>
    </incomingServer>
    
    <outgoingServer type="smtp">
      <hostname>smtp.example.com</hostname>
      <port>587</port>
      <socketType>STARTTLS</socketType>
      <authentication>password-cleartext</authentication>
      <username>%EMAILADDRESS%</username>
    </outgoingServer>
  </emailProvider>
</clientConfig>
```

**XML Parsing Logic:**
- Extract IMAP: `incomingServer[@type="imap"]` → hostname, port, socketType
- Extract SMTP: `outgoingServer[@type="smtp"]` → hostname, port, socketType
- Map socketType: "SSL" → imap_ssl=True, "STARTTLS" → smtp_starttls=True, "plain" → False
- Ignore `<username>` field: MVP rule is username = email (always, hardcoded)

**Async HTTP Client Pattern (httpx) - No Caching:**

```python
# core/provider_detector.py
import httpx
from typing import Optional

# Module-level HTTP client (reuse connection pool)
_http_client: Optional[httpx.AsyncClient] = None

def _get_httpx_client() -> httpx.AsyncClient:
    """Get or create httpx client with Mail Reactor configuration."""
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(
            timeout=5.0,  # 5-second timeout (NFR-P1: don't block startup)
            headers={"User-Agent": "MailReactor/0.1.0"},  # Identify ourselves
        )
    return _http_client

async def detect_via_mozilla_autoconfig(domain: str) -> Optional[ProviderConfig]:
    """Query Mozilla Autoconfig for provider settings (no caching, fresh lookup)."""
    
    # Try Mozilla Autoconfig (HTTPS)
    mozilla_url = f"https://autoconfig.thunderbird.net/v1.1/{domain}"
    logger.info("mozilla_autoconfig_lookup", domain=domain, source="mozilla")
    
    try:
        client = _get_httpx_client()
        response = await client.get(mozilla_url)
        if response.status_code == 200:
            config = _parse_autoconfig_xml(response.text)
            if config:
                logger.info("mozilla_autoconfig_success", domain=domain, imap_host=config.imap_host)
                return config
    except (httpx.TimeoutException, httpx.RequestError) as e:
        logger.debug("mozilla_autoconfig_error", domain=domain, error=str(e), source="mozilla")
    
    # Try ISP fallback (HTTP - per Mozilla spec)
    isp_url = f"http://autoconfig.{domain}/mail/config-v1.1.xml"
    logger.info("mozilla_autoconfig_lookup", domain=domain, source="isp")
    
    try:
        client = _get_httpx_client()
        response = await client.get(isp_url)
        if response.status_code == 200:
            config = _parse_autoconfig_xml(response.text)
            if config:
                logger.info("mozilla_autoconfig_success", domain=domain, imap_host=config.imap_host, source="isp")
                return config
    except (httpx.TimeoutException, httpx.RequestError) as e:
        logger.debug("mozilla_autoconfig_error", domain=domain, error=str(e), source="isp")
    
    # All sources failed
    logger.info("mozilla_autoconfig_failed", domain=domain)
    return None
```

[Source: docs/sprint-artifacts/tech-spec-epic-2.md#Mozilla-Autoconfig-External-Service]
[Source: docs/epics.md#Story-2.2-Mozilla-Thunderbird-Autoconfig-Fallback]
[Source: docs/architecture.md#Integration-Points]

### Project Structure Notes

**Modified Files (Story 2.2):**
```
src/mailreactor/
└── core/
    └── provider_detector.py    # MODIFIED: Add async detect_via_mozilla_autoconfig(), update detect_provider() to async
```

**Dependencies:**
- httpx: Add to pyproject.toml (async HTTP client for Mozilla Autoconfig queries)
- xml.etree.ElementTree: Python stdlib (no install needed)
- asyncio: Python stdlib (no install needed)

**Testing Structure:**
```
tests/
├── unit/
│   └── test_provider_detector.py      # MODIFIED: Add tests for Mozilla Autoconfig (XML parsing, network calls)
└── integration/
    └── test_provider_detection_flow.py  # MODIFIED: Add end-to-end Mozilla Autoconfig test
```

**Backward Compatibility:**
- **Breaking Change**: `detect_provider(email)` becomes async → `await detect_provider(email)`
- **Impact**: All call sites must be updated (Story 2.3+ will call async version)
- **Mitigation**: This story adds async, Story 2.3 will integrate into API endpoints

[Source: docs/architecture.md#Project-Structure]
[Source: docs/hc-standards.md#Project-Root-Structure]

### Technical Notes

**Key Implementation Requirements:**

1. **MVP Authentication Rule (Hardcoded):**
   - Username = email address (always, no exceptions in MVP)
   - Password: Same for IMAP and SMTP (unified authentication for Big 4)
   - No username template system, no username flags
   - Simple: When creating IMAPConfig/SMTPConfig, use email as username

2. **Async HTTP Client (httpx):**
   - Module-level singleton: `_http_client` (reuse connection pool)
   - Timeout: 5 seconds (NFR-P1: don't block startup)
   - User-Agent: `MailReactor/{version}` (identify ourselves to Mozilla)
   - Connection pooling: Default httpx behavior (10 max connections)

3. **XML Parsing (xml.etree.ElementTree):**
   - Parse `<incomingServer type="imap">` for IMAP config (hostname, port, socketType)
   - Parse `<outgoingServer type="smtp">` for SMTP config (hostname, port, socketType)
   - Ignore `<username>` field from XML (MVP rule: username = email)
   - Handle missing fields gracefully (return None, don't crash)
   - Validate required fields: hostname, port (socketType optional, default to SSL)

4. **No Caching (MVP Decision):**
   - Fresh lookup on every detection (stateless design)
   - 5-second timeout prevents excessive delay
   - Users re-run CLI command (shell history = easy)
   - Rationale: YAGNI - premature optimization for rare scenario

5. **Detection Cascade:**
   - Step 1: Local providers.yaml (Story 2.1, synchronous)
   - Step 2: Mozilla Autoconfig (Story 2.2, async)
   - Step 3: ISP autoconfig (Story 2.2, async)
   - Step 4: Manual config (Story 2.3, user-provided)

6. **Environment Variables (Password Only - MVP Decision):**
   - `MAILREACTOR_PASSWORD`: Default for both IMAP and SMTP
   - `MAILREACTOR_IMAP_PASSWORD`: Override for IMAP (relay services)
   - `MAILREACTOR_SMTP_PASSWORD`: Override for SMTP (relay services)
   - Resolution: specific override → default → prompt
   - `.env` file auto-loaded by pydantic-settings

7. **Logging:**
   - INFO: Lookup attempts, success/failure
   - DEBUG: Full XML response
   - No sensitive data: Don't log passwords or full emails in public logs (domain only)

8. **Testing:**
   - Unit tests: XML parsing (valid/invalid), network calls (mock httpx)
   - Integration test: Full cascade (local → Mozilla → ISP → None)
   - Coverage: Aim for 100% on new functions (`detect_via_mozilla_autoconfig`, `_parse_autoconfig_xml`)

**XML Parsing Example:**

```python
# core/provider_detector.py
import xml.etree.ElementTree as ET

def _parse_autoconfig_xml(xml_content: str) -> Optional[ProviderConfig]:
    """Parse Mozilla Autoconfig XML response."""
    try:
        root = ET.fromstring(xml_content)
        
        # Extract IMAP settings
        imap_server = root.find(".//incomingServer[@type='imap']")
        if imap_server is None:
            logger.debug("autoconfig_parse_failed", reason="no_imap_server")
            return None
        
        imap_host = imap_server.findtext("hostname")
        imap_port = imap_server.findtext("port")
        imap_socket = imap_server.findtext("socketType", default="SSL")
        
        if not imap_host or not imap_port:
            logger.debug("autoconfig_parse_failed", reason="missing_imap_fields")
            return None
        
        # Extract SMTP settings
        smtp_server = root.find(".//outgoingServer[@type='smtp']")
        if smtp_server is None:
            logger.debug("autoconfig_parse_failed", reason="no_smtp_server")
            return None
        
        smtp_host = smtp_server.findtext("hostname")
        smtp_port = smtp_server.findtext("port")
        smtp_socket = smtp_server.findtext("socketType", default="STARTTLS")
        
        if not smtp_host or not smtp_port:
            logger.debug("autoconfig_parse_failed", reason="missing_smtp_fields")
            return None
        
        # Create ProviderConfig (username ignored - MVP rule: username = email)
        config = ProviderConfig(
            provider_name=root.find(".//emailProvider").get("id"),  # domain
            imap_host=imap_host,
            imap_port=int(imap_port),
            imap_ssl=(imap_socket.upper() == "SSL"),
            smtp_host=smtp_host,
            smtp_port=int(smtp_port),
            smtp_starttls=(smtp_socket.upper() == "STARTTLS"),
        )
        
        logger.debug("autoconfig_parse_success", imap_host=imap_host, smtp_host=smtp_host)
        return config
    
    except ET.ParseError as e:
        logger.debug("autoconfig_parse_error", error=str(e))
        return None
    except (KeyError, ValueError, AttributeError) as e:
        logger.debug("autoconfig_parse_error", error=str(e))
        return None
```

**Testing Approach:**

Per team constraint: "✅ ONLY test functionality WE have added"

Unit tests:
- ✅ Test XML parsing logic (our code)
- ✅ Test network call handling (our code)
- ✅ Test cache behavior (our code)
- ❌ Don't test httpx library (httpx's responsibility)
- ❌ Don't test xml.etree (Python stdlib's responsibility)

Integration test:
- ✅ Test full cascade: local → Mozilla → ISP → None
- ✅ Verify cache improves performance (second call faster)
- ❌ Don't test actual Mozilla Autoconfig service (mock httpx responses)

**Common Pitfalls to Avoid:**

1. **Blocking I/O**: Must use async/await for network calls (httpx.AsyncClient)
2. **Timeout**: 5-second timeout prevents indefinite hangs
3. **Cache Races**: Use asyncio.Lock to protect cache dict
4. **XML Errors**: Handle malformed XML gracefully (return None, don't crash)
5. **ISP HTTP**: ISP autoconfig uses HTTP, not HTTPS (by spec, acceptable risk)

**FR Coverage:**

This story implements:
- FR-001: Auto-detect IMAP/SMTP settings (extended coverage to 1000s of providers via Mozilla)

Not yet implemented (future stories):
- FR-007: Manual override (Story 2.3)
- FR-008: Validation with clear errors (Story 2.4)

**Related Stories:**
- Story 2.1: Local provider detection (prerequisite)
- Story 2.3: Manual configuration override (next story)
- Story 2.4: Connection validation (uses detected settings)

[Source: docs/sprint-artifacts/tech-spec-epic-2.md#AC-2.2-Mozilla-Autoconfig-Fallback]
[Source: docs/epics.md#Story-2.2-Mozilla-Thunderbird-Autoconfig-Fallback]
[Source: docs/architecture.md#Dependencies-and-Integrations]

### References

- **Tech Spec**: [Source: docs/sprint-artifacts/tech-spec-epic-2.md#Story-2.2]
- **Epic Breakdown**: [Source: docs/epics.md#Epic-2-Email-Account-Connection]
- **Architecture**: [Source: docs/architecture.md#Integration-Points]
- **Mozilla Autoconfig Spec**: https://wiki.mozilla.org/Thunderbird:Autoconfiguration
- **httpx Documentation**: https://www.python-httpx.org/async/
- **Python xml.etree.ElementTree**: https://docs.python.org/3/library/xml.etree.elementtree.html
- **Previous Story**: [Source: docs/sprint-artifacts/2-1-provider-configuration-and-basic-auto-detection.md]
- **Team Standards**: [Source: docs/hc-standards.md]
- **Testing Patterns**: [Source: docs/tdd-guide.md], [Source: docs/test-design-system.md]
- **Development Practices**: [Source: docs/development-practices.md]

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

## Change Log

**2025-12-05:** Story 2.2 drafted by SM agent (Bob) via create-story workflow (YOLO mode)
- Extracted requirements from Epic 2 Story 2.2 (epics.md lines 617-672)
- Incorporated learnings from Story 2.1 (caching pattern, behavior-focused testing, file locations)
- Key deliverables: Mozilla Autoconfig network client, XML parsing, ISP fallback, in-memory cache
- Detection cascade: local providers.yaml → Mozilla Autoconfig → ISP autoconfig → None
- Breaking change: `detect_provider()` becomes async (requires await)
- Testing: Unit tests for XML parsing and network calls (mock httpx), integration for full cascade
- Status: drafted, ready for validation

**2025-12-05:** Story 2.2 updated by SM agent (Bob) after party-mode architectural decisions (first update)
- **REMOVED:** Caching (AC3, Task 4, AutoconfigCache class) - YAGNI for stateless MVP
- **ADDED:** Username pattern support to ProviderConfig model (imap/smtp_username_pattern fields)
- **ADDED:** Username pattern updates to providers.yaml for Big 4 (extends Story 2.1 files)
- **ADDED:** Username parsing from Mozilla Autoconfig XML (%EMAILADDRESS% → {email})
- **ADDED:** Product decisions section documenting Big 4 authentication rule (username=email, same password forever)
- **ADDED:** Credential strategy: env vars for passwords only (MAILREACTOR_PASSWORD + overrides), .env file support
- **ADDED:** CLI flag strategy: all config via flags except passwords (security)
- **RATIONALE:** Party-mode session 2025-12-05 with HC + team - architectural alignment on stateless MVP, credential handling
- Detection remains: local → Mozilla → ISP → None (no caching)
- Story now includes Story 2.1.1 scope (username patterns) - no separate story needed
- Status: drafted, updated, ready for validation

**2025-12-05:** Story 2.2 updated by SM agent (Bob) after party-mode architectural decisions (second update)
- **REMOVED:** Username pattern functionality entirely - YAGNI for MVP
- **REMOVED:** Username pattern fields from ProviderConfig model (imap/smtp_username_pattern)
- **REMOVED:** Username pattern updates to providers.yaml
- **REMOVED:** Username parsing from Mozilla Autoconfig XML
- **REMOVED:** All username pattern tasks and tests
- **SIMPLIFIED:** MVP rule hardcoded: username = email (always, no exceptions, no templates)
- **SIMPLIFIED:** No `--username` CLI flags in MVP
- **RATIONALE:** HC decision - username pattern system unnecessary when email works for all cases
- XML parsing now ignores `<username>` field completely
- Detection remains: local → Mozilla → ISP → None (no caching)
- Status: drafted, updated, ready for validation and context generation
