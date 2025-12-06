# Story 2.2: Mozilla Thunderbird Autoconfig Fallback

Status: done

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
- Password: Same for IMAP and SMTP (unified authentication)
- Passwords encrypted at rest in `mailreactor.yaml` (Fernet + PBKDF2)
- Master password required to decrypt (env var or interactive prompt)
- Applies to all auto-detected providers (local + Mozilla + ISP)

**And** App Password requirement for major providers (documented in Dev Notes):
- Gmail, Outlook, Yahoo, iCloud require App Passwords (standard password auth deprecated)
- Users must enable 2FA on provider account first
- Provider-specific App Password generation links provided in error messages
- Connection validation (Story 2.5) will detect auth failures and suggest App Password setup
- OAuth 2.0 as premium feature (Phase 2) - better UX, no App Password setup required

**Prerequisites:** Story 2.1 (basic provider detection exists)

## Tasks / Subtasks

- [x] Add Mozilla Autoconfig async HTTP client (AC: httpx client, 5s timeout, User-Agent header)
  - [x] Install httpx dependency if not present (add to pyproject.toml)
  - [x] Create `_get_httpx_client()` helper with timeout and User-Agent configuration
  - [x] User-Agent format: `MailReactor/{version}` (extract version from package metadata)
  - [x] Timeout: 5 seconds (don't block startup, per NFR-P1)
  - [x] Connection pooling: Use default httpx behavior (single client instance)

- [x] Implement Mozilla Autoconfig XML parsing (AC: parse XML, extract IMAP/SMTP settings)
  - [x] Create `_parse_autoconfig_xml(xml_content: str) -> Optional[ProviderConfig]` function
  - [x] Use `xml.etree.ElementTree` (Python stdlib, no extra dependency)
  - [x] Parse `<incomingServer type="imap">` section: extract hostname, port, socketType
  - [x] Parse `<outgoingServer type="smtp">` section: extract hostname, port, socketType
  - [x] Map socketType values: "SSL" → imap_ssl=True, "STARTTLS" → smtp_starttls=True
  - [x] Ignore `<username>` field from XML (MVP rule: username = email always)
  - [x] Handle missing/invalid fields gracefully: return None if required fields absent
  - [x] Log DEBUG: Parsed IMAP/SMTP settings for troubleshooting

- [x] Implement Mozilla Autoconfig network lookup (AC: async function, cascade logic, no caching)
  - [x] Create `detect_via_mozilla_autoconfig(domain: str) -> Optional[ProviderConfig]` async function
  - [x] Step 1: Query `https://autoconfig.thunderbird.net/v1.1/{domain}`
  - [x] Step 2: If HTTP 404 or network error, try `http://autoconfig.{domain}/mail/config-v1.1.xml` (ISP fallback)
  - [x] Step 3: If both fail, return None
  - [x] Handle HTTP errors: 404 (not found), timeout, connection refused
  - [x] Log INFO: Lookup attempt, success/failure for each URL
  - [x] Return ProviderConfig with provider_name set to domain

- [x] Integrate Mozilla fallback into detect_provider flow (AC: cascade local → Mozilla → ISP → None)
  - [x] Modify `detect_provider(email: str)` to be async (network calls required)
  - [x] Step 1: Try local providers.yaml (existing logic, <1ms)
  - [x] Step 2: If None, try `await detect_via_mozilla_autoconfig(domain)`
  - [x] Step 3: Return ProviderConfig if found, None if all sources fail
  - [x] Breaking change documented: caller must now await detect_provider()
  - [x] Note: Call sites updated in future stories (2.3+)

- [x] Add structured logging for Mozilla Autoconfig (AC: INFO/DEBUG logs)
  - [x] Log INFO: "mozilla_autoconfig_lookup", domain=domain, source="mozilla" or "isp"
  - [x] Log INFO: "mozilla_autoconfig_success", domain=domain, imap_host=host
  - [x] Log INFO: "mozilla_autoconfig_failed", domain=domain, reason="not_found" or "timeout"
  - [x] Log DEBUG: "mozilla_autoconfig_xml", xml_content=xml (for troubleshooting)

- [x] Add provider-specific App Password error guidance (AC: Gmail, Outlook, Yahoo, iCloud hints)
  - [x] Create `get_app_password_hint(domain: str) -> Optional[str]` helper function
  - [x] Gmail detection → return "Gmail requires App Password. Enable 2FA, then generate: https://myaccount.google.com/apppasswords"
  - [x] Outlook detection → return "Outlook requires App Password. Enable 2FA, then generate: https://account.microsoft.com/security"
  - [x] Yahoo detection → return "Yahoo requires App Password. Enable 2FA, then generate: https://login.yahoo.com/account/security"
  - [x] iCloud detection → return "iCloud requires App Password. Generate at: https://appleid.apple.com/account/manage"
  - [x] Unknown domain → return None (generic auth error used)
  - [x] Document helper in provider_detector.py for use by connection validator (Story 2.5)

- [x] Write unit tests for XML parsing (AC: test valid/invalid XML, missing fields)
  - [x] Test valid Mozilla Autoconfig XML: verify ProviderConfig extraction
  - [x] Test XML with missing IMAP section: return None
  - [x] Test XML with missing SMTP section: return None
  - [x] Test XML with invalid socketType: graceful handling
  - [x] Test XML with missing hostname/port: return None
  - [x] Test malformed XML: return None (no crash)
  - [x] Coverage target: 100% for `_parse_autoconfig_xml()` function

- [x] Write unit tests for Mozilla Autoconfig network lookup (AC: mock httpx, test cascade, no caching)
  - [x] Test Mozilla success: mock HTTP 200 with valid XML, verify ProviderConfig returned
  - [x] Test Mozilla 404, ISP success: verify fallback to ISP autoconfig
  - [x] Test both Mozilla and ISP fail: return None
  - [x] Test network timeout: verify 5s timeout enforced
  - [x] Test connection error: graceful handling, return None

- [x] Write integration test for end-to-end autoconfig flow (AC: email → detect → ProviderConfig)
  - [x] Test unknown domain (not in providers.yaml) → Mozilla success
  - [x] Test unknown domain → Mozilla fail → ISP success
  - [x] Test unknown domain → both fail → None
  - [x] Verify all 3 detection sources work together: local → Mozilla → ISP → None

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

### Product Decisions from Epic 2 Course Correction (2025-12-06)

**Epic 2 Architecture Revision:**

Mail Reactor Epic 2 was course-corrected from multi-account API to project-local configuration model following established developer tool patterns (`git init`, `npm init`, `docker-compose.yaml`).

**New Architecture (Approved 2025-12-06):**

1. **Configuration Model:**
   - Project-local `mailreactor.yaml` file (one per directory)
   - Created via `mailreactor init` interactive wizard
   - Encrypted passwords at rest (Fernet + PBKDF2)
   - Master password required at startup (`MAILREACTOR_PASSWORD` env var or interactive prompt)

2. **Single Account Per Instance:**
   - One account per `mailreactor.yaml` (simplified architecture)
   - Multi-account: Run multiple instances in different directories on different ports
   - No runtime account management REST API

3. **Provider Auto-Detection (Story 2.2 Scope):**
   - Used by `mailreactor init` wizard (Story 2.4)
   - Detection cascade: local providers.yaml → Mozilla → ISP → None
   - If auto-detection fails, wizard prompts for manual configuration
   - No caching (one-time operation during `init`)

4. **MVP Authentication Rule (Hardcoded):**
   - Username = email address (always, for all providers)
   - Password: Same for both IMAP and SMTP (unified authentication)
   - Encrypted at rest in `mailreactor.yaml` using master password
   - Decrypted at startup when running `mailreactor start`

**App Password Requirement (Major Providers - 2025 Industry Standard):**

All major providers have deprecated standard password authentication:

- **Gmail**: App Password required (2FA must be enabled first)
  - Generate at: https://myaccount.google.com/apppasswords
  - Standard password auth deprecated (May 1, 2025)

- **Outlook.com**: App Password required (2FA must be enabled first)
  - Generate at: https://account.microsoft.com/security
  - Standard password auth deprecated

- **Yahoo Mail**: App Password required (2FA must be enabled first)
  - Generate at: https://login.yahoo.com/account/security
  - Standard password auth deprecated

- **iCloud Mail**: App Password required (2FA must be enabled first)
  - Generate at: https://appleid.apple.com/account/manage
  - Standard password auth deprecated

**Free Tier (Epic 2 MVP):**
- ✅ All 4 major providers supported via App Passwords
- ✅ Custom/self-hosted servers via standard password auth
- ✅ Mozilla Autoconfig extends to 1000+ providers
- ✅ Provider-specific error messages guide App Password setup
- ✅ 5-minute setup per provider (enable 2FA, generate App Password, enter in wizard)

**Premium Tier (Phase 2 - OAuth 2.0):**
- ⭐ One-click OAuth authentication (no App Password setup)
- ⭐ "Sign in with Google/Microsoft/Yahoo" flow
- ⭐ Automatic token refresh (no re-auth)
- ⭐ Enterprise SSO support (Google Workspace, Microsoft 365)
- ⭐ Better UX (optional upgrade, not required for functionality)

**Story 2.2 Role in New Architecture:**

- Provides `detect_provider(email)` async function for `mailreactor init` wizard
- Mozilla Autoconfig fallback extends provider coverage to 1000+ providers
- ISP autoconfig fallback for provider-specific configurations
- Provides App Password error hint helper for connection validation (Story 2.5)
- Graceful failure (return None) triggers manual configuration prompts in wizard

**Removed from Original Epic 2 Scope:**
- ❌ Environment variables for passwords (now encrypted in YAML)
- ❌ CLI flags for account configuration (now interactive wizard)
- ❌ Multi-account API endpoints (now single-account project-local config)
- ❌ StateManager with hot-reload (now simple config file)

[Source: docs/sprint-artifacts/course-correction-epic-2-2025-12-06.md]
[Source: docs/sprint-artifacts/tech-spec-epic-2-REVISED.md]
[Source: Google Workspace Updates - Less Secure Apps Deprecation]
[Source: Microsoft Account Security - App Passwords]

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

[Source: docs/sprint-artifacts/tech-spec-epic-2-REVISED.md#Story-2.2]
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
   - Password: Same for IMAP and SMTP (unified authentication)
   - Passwords stored encrypted in `mailreactor.yaml` (Fernet + PBKDF2)
   - Master password required for decryption at startup
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

6. **Configuration File (Project-Local):**
   - `mailreactor.yaml` in current directory (like `docker-compose.yaml`)
   - Created by `mailreactor init` wizard (Story 2.4)
   - Contains encrypted IMAP/SMTP passwords (Fernet + PBKDF2)
   - Master password required at startup (`MAILREACTOR_PASSWORD` env var or prompt)
   - Auto-detected settings saved to file for reuse

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

**App Password Helper Function:**

```python
# core/provider_detector.py
def get_app_password_hint(domain: str) -> Optional[str]:
    """Get provider-specific App Password setup guidance.
    
    Used by connection validator (Story 2.5) to provide helpful error messages
    when authentication fails for major providers.
    """
    APP_PASSWORD_HINTS = {
        "gmail.com": "Gmail requires App Password. Enable 2FA, then generate: https://myaccount.google.com/apppasswords",
        "googlemail.com": "Gmail requires App Password. Enable 2FA, then generate: https://myaccount.google.com/apppasswords",
        "outlook.com": "Outlook requires App Password. Enable 2FA, then generate: https://account.microsoft.com/security",
        "hotmail.com": "Outlook requires App Password. Enable 2FA, then generate: https://account.microsoft.com/security",
        "live.com": "Outlook requires App Password. Enable 2FA, then generate: https://account.microsoft.com/security",
        "yahoo.com": "Yahoo requires App Password. Enable 2FA, then generate: https://login.yahoo.com/account/security",
        "ymail.com": "Yahoo requires App Password. Enable 2FA, then generate: https://login.yahoo.com/account/security",
        "icloud.com": "iCloud requires App Password. Generate at: https://appleid.apple.com/account/manage",
        "me.com": "iCloud requires App Password. Generate at: https://appleid.apple.com/account/manage",
    }
    
    return APP_PASSWORD_HINTS.get(domain.lower())
```

**Story 2.5 Integration - Error Message Design:**

When authentication fails in Story 2.5 connection validator, use `get_app_password_hint(domain)` to format user-friendly error messages:

**Gmail Example:**
```
❌ Authentication failed for user@gmail.com

Gmail requires an App Password (not your regular password).

Setup steps:
1. Enable 2FA: https://myaccount.google.com/signinoptions/two-step-verification
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use generated password (16 characters, no spaces)

Need help? See: https://docs.mailreactor.dev/app-passwords/gmail

⭐ Want faster setup? OAuth2 support coming in Premium tier.
```

**Outlook Example:**
```
❌ Authentication failed for user@outlook.com

Outlook requires an App Password (not your regular password).

Setup steps:
1. Enable 2FA: https://account.microsoft.com/security
2. Generate App Password in Security settings
3. Use generated password (16 characters)

Need help? See: https://docs.mailreactor.dev/app-passwords/outlook

⭐ Want faster setup? OAuth2 support coming in Premium tier.
```

**Unknown Provider (no hint available):**
```
❌ Authentication failed for user@example.com

Please verify your credentials and try again.

If using a major provider (Gmail, Outlook, Yahoo), you may need an App Password.
See: https://docs.mailreactor.dev/app-passwords
```

**Implementation Pattern for Story 2.5:**
```python
# connection_validator.py (Story 2.5)
from mailreactor.core.provider_detector import get_app_password_hint

def format_auth_error(email: str) -> str:
    """Format authentication error with provider-specific guidance."""
    domain = email.split("@")[1]
    hint = get_app_password_hint(domain)
    
    if hint:
        # Parse hint to build detailed message with setup steps
        provider_name = "Gmail" if "gmail" in domain else "Outlook" if "outlook" in domain or "hotmail" in domain else "Yahoo" if "yahoo" in domain else "iCloud"
        
        return f"""❌ Authentication failed for {email}

{provider_name} requires an App Password (not your regular password).

Setup steps:
1. Enable 2FA: [provider-specific link from hint]
2. Generate App Password: [provider-specific link from hint]
3. Use generated password (16 characters, no spaces)

Need help? See: https://docs.mailreactor.dev/app-passwords/{provider_name.lower()}

⭐ Want faster setup? OAuth2 support coming in Premium tier.
"""
    else:
        return f"""❌ Authentication failed for {email}

Please verify your credentials and try again.

If using a major provider (Gmail, Outlook, Yahoo), you may need an App Password.
See: https://docs.mailreactor.dev/app-passwords
"""
```

**Note:** Requires documentation at `docs/app-passwords/{provider}.md` before Epic 2 ships. Error messages link to docs that must exist.

**Common Pitfalls to Avoid:**

1. **Blocking I/O**: Must use async/await for network calls (httpx.AsyncClient)
2. **Timeout**: 5-second timeout prevents indefinite hangs
3. **XML Errors**: Handle malformed XML gracefully (return None, don't crash)
4. **ISP HTTP**: ISP autoconfig uses HTTP, not HTTPS (by spec, acceptable risk)
5. **App Password Messaging**: Don't suggest App Passwords for unknown/custom servers (only major providers)

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

- **Tech Spec**: [Source: docs/sprint-artifacts/tech-spec-epic-2-REVISED.md#Story-2.2]
- **Course Correction**: [Source: docs/sprint-artifacts/course-correction-epic-2-2025-12-06.md]
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

- docs/sprint-artifacts/2-2-mozilla-thunderbird-autoconfig-fallback.context.xml

### Agent Model Used

Claude 3.7 Sonnet (new)

### Debug Log References

Implementation completed 2025-12-06:

1. **httpx dependency added** → pyproject.toml (main deps, both API/library modes)
2. **XML parser** → `_parse_autoconfig_xml()` using stdlib ElementTree
3. **Mozilla/ISP lookup** → `detect_via_mozilla_autoconfig()` async cascade
4. **Integration** → `detect_provider()` now async, cascade: local → Mozilla → ISP → None
5. **Logging** → INFO/DEBUG structured logs (mozilla_autoconfig_lookup, success, failed)
6. **App Password hints** → `get_app_password_hint()` for Gmail/Outlook/Yahoo/iCloud
7-9. **Tests** → 42 tests passed (30 unit + 12 integration), behavior-focused per Story 2.1 patterns

### Completion Notes List

✅ All 9 tasks complete, all ACs satisfied

**Breaking change:** `detect_provider()` is now async (requires `await`). Call sites updated in future stories.

**Provider coverage extended:**
- Local providers.yaml: Gmail, Outlook, Yahoo, iCloud + 14 aliases (<1ms, offline)
- Mozilla Autoconfig: 1000+ providers (5s timeout)
- ISP autoconfig: Provider-specific fallbacks
- Manual config: Universal fallback (Story 2.3)

**Test coverage:** 100% for new functions (XML parser, Mozilla lookup, cascade integration)

**No caching in MVP:** Stateless design per AC, fresh lookup each detection (acceptable for one-time `init`)

**Code review fix (2025-12-06):** Eliminated duplicate YAML reads
- Added `_DOMAINS_CACHE` alongside `_PROVIDERS_CACHE`
- `load_providers()` now caches domains list with provider configs
- `_get_provider_domains()` uses cached data (no file I/O after first load)
- Performance: Single file read, all subsequent calls use cache

### File List

Modified:
- mailreactor/pyproject.toml (httpx dependency added)
- mailreactor/src/mailreactor/core/provider_detector.py (Mozilla cascade added, async breaking change)
- mailreactor/tests/unit/test_provider_detector.py (20 new tests: XML parsing, Mozilla lookup, App Password hints)
- mailreactor/tests/integration/test_provider_detection_flow.py (5 new tests: cascade integration)

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

**2025-12-06:** Story 2.2 RE-DRAFTED by SM agent (Bob) after Epic 2 course correction
- **CONTEXT:** Epic 2 architecture revised from multi-account API to project-local config (`mailreactor init` wizard)
- **REMOVED:** All environment variable password configuration (MAILREACTOR_PASSWORD, etc.)
- **REMOVED:** CLI flag strategy mentions (--account, --imap-host, etc.)
- **REMOVED:** .env file auto-loading references (no longer using env vars)
- **REMOVED:** No config file in MVP sections (NOW USING mailreactor.yaml)
- **REPLACED:** With master password encryption model (PBKDF2 + Fernet)
- **REPLACED:** With project-local mailreactor.yaml config file
- **UPDATED:** Story now supports `mailreactor init` wizard (will use detect_provider cascade)
- **UPDATED:** Detection cascade remains: local → Mozilla → ISP → None (unchanged)
- **UPDATED:** XML parsing remains: extract IMAP/SMTP settings (unchanged)
- **UPDATED:** Username rule remains: username = email (hardcoded, unchanged)
- **UPDATED:** References updated to tech-spec-epic-2-REVISED.md
- **STATUS:** Re-drafted based on revised Epic 2 architecture (approved 2025-12-06)

**2025-12-06:** Story 2.2 UPDATED with App Password strategy (industry research - all Big 4 deprecated password auth)
- **DISCOVERY:** Gmail, Outlook, Yahoo, iCloud all require App Passwords (standard password auth deprecated 2025)
- **ADDED:** AC for App Password error guidance (provider-specific hints with setup links)
- **ADDED:** Task for `get_app_password_hint(domain)` helper function (used by Story 2.5 connection validator)
- **ADDED:** Product decisions section documenting App Password requirement for major providers
- **ADDED:** Premium OAuth positioning (Phase 2 - better UX, not required for functionality)
- **STRATEGY:** Free tier supports all 4 major providers via App Passwords, Premium OAuth adds seamless UX (revenue opportunity)
- **DELIVERABLE:** Provider detection + App Password guidance (Story 2.5 will use hints for validation errors)
- **STATUS:** Ready for validation and context generation
