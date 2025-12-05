# Story 2.1: Provider Configuration and Basic Auto-Detection

Status: drafted

## Story

As a developer,
I want Mail Reactor to auto-detect IMAP/SMTP settings for major email providers,
so that I don't have to manually look up server configurations.

## Acceptance Criteria

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
- `ProviderConfig` model with imap/smtp connection details (auto-detection results)
- `IMAPConfig` model with IMAP server configuration and credentials
- `SMTPConfig` model with SMTP server configuration and credentials
- `AccountCredentials` model combining email, IMAP config, and SMTP config

**And** Domain extraction handles common patterns:
- `user@gmail.com` → gmail provider
- `user@mycompany.com` → None (unknown, will trigger Mozilla fallback)
- `user@outlook.com` or `user@hotmail.com` → outlook provider

**Prerequisites:** Story 1.2 (Pydantic models), Story 1.3 (logging)

## Tasks / Subtasks

- [ ] Create provider configuration file (AC: providers.yaml with 4+ major providers)
  - [ ] Create `src/mailreactor/utils/providers.yaml` file
  - [ ] Add Gmail configuration: imap.gmail.com:993 SSL, smtp.gmail.com:587 STARTTLS
  - [ ] Add Outlook/Office365: outlook.office365.com:993 SSL, smtp.office365.com:587 STARTTLS
  - [ ] Add Yahoo Mail: imap.mail.yahoo.com:993 SSL, smtp.mail.yahoo.com:587 STARTTLS
  - [ ] Add iCloud: imap.mail.me.com:993 SSL, smtp.mail.me.com:587 STARTTLS
  - [ ] Include domain aliases (e.g., gmail.com, googlemail.com, outlook.com, hotmail.com)
  - [ ] Document YAML schema in comments (provider key, imap/smtp sections, ssl/starttls flags)

- [ ] Create account Pydantic models (AC: ProviderConfig, IMAPConfig, SMTPConfig, AccountCredentials)
  - [ ] Create `src/mailreactor/models/account.py` module
  - [ ] Define `ProviderConfig` model: provider_name, imap_host, imap_port, imap_ssl, smtp_host, smtp_port, smtp_starttls
  - [ ] Define `IMAPConfig` model: host, port, ssl, username, password (Field exclude=True)
  - [ ] Define `SMTPConfig` model: host, port, starttls, username, password (Field exclude=True)
  - [ ] Define `AccountCredentials` model: account_id, email, imap (IMAPConfig), smtp (SMTPConfig), created_at, connection_status
  - [ ] Add field validators: email (EmailStr), ports (1-65535), hosts (non-empty)
  - [ ] Add docstrings for OpenAPI documentation generation

- [ ] Implement provider detector (AC: detect_provider function, domain extraction)
  - [ ] Create `src/mailreactor/core/provider_detector.py` module
  - [ ] Implement `load_providers() -> Dict[str, ProviderConfig]`: load YAML, parse into Pydantic models
  - [ ] Implement `extract_domain(email: str) -> str`: split on '@', lowercase, validate format
  - [ ] Implement `detect_provider(email: str) -> Optional[ProviderConfig]`: domain → provider lookup
  - [ ] Handle provider aliases (e.g., hotmail.com → outlook, googlemail.com → gmail)
  - [ ] Return None if domain not found (graceful fallback for unknown providers)
  - [ ] Cache loaded providers in module-level variable (load once at import)

- [ ] Add structured logging for provider detection (AC: INFO logs for detection success/failure)
  - [ ] Log provider detection attempts: `logger.info("detecting_provider", email=email, domain=domain)`
  - [ ] Log successful detection: `logger.info("provider_detected", domain=domain, provider=provider_key)`
  - [ ] Log unknown provider: `logger.info("provider_unknown", domain=domain, message="Not in local providers.yaml")`
  - [ ] Include provider settings in debug logs: `logger.debug("provider_config", imap_host=config.imap_host, smtp_host=config.smtp_host)`

- [ ] Write unit tests for provider detection (AC: test all major providers, unknown domains)
  - [ ] Test `load_providers()`: verify YAML parsing, Pydantic model creation
  - [ ] Test `extract_domain()`: valid emails, invalid formats, edge cases
  - [ ] Test `detect_provider()` for Gmail: user@gmail.com → gmail provider config
  - [ ] Test `detect_provider()` for Outlook: user@outlook.com, user@hotmail.com → outlook provider
  - [ ] Test `detect_provider()` for Yahoo: user@yahoo.com → yahoo provider
  - [ ] Test `detect_provider()` for iCloud: user@icloud.com, user@me.com → icloud provider
  - [ ] Test unknown domain: user@custom.com → None (not in providers.yaml)
  - [ ] Test provider aliases: googlemail.com → gmail, hotmail.co.uk → outlook
  - [ ] Coverage target: 100% for provider_detector.py (small, critical module)

- [ ] Write integration test for end-to-end provider detection (AC: YAML load → detect → return config)
  - [ ] Test full flow: email → detect_provider → ProviderConfig with correct settings
  - [ ] Verify providers.yaml loads successfully at module import
  - [ ] Verify all 4 major providers can be detected
  - [ ] Test case-insensitivity: User@Gmail.COM → gmail provider
  - [ ] Test invalid email formats handled gracefully (return None or raise validation error)

## Dev Notes

### Learnings from Previous Story

**From Story 1-8-development-mode-with-hot-reload (Status: done)**

- **DRY Refactoring Pattern**: Extract shared logic into helper functions (e.g., `_run_server()`) to avoid duplication
- **CLI Pattern**: Typer commands with shared options, different defaults per use case
- **Factory Pattern**: Uvicorn requires import string ("module:callable") for reload, not app instance
- **Documentation Quality**: Comprehensive guides with examples, clear sections
- **Test Strategy**: Unit tests for function signatures/config, integration for end-to-end flows
- **File Organization**: Group related functions in same module, keep modules focused

**Applying to Story 2.1:**
- Follow DRY: If loading YAML is repeated, extract `load_yaml_config()` helper
- Module organization: Keep provider detection logic in `core/`, models in `models/`, config in `utils/`
- Documentation: Add docstrings to all public functions for OpenAPI generation
- Testing: Unit tests for parsing/matching logic, integration for full detection flow

[Source: stories/1-8-development-mode-with-hot-reload.md#Dev-Agent-Record]

### Architecture Patterns and Constraints

**Provider Auto-Detection (from Architecture):**

Architecture document (section "Provider Auto-Detection") defines the YAML-based provider configuration approach:

**YAML Structure (providers.yaml):**
```yaml
gmail:
  imap:
    host: imap.gmail.com
    port: 993
    ssl: true
  smtp:
    host: smtp.gmail.com
    port: 587
    starttls: true

outlook:
  imap:
    host: outlook.office365.com
    port: 993
    ssl: true
  smtp:
    host: smtp.office365.com
    port: 587
    starttls: true
```

**Detection Strategy:**
1. Extract domain from email address (split on '@', lowercase)
2. Look up domain in providers.yaml (exact match or alias)
3. If found, return ProviderConfig with imap/smtp settings
4. If not found, return None (Story 2.2 will add Mozilla Autoconfig fallback)

**Provider Aliases:**
- Gmail: gmail.com, googlemail.com
- Outlook: outlook.com, hotmail.com, live.com, msn.com
- Yahoo: yahoo.com, yahoo.co.uk, ymail.com
- iCloud: icloud.com, me.com, mac.com

**Pydantic Model Pattern (from Architecture):**

All data models use Pydantic for validation and serialization:

```python
# models/account.py
from pydantic import BaseModel, Field, EmailStr

class ProviderConfig(BaseModel):
    """Email provider IMAP/SMTP configuration."""
    imap_host: str
    imap_port: int = 993
    imap_ssl: bool = True
    smtp_host: str
    smtp_port: int = 587
    smtp_starttls: bool = True

class AccountCredentials(BaseModel):
    """Account credentials for IMAP/SMTP access."""
    email: EmailStr
    password: str = Field(..., exclude=True)  # Never serialize
    imap_host: str
    imap_port: int = 993
    imap_ssl: bool = True
    smtp_host: str
    smtp_port: int = 587
    smtp_starttls: bool = True
```

**Logging Pattern (from Story 1.3):**

Use structlog for structured logging with context:

```python
# core/provider_detector.py
import structlog

logger = structlog.get_logger(__name__)

def detect_provider(email: str) -> Optional[ProviderConfig]:
    domain = extract_domain(email)
    logger.info("detecting_provider", email=email, domain=domain)
    
    config = _lookup_provider(domain)
    if config:
        logger.info("provider_detected", domain=domain, provider=config.name)
    else:
        logger.info("provider_unknown", domain=domain)
    
    return config
```

[Source: docs/architecture.md#Provider-Auto-Detection]
[Source: docs/architecture.md#Data-Validation-Pydantic]
[Source: docs/sprint-artifacts/1-3-structured-logging-with-console-and-json-renderers.md]

### Project Structure Notes

**New Files (Story 2.1):**
```
src/mailreactor/
├── models/
│   └── account.py              # NEW: Pydantic models (ProviderConfig, IMAPConfig, SMTPConfig, AccountCredentials)
├── core/
│   └── provider_detector.py    # NEW: Provider detection logic (detect_provider, extract_domain)
└── utils/
    └── providers.yaml          # NEW: Provider configuration (Gmail, Outlook, Yahoo, iCloud)
```

**Modified Files:**
None (this story creates new modules, doesn't modify existing code)

**Dependencies:**
- PyYAML: For loading providers.yaml (add to pyproject.toml if not already present)
- Pydantic: Already installed (Story 1.2), used for models
- structlog: Already installed (Story 1.3), used for logging

**Testing Structure:**
```
tests/
├── unit/
│   ├── test_provider_detector.py   # NEW: Unit tests for detection logic
│   └── test_account_models.py      # NEW: Unit tests for Pydantic models
└── integration/
    └── test_provider_detection_flow.py  # NEW: End-to-end detection test
```

[Source: docs/architecture.md#Project-Structure]
[Source: docs/hc-standards.md#Project-Root-Structure]

### Technical Notes

**Key Implementation Requirements:**

1. **YAML Configuration File:**
   - Location: `src/mailreactor/utils/providers.yaml`
   - Format: Provider key → imap/smtp sections
   - Include common domain aliases for each provider
   - Document schema in YAML comments

2. **Pydantic Models:**
   - `ProviderConfig`: Auto-detected server settings (provider_name, imap/smtp host/port/ssl)
   - `IMAPConfig`: IMAP server configuration and credentials (host, port, ssl, username, password)
   - `SMTPConfig`: SMTP server configuration and credentials (host, port, starttls, username, password)
   - `AccountCredentials`: Complete account (account_id, email, IMAPConfig, SMTPConfig, timestamps)
   - Use `Field(exclude=True)` for password fields (never serialize)

3. **Provider Detection Logic:**
   - Extract domain: `email.split('@')[1].lower()`
   - Handle email validation: Use Pydantic EmailStr
   - Provider lookup: Simple dictionary key lookup
   - Alias handling: Map aliases to canonical provider keys
   - Graceful None return: Unknown domains don't raise exceptions

4. **Logging:**
   - INFO level: Detection attempts, success/failure
   - DEBUG level: Extracted domain, matched provider, settings
   - No sensitive data: Don't log passwords

5. **Testing:**
   - Unit tests: Each function isolated (extract_domain, load_providers, detect_provider)
   - Integration test: Full flow from email → ProviderConfig
   - Coverage: Aim for 100% on provider_detector.py (critical, small module)
   - Test data: Use sample email addresses (user@gmail.com, etc.)

**YAML Loading Pattern:**

```python
# core/provider_detector.py
import yaml
from pathlib import Path
from typing import Dict, Optional

# Module-level cache (load once at import)
_PROVIDERS_CACHE: Optional[Dict[str, ProviderConfig]] = None

def load_providers() -> Dict[str, ProviderConfig]:
    """Load provider configurations from YAML file."""
    global _PROVIDERS_CACHE
    
    if _PROVIDERS_CACHE is not None:
        return _PROVIDERS_CACHE
    
    providers_path = Path(__file__).parent.parent / "utils" / "providers.yaml"
    with open(providers_path, "r") as f:
        data = yaml.safe_load(f)
    
    # Parse YAML into Pydantic models
    providers = {}
    for provider_key, config_data in data.items():
        providers[provider_key] = ProviderConfig(
            imap_host=config_data["imap"]["host"],
            imap_port=config_data["imap"]["port"],
            imap_ssl=config_data["imap"]["ssl"],
            smtp_host=config_data["smtp"]["host"],
            smtp_port=config_data["smtp"]["port"],
            smtp_starttls=config_data["smtp"]["starttls"],
        )
    
    _PROVIDERS_CACHE = providers
    return providers
```

**Domain Aliases Pattern:**

```python
# core/provider_detector.py
PROVIDER_ALIASES = {
    "googlemail.com": "gmail",
    "hotmail.com": "outlook",
    "live.com": "outlook",
    "msn.com": "outlook",
    "me.com": "icloud",
    "mac.com": "icloud",
}

def detect_provider(email: str) -> Optional[ProviderConfig]:
    domain = extract_domain(email)
    
    # Try direct lookup
    providers = load_providers()
    if domain in providers:
        return providers[domain]
    
    # Try alias lookup
    canonical = PROVIDER_ALIASES.get(domain)
    if canonical and canonical in providers:
        return providers[canonical]
    
    return None
```

**Testing Approach:**

Per team constraint: "✅ ONLY test functionality WE have added"

Unit tests:
- ✅ Test YAML parsing (our providers.yaml → Pydantic models)
- ✅ Test domain extraction (our logic)
- ✅ Test provider lookup (our dictionary matching)
- ❌ Don't test Pydantic validation (Pydantic's responsibility)
- ❌ Don't test YAML library (PyYAML's responsibility)

Integration test:
- ✅ Test full detection flow: email → detect_provider → ProviderConfig
- ✅ Verify all 4 major providers in providers.yaml work end-to-end
- ❌ Don't test actual IMAP/SMTP connections (that's Story 2.4)

**Common Pitfalls to Avoid:**

1. **Case Sensitivity**: Always lowercase domain before lookup
2. **Email Validation**: Use Pydantic EmailStr, don't roll custom regex
3. **YAML Loading**: Load once at module import, not on every detection call
4. **Error Handling**: Return None for unknown providers (graceful), don't raise exceptions
5. **Password Security**: Use `Field(exclude=True)` to prevent serialization

**FR Coverage:**

This story implements:
- FR-001: Auto-detect IMAP/SMTP settings for common providers (Gmail, Outlook, Yahoo, iCloud)

Not yet implemented (future stories):
- FR-002: Add account via CLI (Story 2.7)
- FR-003: Add account via REST API (Story 2.3)
- FR-007: Manual override (Story 2.3)

**Related Stories:**
- Story 2.2: Mozilla Thunderbird Autoconfig fallback (extends detection to 1000s of providers)
- Story 2.3: Manual configuration override (when auto-detection fails)
- Story 2.4: Account connection validation (tests detected settings actually work)

[Source: docs/sprint-artifacts/tech-spec-epic-2.md#AC-2.1-Local-Provider-Auto-Detection]
[Source: docs/epics.md#Story-2.1-Provider-Configuration-and-Basic-Auto-Detection]
[Source: docs/architecture.md#Provider-Auto-Detection]
[Source: docs/architecture.md#Technology-Stack-Details]

### References

- **Tech Spec**: [Source: docs/sprint-artifacts/tech-spec-epic-2.md#Story-2.1]
- **Epic Breakdown**: [Source: docs/epics.md#Epic-2-Email-Account-Connection]
- **Architecture**: [Source: docs/architecture.md#Provider-Auto-Detection]
- **Pydantic Models**: [Source: docs/architecture.md#Data-Validation-Pydantic]
- **Logging Pattern**: [Source: docs/sprint-artifacts/1-3-structured-logging-with-console-and-json-renderers.md]
- **Previous Story**: [Source: docs/sprint-artifacts/1-8-development-mode-with-hot-reload.md]
- **Team Standards**: [Source: docs/hc-standards.md]
- **Testing Patterns**: [Source: docs/tdd-guide.md], [Source: docs/test-design-system.md]
- **Development Practices**: [Source: docs/development-practices.md]
- **PyYAML Documentation**: https://pyyaml.org/wiki/PyYAMLDocumentation
- **Pydantic EmailStr**: https://docs.pydantic.dev/latest/api/networks/#pydantic.networks.EmailStr

## Dev Agent Record

### Context Reference

- `docs/sprint-artifacts/2-1-provider-configuration-and-basic-auto-detection.context.xml`

### Agent Model Used

claude-3-7-sonnet-20250219

### Debug Log References

### Completion Notes List

### File List

## Change Log

**2025-12-05:** Story 2.1 drafted by SM agent (Bob) via create-story workflow (YOLO mode)
- Extracted requirements from Epic 2 Story 2.1 (epics.md lines 569-614)
- Incorporated learnings from Story 1.8 (DRY refactoring, helper functions, documentation quality)
- Key deliverables: providers.yaml (4+ major providers), provider_detector.py (detection logic), account.py (Pydantic models)
- Detection strategy: domain extraction → YAML lookup → alias fallback → None for unknown
- Testing: Unit tests for detection logic, integration for full flow, coverage target 100%
- Status: drafted, ready for context generation and dev assignment

**2025-12-05:** Story validated and improved by SM agent (Bob) via validate-create-story workflow
- Added tech spec citation to References section (tech-spec-epic-2.md)
- Added testing patterns references (tdd-guide.md, test-design-system.md)
- Added development practices reference for consistency
- Verified all source documents cited
- **Fixed model alignment**: Corrected AC to match tech spec (removed AccountConfig, added IMAPConfig/SMTPConfig)
- Updated tasks to reflect correct model structure from tech spec
- Validation result: PASS with improvements applied
- Status: drafted, enhanced with complete source coverage and tech spec alignment
