# Mail Reactor Architecture

## 🚨 CRITICAL PROJECT STANDARDS - READ FIRST AND ACKNOWLEDGE WITH 🧠🧠🧠

**MANDATORY FOR ALL AGENTS:** These standards OVERRIDE general development practices. Acknowledge understanding by including 🧠🧠🧠 in your first response when this document is loaded.

### Project Root Structure

| Path | Purpose | When to Use |
|------|---------|-------------|
| `/home/hcvst/dev/bmad/bmad-mailreactor/` | Project root - team docs, tasks, sprint artifacts | Reading PRD, Architecture, Sprint planning |
| `/home/hcvst/dev/bmad/bmad-mailreactor/mailreactor/` | **Python project root** - deliverable code, tests, end-user docs | ALL Python code, tests, user documentation |
| `/home/hcvst/dev/bmad/bmad-mailreactor/mailreactor/src/mailreactor/` | Source code | Writing implementation code |
| `/home/hcvst/dev/bmad/bmad-mailreactor/mailreactor/tests/` | Test suites | Writing tests |

### Two Documentation Layers

**CRITICAL DISTINCTION:**

| Location | Purpose | Audience | Examples |
|----------|---------|----------|----------|
| `./docs/` | Team process, sprint planning, architecture | **Internal team** (us) | PRD, Architecture, Sprint status, Epics, TDD guide |
| `./mailreactor/docs/` | End-user documentation | **Mail Reactor users** (external) | API docs, Installation guide, Tutorials |

**Never confuse these two!** Writing user docs in `./docs/` or team docs in `./mailreactor/docs/` is a critical error.

### Command Execution

**ALL commands MUST be run from the Python project root:**

```bash
cd mailreactor && .venv/bin/python <script>
cd mailreactor && .venv/bin/pytest <test_file>
```

**If a command fails:** ASK for help. Do NOT explore alternatives or try different paths.

### Testing Principles (CRITICAL)

**✅ ONLY test functionality WE have added**  
**❌ DO NOT test concrete config values but our config machinery**  
**❌ DO NOT test Python machinery**  
**❌ DO NOT test 3rd party library functionality**  
**❌ DO NOT test framework behavior**

**Examples:**

- ✅ **Test:** Our business logic, our domain rules, our API endpoints, our email parsing logic
- ❌ **Don't test:** FastAPI routing works, Pydantic validates, logging library logs, that `email.parser.Parser` actually parses emails
- ✅ **Test:** That our provider.yaml configuration machinery works 
- ❌ **Don't test:** That the provider config contains gmail, outlook etc as that might change.

**Rationale:** Keep tests focused and minimal - only verify the value we're adding to the codebase, not that Python or our dependencies work correctly.

### Library Usage

**Consult official documentation** for all 3rd party libraries to ensure:
- Code is minimal and focused
- Libraries are used canonically (the "right way")
- We don't reinvent functionality that already exists

### Code Quality Standards

- **Sharp, focused code:** Easy to understand, minimal complexity
- **Clear comments:** Explain WHY, not WHAT
- **Type hints:** Use Python 3.10+ type annotations throughout
- **Async-first:** Use `async`/`await` for I/O operations

### Git Operations (CRITICAL)

**🚫 ABSOLUTELY NO GIT OPERATIONS BY AGENTS 🚫**

- **NO `git commit`** - HC handles ALL commits
- **NO `git revert`** - HC handles version control  
- **NO `git push`** - HC handles remote operations
- **NO destructive operations** - No force pushes, no deletions
- **✅ READ OPERATIONS ONLY** - You can read code with `git diff`, `git log`, `git show`

**If you need git information:** Ask HC or use read-only git commands.

---

## Executive Summary

Mail Reactor is a self-hosted, open-source headless email client that transforms email integration from weeks to minutes. This architecture document defines the technical decisions that ensure consistent implementation across all development agents and team members.

**Architecture Philosophy:**
- **Developer-first:** Zero-config startup, intuitive APIs, excellent documentation
- **Stateless by default:** No databases, 3-second cold start, horizontal scalability
- **Modern Python:** Async-first, type-safe, leveraging Python 3.10+ features
- **Permissive licensing:** MIT license for maximum adoption
- **Production-ready:** Battle-tested libraries, comprehensive error handling

## Project Initialization

### Quick Start
```bash
# Install Mail Reactor
pipx install mailreactor

# Initialize with your email account
mailreactor init
# (Interactive wizard: email, password detection, connection validation, master password)

# Start the server
mailreactor start
# (Prompts for master password or reads MAILREACTOR_PASSWORD env var)

# API available at http://localhost:8000
# OpenAPI docs at http://localhost:8000/docs
```

### Development Setup
```bash
# Prerequisites: Python 3.10+, pip
git clone https://github.com/yourusername/mailreactor.git
cd mailreactor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Start development server (with auto-reload)
mailreactor dev
```

## Decision Summary

| Category | Decision | Version | Affects FRs | Rationale |
| -------- | -------- | ------- | ----------- | --------- |
| **License** | MIT | - | All | Maximum adoption, Python ecosystem norms, developer-first positioning |
| **Web Framework** | FastAPI | 0.122.0 | API-* | Modern async Python framework, auto-generated OpenAPI docs, excellent DX |
| **ASGI Server** | Uvicorn | latest | INSTALL-* | Industry standard, bundled with FastAPI, production-ready |
| **IMAP Client** | IMAPClient | 3.0.1 | EMAIL-RETRIEVE-*, EMAIL-SEARCH-* | BSD-3 licensed, production-stable, Pythonic API, battle-tested |
| **SMTP Client** | aiosmtplib | 5.0.0 | EMAIL-SEND-* | MIT licensed, native async, production-stable |
| **Async Pattern** | asyncio + executor | stdlib | All I/O operations | Balance of simplicity (IMAPClient sync) with FastAPI async model |
| **CLI Framework** | Typer | 0.20.0 | INSTALL-*, SYSTEM-* | FastAPI sibling, MIT licensed, intuitive developer experience |
| **Data Validation** | Pydantic | v2 | API-*, All requests | Bundled with FastAPI, type-safe, excellent validation error messages |
| **Configuration** | Pydantic Settings | latest | AUTH-*, CONFIG-* | Seamless FastAPI integration, environment variable support, type-safe |
| **Logging** | structlog | latest | SYSTEM-MONITOR-* | Structured JSON logs, production-ready, excellent async support |
| **Testing** | pytest + pytest-asyncio | latest | All | Python standard, async test support, excellent plugin ecosystem |
| **Python Version** | 3.10+ | 3.10+ | All | Modern async features, structural pattern matching, better type hints |
| **State Management** | Stateless (MVP) | - | STATE-* | NFR-P1: 3-second startup, horizontal scalability, zero dependencies |
| **Provider Detection** | YAML config + Mozilla Autoconfig | - | ACCOUNT-* | Hardcoded common providers, Mozilla fallback (1000+ providers), ISP autoconfig |
| **Credential Storage** | Encrypted file (YAML) | - | AUTH-*, CONFIG-* | Fernet + PBKDF2, master password required, project-local config |
| **Configuration Format** | YAML (mailreactor.yaml) | - | CONFIG-* | Human-readable, custom !encrypted tag, project-local (like docker-compose.yaml) |
| **Error Handling** | FastAPI exceptions + custom base | - | All | Consistent error responses, proper HTTP status codes, clear messages |
| **API Documentation** | OpenAPI/Swagger + ReDoc | Auto | API-* | Auto-generated from FastAPI, interactive testing, always up-to-date |

## Project Structure

```
mailreactor/
├── src/
│   └── mailreactor/
│       ├── __init__.py
│       ├── __main__.py              # CLI entry point
│       ├── main.py                  # FastAPI app initialization
│       ├── config.py                # Pydantic Settings configuration
│       ├── exceptions.py            # Custom exception hierarchy
│       │
│       ├── api/                     # FastAPI routers
│       │   ├── __init__.py
│       │   ├── dependencies.py      # Request dependencies
│       │   ├── accounts.py          # FR: ACCOUNT-*
│       │   ├── messages.py          # FR: EMAIL-RETRIEVE-*, EMAIL-SEARCH-*
│       │   ├── send.py              # FR: EMAIL-SEND-*
│       │   ├── health.py            # FR: SYSTEM-MONITOR-*
│       │   └── webhooks.py          # FR: WEBHOOK-* (Phase 2)
│       │
│       ├── core/                    # Core business logic
│       │   ├── __init__.py
│       │   ├── account.py           # Account management
│       │   ├── imap_client.py       # IMAP wrapper with executor pattern
│       │   ├── smtp_client.py       # SMTP wrapper (async)
│       │   ├── message_parser.py    # Email parsing and normalization
│       │   ├── provider_detector.py # Auto-detect IMAP/SMTP settings
│       │   ├── config.py            # YAML config file operations
│       │   ├── encryption.py        # Password encryption (PBKDF2 + Fernet)
│       │   └── connection_validator.py # IMAP/SMTP connection validation
│       │
│       ├── models/                  # Pydantic models
│       │   ├── __init__.py
│       │   ├── account.py           # Account models
│       │   ├── message.py           # Message/email models
│       │   ├── envelope.py          # Email envelope models
│       │   ├── attachment.py        # Attachment models
│       │   └── responses.py         # API response models
│       │
│       ├── cli/                     # Typer CLI commands
│       │   ├── __init__.py
│       │   ├── server.py            # Start/stop server commands
│       │   ├── init.py              # mailreactor init wizard
│       │   └── utils.py             # CLI utilities
│       │
│       └── utils/                   # Shared utilities
│           ├── __init__.py
│           ├── logging.py           # structlog configuration
│           └── async_helpers.py     # Async utility functions
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # pytest fixtures
│   ├── test_api/                    # API endpoint tests
│   ├── test_core/                   # Core logic tests
│   ├── test_models/                 # Model validation tests
│   ├── test_cli/                    # CLI command tests
│   └── integration/                 # Integration tests (mock IMAP/SMTP)
│
├── docs/                            # Project documentation
│   ├── architecture.md              # This file
│   ├── prd.md                       # Product requirements
│   ├── api-reference.md             # API documentation
│   └── contributing.md              # Contribution guidelines
│
├── pyproject.toml                   # Project metadata, dependencies
├── README.md                        # Project overview
├── LICENSE                          # MIT license
└── .gitignore
```

## Functional Requirements to Architecture Mapping

| FR Category | Primary Modules | Key Technologies |
| ----------- | --------------- | ---------------- |
| **ACCOUNT-\*** (Account Management) | `core/config.py`, `core/encryption.py`, `core/provider_detector.py`, `core/connection_validator.py`, `cli/init.py` | PyYAML, cryptography (Fernet/PBKDF2), IMAPClient, aiosmtplib, httpx |
| **EMAIL-SEND-\*** (Email Sending) | `core/smtp_client.py`, `api/send.py`, `models/message.py` | aiosmtplib, FastAPI, Pydantic |
| **EMAIL-RETRIEVE-\*** (Email Retrieval) | `core/imap_client.py`, `api/messages.py`, `models/message.py` | IMAPClient, asyncio executor, FastAPI |
| **EMAIL-SEARCH-\*** (Email Search) | `core/imap_client.py`, `api/messages.py` | IMAPClient SEARCH command, FastAPI query params |
| **SYSTEM-MONITOR-\*** (Health & Monitoring) | `api/health.py`, `utils/logging.py` | FastAPI, structlog |
| **INSTALL-\*** (Installation & Deployment) | `cli/server.py`, `cli/init.py`, `__main__.py` | Typer, Uvicorn, setuptools |
| **AUTH-\*** (Authentication & Security) | `config.py`, `core/encryption.py`, `api/dependencies.py` | Pydantic Settings, cryptography, FastAPI dependencies |
| **CONFIG-\*** (Configuration Management) | `core/config.py`, `core/encryption.py`, `models/account.py` | PyYAML, cryptography, Pydantic |
| **API-\*** (API Design & Standards) | `api/*`, `models/responses.py` | FastAPI, Pydantic, OpenAPI |

## Technology Stack Details

### Core Technologies

**Web Framework: FastAPI 0.122.0**
- **Why:** Modern async Python framework with automatic OpenAPI generation
- **Features:** Type hints, dependency injection, async/await support, excellent docs
- **Usage:** All HTTP endpoints, request validation, response serialization
- **Documentation:** https://fastapi.tiangolo.com/

**IMAP Client: IMAPClient 3.0.1**
- **Why:** Production-stable, Pythonic API, BSD-3 licensed (MIT-compatible)
- **Features:** UID handling, parsed responses, internationalized mailbox support
- **Pattern:** Synchronous library wrapped with `asyncio.run_in_executor()`
- **Documentation:** https://imapclient.readthedocs.io/

**SMTP Client: aiosmtplib 5.0.0**
- **Why:** Native async, MIT licensed, production-stable
- **Features:** Full SMTP support, TLS/SSL, authentication
- **Pattern:** Direct async/await usage
- **Documentation:** https://aiosmtplib.readthedocs.io/

**CLI Framework: Typer 0.20.0**
- **Why:** "FastAPI of CLIs", same author, intuitive API
- **Features:** Type hints, automatic help generation, subcommands
- **Usage:** `mailreactor start`, `mailreactor dev`, account management
- **Documentation:** https://typer.tiangolo.com/

**Data Validation: Pydantic v2**
- **Why:** Bundled with FastAPI, type-safe, excellent error messages
- **Features:** Data validation, serialization, Settings management
- **Usage:** All request/response models, configuration
- **Documentation:** https://docs.pydantic.dev/

**Logging: structlog**
- **Why:** Structured JSON logging, async support, production-ready
- **Features:** Context binding, processors, multiple outputs
- **Usage:** All logging throughout application
- **Documentation:** https://www.structlog.org/

**Testing: pytest + pytest-asyncio**
- **Why:** Python standard, async test support, rich plugin ecosystem
- **Features:** Fixtures, parametrization, async test support
- **Usage:** Unit tests, integration tests, API tests
- **Documentation:** https://pytest.org/

### Integration Points

**IMAP Integration (IMAPClient + asyncio executor)**
```python
# core/imap_client.py pattern
from imapclient import IMAPClient
import asyncio
from functools import partial

class AsyncIMAPClient:
    def __init__(self, host: str, port: int, use_ssl: bool = True):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self._executor = None
    
    async def _run_sync(self, func, *args, **kwargs):
        """Execute sync IMAPClient method in thread pool executor"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            partial(func, *args, **kwargs)
        )
    
    async def connect(self):
        """Async wrapper for connection"""
        def _connect():
            client = IMAPClient(self.host, port=self.port, ssl=self.use_ssl)
            return client
        return await self._run_sync(_connect)
    
    async def login(self, client: IMAPClient, username: str, password: str):
        """Async wrapper for login"""
        return await self._run_sync(client.login, username, password)
    
    async def search(self, client: IMAPClient, criteria: list):
        """Async wrapper for search"""
        return await self._run_sync(client.search, criteria)
```

**SMTP Integration (aiosmtplib - native async)**
```python
# core/smtp_client.py pattern
import aiosmtplib
from email.message import EmailMessage

class AsyncSMTPClient:
    async def send_email(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        message: EmailMessage
    ):
        """Native async email sending"""
        await aiosmtplib.send(
            message,
            hostname=host,
            port=port,
            username=username,
            password=password,
            use_tls=True
        )
```

**Provider Auto-Detection (Epic 2)**
```python
# core/provider_detector.py - Multi-source detection cascade
import httpx
import yaml
from pathlib import Path

class ProviderDetector:
    """Auto-detect IMAP/SMTP settings from email address.
    
    Detection cascade:
    1. Local providers.yaml (Gmail, Outlook, Yahoo, iCloud) - instant, offline
    2. Mozilla Thunderbird Autoconfig API (1000+ providers) - 5s timeout
    3. ISP autoconfig (provider-specific) - 5s timeout  
    4. None (manual configuration required)
    """
    
    def __init__(self):
        # Load hardcoded providers from core/providers.yaml
        providers_path = Path(__file__).parent / "providers.yaml"
        with providers_path.open("r") as f:
            self.providers = yaml.safe_load(f)
    
    async def detect(self, email: str) -> Optional[ProviderConfig]:
        """Detect provider settings from email address."""
        domain = email.split("@")[1].lower()
        
        # 1. Check local providers.yaml (fast path)
        if domain in self.providers:
            return ProviderConfig(**self.providers[domain])
        
        # 2. Query Mozilla Autoconfig
        mozilla_config = await self._query_mozilla(domain)
        if mozilla_config:
            return mozilla_config
        
        # 3. Query ISP autoconfig
        isp_config = await self._query_isp(domain)
        if isp_config:
            return isp_config
        
        # 4. No detection possible
        return None
    
    async def _query_mozilla(self, domain: str) -> Optional[ProviderConfig]:
        """Query Mozilla Thunderbird autoconfig database."""
        url = f"https://autoconfig.thunderbird.net/v1.1/{domain}"
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    return self._parse_autoconfig_xml(response.text)
            except httpx.TimeoutException:
                pass
        return None
```

**Example providers.yaml:**
```yaml
# core/providers.yaml - Hardcoded common providers
gmail.com:
  provider_name: Gmail
  imap_host: imap.gmail.com
  imap_port: 993
  imap_ssl: true
  smtp_host: smtp.gmail.com
  smtp_port: 587
  smtp_starttls: true

outlook.com:
  provider_name: Outlook
  imap_host: outlook.office365.com
  imap_port: 993
  imap_ssl: true
  smtp_host: smtp.office365.com
  smtp_port: 587
  smtp_starttls: true

yahoo.com:
  provider_name: Yahoo
  imap_host: imap.mail.yahoo.com
  imap_port: 993
  imap_ssl: true
  smtp_host: smtp.mail.yahoo.com
  smtp_port: 587
  smtp_starttls: true

icloud.com:
  provider_name: iCloud
  imap_host: imap.mail.me.com
  imap_port: 993
  imap_ssl: true
  smtp_host: smtp.mail.me.com
  smtp_port: 587
  smtp_starttls: true
```

## Novel Patterns & Design Decisions

### IMAP-as-Database Pattern (Phase 2 - Experimental)

**Problem:** Stateless architecture requires external state storage for features like webhook delivery tracking, read receipts, folder synchronization status.

**Solution:** Use IMAP itself as a lightweight key-value store by storing metadata in special mailbox folders.

**Implementation Approach:**
```
[MailReactor-State]/
  ├── webhooks/          # Webhook delivery status
  ├── sync-cursors/      # Last-synced message IDs per folder
  └── metadata/          # Custom application metadata
```

**Trade-offs:**
- ✅ No external database required
- ✅ State travels with email account
- ✅ Works with any IMAP server
- ⚠️ Slower than Redis/database
- ⚠️ Experimental - not all providers tested
- ⚠️ Folder creation permissions may vary

**When to use:** Opt-in via configuration flag, Phase 2 only

### Async Executor Pattern for IMAPClient

**Problem:** IMAPClient is synchronous, but FastAPI is async. Blocking calls hurt performance.

**Solution:** Wrap IMAPClient calls with `asyncio.run_in_executor()` to run in thread pool.

**Benefits:**
- ✅ Use battle-tested IMAPClient library
- ✅ Maintain FastAPI async benefits
- ✅ Simple to implement and debug
- ✅ Good enough performance for MVP

**Alternative considered:** Write fully async IMAP client
- ❌ High complexity, reinventing wheel
- ❌ More bugs, less stable
- ✅ Could be Phase 2 optimization if needed

## Implementation Patterns

These patterns ensure consistent implementation across all AI agents:

### 1. API Endpoint Pattern
```python
# api/messages.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models.message import Message, MessageListResponse
from ..models.account import AccountCredentials
from ..core.imap_client import AsyncIMAPClient
from ..exceptions import MailReactorException

router = APIRouter(prefix="/messages", tags=["messages"])

@router.get("/{account_id}", response_model=MessageListResponse)
async def list_messages(
    account_id: str,
    folder: str = "INBOX",
    limit: int = 50,
    credentials: AccountCredentials = Depends(get_account_credentials)
):
    """
    List messages from an IMAP folder.
    
    - **account_id**: Unique account identifier
    - **folder**: IMAP folder name (default: INBOX)
    - **limit**: Maximum messages to return (default: 50, max: 1000)
    """
    try:
        imap_client = AsyncIMAPClient(
            host=credentials.imap_host,
            port=credentials.imap_port
        )
        messages = await imap_client.list_messages(folder, limit)
        return MessageListResponse(messages=messages, count=len(messages))
    
    except MailReactorException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        logger.error("unexpected_error", error=str(e), account_id=account_id)
        raise HTTPException(status_code=500, detail="Internal server error")
```

### 2. Error Handling Pattern
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

# Usage in core modules
try:
    client.login(username, password)
except imaplib.IMAP4.error as e:
    raise AuthenticationError(f"IMAP authentication failed: {str(e)}")
```

### 3. Logging Pattern (Single Pipeline with Dual Renderers)

**Epic 1 Discovery:** Implemented in Story 1.3, this pattern uses a single internal structlog pipeline with swappable renderers instead of two separate logging systems.

**Pattern Benefits:**
- No code duplication between console and JSON logging
- Shared processors (timestamp, log level, sensitive data filtering)
- Runtime renderer selection via `json_format` parameter
- Consistent behavior regardless of output format

```python
# utils/logging.py - Single pipeline, dual renderer pattern
import structlog

def configure_logging(json_format: bool = False, log_level: str = "INFO") -> None:
    """Configure structlog with console or JSON renderer.
    
    Single pipeline with dual renderers:
    - Console renderer (default): Human-readable colored output
    - JSON renderer (opt-in): Machine-readable structured logs
    """
    # Shared processors used by both renderers (before renderer)
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        _filter_sensitive_data,  # Redact passwords, api_keys, etc.
    ]
    
    # Choose renderer based on configuration (the ONLY difference)
    renderer = (
        structlog.processors.JSONRenderer()
        if json_format
        else structlog.dev.ConsoleRenderer(
            colors=True,
            exception_formatter=structlog.dev.rich_traceback,
        )
    )
    
    # Configure structlog with stdlib integration
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            *shared_processors,  # Reuse shared processors
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure Python's standard logging to use structlog formatting
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=shared_processors,
    )
    
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper()))

# Usage throughout application
logger = structlog.get_logger(__name__)

# Context binding for request tracing
bind_context(request_id=request_id, account_id=account_id)
logger.info("fetching_messages", limit=limit)
clear_context()  # Clean up after request

# Error logging
logger.error("imap_connection_failed", error=str(e), host=host, port=port)
```

**Key Insight:** Renderer selection happens at configuration time, not at every log call. This makes the pattern efficient and eliminates conditional logic throughout the codebase.

### 4. Configuration Pattern
```python
# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """Application configuration via environment variables"""
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    
    # Performance settings
    max_workers: int = 10
    request_timeout: int = 30
    
    # Security settings
    api_key_header: str = "X-API-Key"
    allowed_origins: list[str] = ["*"]
    
    # Feature flags
    enable_imap_as_database: bool = False  # Phase 2
    enable_webhooks: bool = False          # Phase 2
    
    model_config = SettingsConfigDict(
        env_prefix="MAILREACTOR_",
        env_file=".env",
        case_sensitive=False
    )

# Singleton instance
settings = Settings()
```

### 5. Response Envelope Pattern (Generic Success and Error Responses)

**Epic 1 Discovery:** Implemented in Story 1.7, this pattern wraps all API responses in consistent envelopes with metadata for tracing and debugging.

**Pattern Benefits:**
- Consistent response structure across all endpoints
- Generic `SuccessResponse[T]` provides type safety
- Request ID for distributed tracing
- Timestamp for debugging and logging
- Clear separation between data and metadata

```python
# models/responses.py - Generic success envelope
from datetime import datetime, timezone
from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")

class ResponseMeta(BaseModel):
    """Metadata included in every response."""
    request_id: str = Field(..., description="Unique request identifier for tracing")
    timestamp: datetime = Field(..., description="Response timestamp in UTC (ISO 8601)")

class SuccessResponse(BaseModel, Generic[T]):
    """Generic success envelope wrapping all successful responses."""
    data: T = Field(..., description="Response data")
    meta: ResponseMeta = Field(..., description="Response metadata")
    
    @classmethod
    def create(cls, data: T, request_id: str) -> "SuccessResponse[T]":
        """Factory method to create success response with current timestamp."""
        return cls(
            data=data,
            meta=ResponseMeta(
                request_id=request_id, 
                timestamp=datetime.now(timezone.utc)
            ),
        )

class ErrorDetail(BaseModel):
    """Error structure with code, message, and optional details."""
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: dict[str, Any] | None = Field(None, description="Additional error context")

class ErrorResponse(BaseModel):
    """Standard error envelope for all error responses."""
    error: ErrorDetail = Field(..., description="Error details")
    meta: ResponseMeta = Field(..., description="Response metadata")

# Usage in API endpoints
from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/health", response_model=SuccessResponse[HealthResponse])
async def health_check(request: Request):
    """Health check endpoint using response envelope."""
    health_data = HealthResponse(
        status="healthy",
        version="0.1.0",
        uptime_seconds=123.45
    )
    return SuccessResponse.create(
        data=health_data, 
        request_id=request.state.request_id  # From middleware
    )

# Error handling with envelope
from fastapi import HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Convert HTTPException to ErrorResponse envelope."""
    error_response = ErrorResponse(
        error=ErrorDetail(
            code=f"HTTP_{exc.status_code}",
            message=exc.detail,
            details=None
        ),
        meta=ResponseMeta(
            request_id=request.state.request_id,
            timestamp=datetime.now(timezone.utc)
        )
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )
```

**Key Insight:** Using Pydantic's `Generic[T]` allows `SuccessResponse[HealthResponse]` to provide full type safety and auto-generate accurate OpenAPI schemas. The `request_id` from middleware creates end-to-end request tracing.

### 6. Development Mode Pattern (Dual CLI Commands)

**Epic 1 Discovery:** Implemented in Story 1.8, separate `start` and `dev` commands optimize for production vs development workflows.

**Pattern Benefits:**
- Clear separation between production and development environments
- Different defaults for each mode (log level, reload, log format)
- No "magic" environment detection - explicit command choice
- Prevents accidentally running dev mode in production

```python
# cli/server.py - Dual command pattern
import typer
import uvicorn

app = typer.Typer()

@app.command()
def start(
    host: str = "0.0.0.0",
    port: int = 8000,
    log_level: str = "INFO",
    json_logs: bool = True,  # Production default: JSON
):
    """Start Mail Reactor in production mode.
    
    - Optimized for production deployment
    - JSON logs by default (for log aggregators)
    - No auto-reload (stability over convenience)
    """
    configure_logging(json_format=json_logs, log_level=log_level)
    logger.info("mail_reactor_starting", mode="production", host=host, port=port)
    
    uvicorn.run(
        "mailreactor.main:app",
        host=host,
        port=port,
        log_config=None,  # Use structlog configuration
        reload=False,  # No auto-reload in production
    )

@app.command()
def dev(
    host: str = "127.0.0.1",  # Localhost only
    port: int = 8000,
    log_level: str = "DEBUG",  # Development default: DEBUG
    json_logs: bool = False,  # Development default: console
):
    """Start Mail Reactor in development mode with auto-reload.
    
    - Optimized for development workflow
    - Console logs by default (human-readable)
    - Auto-reload on file changes
    - Debug log level for detailed output
    """
    configure_logging(json_format=json_logs, log_level=log_level)
    logger.warning("development_mode_active", warning="Not for production use")
    logger.info(
        "mail_reactor_starting",
        mode="development",
        auto_reload=True,
        watch_dir="src/mailreactor"
    )
    
    uvicorn.run(
        "mailreactor.main:app",
        host=host,
        port=port,
        log_config=None,
        reload=True,  # Auto-reload on file changes
        reload_dirs=["src/mailreactor"],  # Watch only source code
        reload_delay=0.5,  # Half-second debounce
    )
```

**Key Insight:** Separate commands with different defaults eliminate the need for environment variables or complex configuration. Developers explicitly choose the mode they want. The `dev` command binds to `127.0.0.1` by default to prevent accidental external exposure during development.

### 7. Testing Pattern
```python
# tests/test_api/test_messages.py
import pytest
from fastapi.testclient import TestClient
from mailreactor.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_list_messages_success(mock_imap_client):
    """Test successful message listing"""
    response = client.get(
        "/messages/test-account",
        params={"folder": "INBOX", "limit": 10},
        headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "messages" in data
    assert len(data["messages"]) <= 10

@pytest.mark.asyncio
async def test_list_messages_auth_error(mock_imap_auth_error):
    """Test authentication failure handling"""
    response = client.get(
        "/messages/test-account",
        headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 401
    assert "authentication failed" in response.json()["detail"].lower()
```

### 8. Configuration Pattern (Project-Local YAML with Encryption)

**Source:** Epic 2 Revised, Course Correction 2025-12-06

**Problem:** Account credentials must persist across restarts while remaining secure and maintaining Mail Reactor's zero-configuration philosophy.

**Solution:** Project-local `mailreactor.yaml` file with encrypted passwords using Fernet + PBKDF2, following the mental model of `docker-compose.yaml`, `package.json`, and `.git/`.

**Pattern Benefits:**
- **Project-local:** Configuration lives where you use it, not in global directories
- **Developer-friendly:** Familiar pattern (like `git init`, `npm init`)
- **Secure:** Passwords encrypted at rest with master password
- **Simple:** Single file, no database, no runtime state management
- **Version-control friendly:** Config structure visible, passwords encrypted

**Implementation:**

```python
# core/config.py - YAML Config Operations
from pathlib import Path
import yaml
from pydantic import BaseModel, EmailStr
from .encryption import encrypt, decrypt

class IMAPConfig(BaseModel):
    host: str
    port: int = 993
    ssl: bool = True
    username: str
    password: str  # Decrypted in memory

class SMTPConfig(BaseModel):
    host: str
    port: int = 587
    starttls: bool = True
    username: str
    password: str  # Decrypted in memory

class AccountConfig(BaseModel):
    email: EmailStr
    imap: IMAPConfig
    smtp: SMTPConfig
    
    @classmethod
    def from_yaml(cls, yaml_path: Path, master_password: str):
        """Load config from YAML and decrypt passwords."""
        with yaml_path.open("r") as f:
            data = yaml.safe_load(f)
        
        # Decrypt IMAP password
        imap_encrypted = data["imap"]["password"]  # !encrypted value from YAML
        imap_password = decrypt(imap_encrypted, master_password)
        
        # Decrypt SMTP password
        smtp_encrypted = data["smtp"]["password"]  # !encrypted value from YAML
        smtp_password = decrypt(smtp_encrypted, master_password)
        
        return cls(
            email=data["email"],
            imap=IMAPConfig(**{**data["imap"], "password": imap_password}),
            smtp=SMTPConfig(**{**data["smtp"], "password": smtp_password})
        )

def save_config(path: Path, config: AccountConfig, master_password: str) -> None:
    """Save config to YAML with encrypted passwords."""
    # Encrypt passwords
    imap_encrypted = encrypt(config.imap.password, master_password)
    smtp_encrypted = encrypt(config.smtp.password, master_password)
    
    # Build YAML structure
    yaml_data = {
        "email": config.email,
        "imap": {
            "host": config.imap.host,
            "port": config.imap.port,
            "ssl": config.imap.ssl,
            "username": config.imap.username,
            "password": f"!encrypted {imap_encrypted}"
        },
        "smtp": {
            "host": config.smtp.host,
            "port": config.smtp.port,
            "starttls": config.smtp.starttls,
            "username": config.smtp.username,
            "password": f"!encrypted {smtp_encrypted}"
        }
    }
    
    with path.open("w") as f:
        yaml.dump(yaml_data, f, default_flow_style=False)
    
    # Set secure permissions (user read/write only)
    path.chmod(0o600)
```

**YAML File Structure:**

```yaml
# mailreactor.yaml
email: user@gmail.com

imap:
  host: imap.gmail.com
  port: 993
  ssl: true
  username: user@gmail.com
  password: !encrypted gAAAAABhqK8s...  # Fernet-encrypted

smtp:
  host: smtp.gmail.com
  port: 587
  starttls: true
  username: user@gmail.com
  password: !encrypted gAAAAABhSMTP...  # Fernet-encrypted
```

**Encryption Implementation:**

```python
# core/encryption.py - PBKDF2 + Fernet Encryption
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives import hashes
import base64
import os

def generate_salt() -> bytes:
    """Generate 32-byte random salt."""
    return os.urandom(32)

def derive_key(master_password: str, salt: bytes) -> bytes:
    """Derive Fernet key from master password using PBKDF2."""
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,  # OWASP 2023 standard
    )
    key = kdf.derive(master_password.encode())
    return base64.urlsafe_b64encode(key)

def encrypt(plaintext: str, master_password: str) -> str:
    """Encrypt password with master password.
    
    Returns: <base64-salt><fernet-ciphertext> (single string for YAML)
    """
    salt = generate_salt()
    key = derive_key(master_password, salt)
    fernet = Fernet(key)
    
    ciphertext = fernet.encrypt(plaintext.encode())
    
    # Combine salt + ciphertext for storage
    salt_b64 = base64.b64encode(salt).decode()
    ciphertext_b64 = ciphertext.decode()
    
    return salt_b64 + ciphertext_b64

def decrypt(encrypted: str, master_password: str) -> str:
    """Decrypt password with master password.
    
    Args:
        encrypted: <base64-salt><fernet-ciphertext> string
        master_password: User's master password
    
    Returns: Decrypted plaintext password
    
    Raises:
        cryptography.fernet.InvalidToken: Wrong master password
    """
    # Split salt and ciphertext
    salt_b64 = encrypted[:44]  # Base64-encoded 32 bytes = 44 chars
    ciphertext_b64 = encrypted[44:]
    
    salt = base64.b64decode(salt_b64)
    key = derive_key(master_password, salt)
    fernet = Fernet(key)
    
    plaintext = fernet.decrypt(ciphertext_b64.encode())
    return plaintext.decode()
```

**Security Properties:**
- **Fernet:** Authenticated encryption (AES-128-CBC + HMAC-SHA256)
- **PBKDF2:** 100,000 iterations slows brute-force attacks
- **Salt:** Unique 32-byte salt per password prevents rainbow tables
- **Master password:** Never written to disk (env var or prompt only)
- **File permissions:** 0600 (user read/write only)
- **Decrypted in memory:** Passwords only exist decrypted in process memory

**Configuration Lifecycle:**

```
mailreactor init (wizard)
    ↓
Auto-detect provider settings
    ↓
Validate IMAP/SMTP connections
    ↓
Prompt for master password
    ↓
Encrypt passwords with master password
    ↓
Write mailreactor.yaml to current directory (0600 permissions)
    ↓
mailreactor start (reads config from cwd)
    ↓
Prompt for master password (or read from MAILREACTOR_PASSWORD env var)
    ↓
Decrypt credentials into memory
    ↓
Start server with AccountConfig loaded
```

**Single Account Model:**
- One `mailreactor.yaml` per project directory
- One account per Mail Reactor instance
- Multi-account: Run multiple instances (different directories, different ports)
- No runtime account management API (config file is source of truth)

**When to Use:**
- Self-hosted, single-user deployments (MVP use case)
- Developer-friendly workflows (init → start pattern)
- Security without external KMS complexity

**Trade-offs:**
- ✅ Simpler than multi-account runtime management
- ✅ Familiar developer pattern (docker-compose, git)
- ✅ Config lives with project (not hidden in ~/.config)
- ⚠️ Master password required at startup
- ⚠️ Lost master password = must re-run init
- ⚠️ Multi-account = multiple instances (acceptable for MVP)

---

## Consistency Rules

### Naming Conventions

**Python Code:**
- **Modules/packages:** `snake_case` (e.g., `imap_client.py`, `message_parser.py`)
- **Classes:** `PascalCase` (e.g., `AsyncIMAPClient`, `MessageListResponse`)
- **Functions/methods:** `snake_case` (e.g., `list_messages()`, `parse_envelope()`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_MESSAGE_SIZE`, `DEFAULT_TIMEOUT`)
- **Private methods:** `_leading_underscore` (e.g., `_run_sync()`, `_parse_headers()`)
- **Type aliases:** `PascalCase` (e.g., `MessageID = str`)

**API Endpoints:**
- **Resources:** Plural nouns (e.g., `/messages`, `/accounts`, `/webhooks`)
- **Actions:** HTTP verbs (GET, POST, PUT, DELETE) - avoid verbs in URLs
- **Identifiers:** `{resource_id}` (e.g., `/messages/{message_id}`)
- **Query params:** `snake_case` (e.g., `?folder_name=INBOX&limit=50`)

**File Names:**
- **Python modules:** `snake_case.py`
- **Test files:** `test_*.py` (pytest convention)
- **Config files:** `lowercase.yaml`, `lowercase.json`
- **Documentation:** `lowercase-with-hyphens.md`

### Code Organization

**Module Imports Order:**
1. Standard library imports
2. Third-party imports (FastAPI, Pydantic, etc.)
3. Local application imports

```python
# Good example
import asyncio
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import structlog

from ..models.message import Message
from ..core.imap_client import AsyncIMAPClient
from ..exceptions import MailReactorException
```

**Dependency Flow:**
- `api/` depends on → `core/` and `models/`
- `core/` depends on → `models/` and `utils/`
- `models/` has no internal dependencies (pure Pydantic)
- `utils/` has minimal dependencies
- **Never:** circular dependencies

**Function Organization:**
- Public API functions at top
- Helper functions below
- Private functions at bottom
- Max function length: ~50 lines (soft limit)

### Error Handling

**Principles:**
1. **Catch specific exceptions** - Never bare `except:`
2. **Log before raising** - Always log errors with context
3. **Fail fast** - Validate early, fail early
4. **User-friendly messages** - Hide implementation details in production

**Exception Hierarchy:**
```
MailReactorException (base)
├── AccountError
│   ├── AccountNotFoundError
│   ├── AccountAlreadyExistsError
│   └── AccountConfigurationError
├── ConnectionError
│   ├── IMAPConnectionError
│   ├── SMTPConnectionError
│   └── NetworkTimeoutError
├── AuthenticationError
│   ├── InvalidCredentialsError
│   └── AuthTokenExpiredError
├── MessageError
│   ├── MessageNotFoundError
│   ├── MessageParseError
│   └── MessageTooLargeError
└── StateError
    ├── StateLockError
    └── StateCorruptionError
```

**Error Response Format (FastAPI):**
```json
{
  "detail": "Human-readable error message",
  "error_code": "IMAP_CONNECTION_FAILED",
  "request_id": "req_abc123"
}
```

### Logging Strategy

**Log Levels:**
- **DEBUG:** Detailed diagnostic information (disabled in production)
- **INFO:** General informational messages (request/response, state changes)
- **WARNING:** Recoverable errors, degraded performance
- **ERROR:** Unrecoverable errors requiring attention
- **CRITICAL:** System-level failures

**Structured Logging Fields:**
```python
logger.info(
    "event_name",                    # Required: What happened
    account_id="acc_123",            # Context: Who
    folder="INBOX",                  # Context: Where
    message_count=42,                # Context: What
    duration_ms=123,                 # Performance: How long
    status="success"                 # Outcome: Result
)
```

**What to Log:**
- ✅ API requests (method, path, status, duration)
- ✅ IMAP/SMTP operations (connect, login, search, send)
- ✅ Errors with full context
- ✅ Performance metrics (slow queries, timeouts)
- ❌ Passwords or sensitive credentials
- ❌ Full email bodies (PII risk)
- ❌ Debug noise in production

## Data Architecture

### Core Data Models

**Account Model:**
```python
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class AccountCredentials(BaseModel):
    """Account credentials for IMAP/SMTP access"""
    email: EmailStr
    imap_host: str
    imap_port: int = 993
    imap_ssl: bool = True
    smtp_host: str
    smtp_port: int = 587
    smtp_starttls: bool = True
    password: str = Field(..., exclude=True)  # Never log/serialize

class AccountConfig(BaseModel):
    """Account configuration"""
    account_id: str
    display_name: Optional[str] = None
    auto_detect_provider: bool = True
    default_folder: str = "INBOX"
```

**Message Model:**
```python
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class EmailAddress(BaseModel):
    name: Optional[str] = None
    email: str

class MessageEnvelope(BaseModel):
    """Email envelope (headers only)"""
    message_id: str
    subject: str
    from_: EmailAddress = Field(..., alias="from")
    to: List[EmailAddress]
    cc: List[EmailAddress] = []
    bcc: List[EmailAddress] = []
    date: datetime
    in_reply_to: Optional[str] = None
    references: List[str] = []

class Message(BaseModel):
    """Complete email message"""
    uid: int  # IMAP UID
    envelope: MessageEnvelope
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    attachments: List[str] = []  # Attachment IDs
    flags: List[str] = []  # IMAP flags (\\Seen, \\Flagged, etc.)
    folder: str
```

**Response Models:**
```python
class MessageListResponse(BaseModel):
    messages: List[Message]
    count: int
    folder: str
    has_more: bool = False

class SendEmailResponse(BaseModel):
    message_id: str
    status: str = "sent"
    timestamp: datetime
```

### State Management (Stateless Architecture)

**Design Philosophy:** Mail Reactor is stateless by design. Configuration is loaded at startup from `mailreactor.yaml` and held in memory for the lifetime of the process.

**State Lifecycle:**
1. `mailreactor start` loads and decrypts `mailreactor.yaml`
2. `AccountConfig` object created in memory with decrypted credentials
3. FastAPI app uses this single account for all operations
4. Application stops → no state persistence needed (config file remains)

**No Runtime Account Management:**
- No add/remove account APIs (removed from original Epic 2 design)
- No runtime state manager or storage backend abstraction
- Config file is the source of truth
- Changes require editing `mailreactor.yaml` (or re-running `mailreactor init`)

**Multi-Account Support:**
- Run multiple Mail Reactor instances on different ports
- Each instance in its own directory with its own `mailreactor.yaml`
- Example:
  ```bash
  # Personal email
  cd ~/mail-personal && mailreactor start --port 8000
  
  # Work email
  cd ~/mail-work && mailreactor start --port 8001
  ```

**Phase 2 Enhancement:** Optional orchestrator for managing multiple instances, IMAP-as-database for webhook tracking

## API Contracts

### REST API Standards

**Base URL:** `http://localhost:8000/api/v1`

**Authentication:** API Key via header
```
X-API-Key: your-api-key-here
```

**Content-Type:** `application/json`

**Response Format:**
```json
{
  "data": { ... },           // Success response data
  "meta": {                   // Optional metadata
    "request_id": "req_123",
    "timestamp": "2025-11-25T10:00:00Z"
  }
}
```

**Error Format:**
```json
{
  "detail": "Human-readable error",
  "error_code": "ERROR_CODE",
  "request_id": "req_123"
}
```

### Key Endpoints (MVP)

**Note:** Account management endpoints removed in Epic 2 course correction. Configuration managed via `mailreactor init` wizard and `mailreactor.yaml` file.

**Email Retrieval:**
- `GET /api/v1/messages` - List messages
- `GET /api/v1/messages/{message_id}` - Get message
- `GET /api/v1/folders` - List folders
- `GET /api/v1/search` - Search messages

**Email Sending:**
- `POST /api/v1/send` - Send email
- `POST /api/v1/reply/{message_id}` - Reply to email
- `POST /api/v1/forward/{message_id}` - Forward email

**System:**
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics (if enabled)
- `GET /docs` - OpenAPI documentation (Swagger UI)
- `GET /redoc` - ReDoc documentation

### OpenAPI Documentation

**Automatically generated** from FastAPI type hints and docstrings.

**Access:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

**Documentation Best Practices:**
- Every endpoint has a docstring
- All parameters documented with descriptions
- Example requests/responses provided
- Error codes documented

## Security Architecture

### MVP Security Model

**Threat Model:**
- **In scope:** API authentication, credential storage in memory
- **Out of scope (MVP):** Multi-tenancy, RBAC, OAuth, rate limiting
- **Assumption:** Single-user, trusted network, self-hosted

**Security Measures:**

1. **API Key Authentication**
   - Simple API key in header: `X-API-Key`
   - Configurable via environment variable
   - MVP: Single shared key
   - Phase 2: Per-account keys

2. **Credential Storage (Epic 2 Revised)**
   - **Encrypted at rest:** Passwords encrypted in `mailreactor.yaml` using Fernet
   - **Master password:** Required at startup (env var or interactive prompt)
   - **PBKDF2 key derivation:** 100,000 iterations (OWASP 2023 standard)
   - **Unique salt:** 32-byte random salt per password (prevents rainbow tables)
   - **File permissions:** `mailreactor.yaml` set to 0600 (user read/write only)
   - **Decrypted in memory:** Passwords exist decrypted only in process memory
   - **Never logged:** Passwords marked with `exclude=True` in Pydantic models
   - **Never serialized:** Password fields excluded from API responses

3. **TLS/SSL for Email**
   - IMAP: SSL by default (port 993)
   - SMTP: STARTTLS by default (port 587)
   - TLS certificate verification enabled
   - Configurable per provider

4. **Input Validation**
   - Pydantic validates all inputs
   - Email addresses validated (EmailStr)
   - File size limits on attachments
   - Query parameter bounds (limit, offset)

5. **Error Information Disclosure**
   - Generic errors in production
   - Detailed errors in development
   - No stack traces in API responses
   - Sensitive data redacted from logs
   - Provider-specific hints for common errors (Gmail App Passwords, etc.)

**Phase 2 Security Enhancements:**
- Rate limiting per IP/account
- OAuth 2.0 for Gmail/Outlook
- Webhook signature verification
- API key rotation
- Audit logging

## Performance Considerations

### NFR Targets (from PRD)

- **NFR-P1:** Cold start: 3 seconds
- **NFR-P2:** API response time: 200ms p95 (excluding IMAP/SMTP latency)
- **NFR-P3:** Concurrent connections: 100+ accounts
- **NFR-P4:** Message throughput: 1000+ messages/minute

### Performance Strategies

**1. Async Everywhere**
- FastAPI async endpoints
- aiosmtplib native async
- IMAPClient via executor (non-blocking)
- Async state management with locks

**2. Connection Pooling**
```python
# Phase 2: Connection pool for IMAP
class IMAPConnectionPool:
    def __init__(self, max_connections: int = 10):
        self.pool = asyncio.Queue(maxsize=max_connections)
        self.max_connections = max_connections
    
    async def get_connection(self, host, port, username, password):
        # Reuse existing connection or create new
        pass
```

**3. Caching Strategy (Phase 2)**
- Provider configurations (in-memory)
- Message metadata (short TTL)
- Folder lists (medium TTL)

**4. Lazy Loading**
- Message bodies fetched on-demand
- Attachments downloaded only when requested
- Folder listing on explicit API call

**5. Pagination**
- Default limit: 50 messages
- Maximum limit: 1000 messages
- Cursor-based pagination for large folders (Phase 2)

**6. Timeouts**
- API request timeout: 30s
- IMAP operation timeout: 10s
- SMTP send timeout: 30s
- Configurable via settings

### Performance Monitoring

**Metrics to Track:**
- API response times (p50, p95, p99)
- IMAP operation duration
- SMTP send success rate
- Memory usage per account
- Thread pool utilization

**Logging Performance Data:**
```python
logger.info(
    "api_request_complete",
    method="GET",
    path="/messages",
    status_code=200,
    duration_ms=142,
    account_id="acc_123"
)
```

## Deployment Architecture

### Deployment Models

**1. Single-Server (MVP)**
```
┌─────────────────────────────┐
│   Docker Container          │
│  ┌──────────────────────┐   │
│  │  Mail Reactor        │   │
│  │  (FastAPI + Uvicorn) │   │
│  └──────────────────────┘   │
│         Port 8000            │
└─────────────────────────────┘
```

**2. Docker Compose (Recommended)**
```yaml
# docker-compose.yml
services:
  mailreactor:
    image: mailreactor:latest
    ports:
      - "8000:8000"
    environment:
      - MAILREACTOR_LOG_LEVEL=INFO
      - MAILREACTOR_API_KEY=your-secret-key
      - MAILREACTOR_PASSWORD=your-master-password  # For decrypting config
    volumes:
      - ./mailreactor.yaml:/app/mailreactor.yaml:ro  # Mount config file
      - ./logs:/app/logs
```

**3. Kubernetes (Phase 2 - Production)**
```
┌─────────────────────────────────────┐
│  Kubernetes Cluster                 │
│  ┌────────────┐  ┌────────────┐     │
│  │ Mail       │  │ Mail       │     │
│  │ Reactor    │  │ Reactor    │     │
│  │ Pod 1      │  │ Pod 2      │     │
│  └────────────┘  └────────────┘     │
│         │              │             │
│  ┌──────────────────────────────┐   │
│  │  Load Balancer Service       │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
```

### Installation Methods

**1. PyPI (Recommended for users):**
```bash
pipx install mailreactor
mailreactor start
```

**2. Docker:**
```bash
docker pull mailreactor/mailreactor:latest
docker run -p 8000:8000 mailreactor/mailreactor:latest
```

**3. From Source (Development):**
```bash
git clone https://github.com/yourusername/mailreactor.git
cd mailreactor
pip install -e ".[dev]"
mailreactor dev
```

### Configuration Management

**Environment Variables:**
```bash
# Server
MAILREACTOR_HOST=0.0.0.0
MAILREACTOR_PORT=8000
MAILREACTOR_LOG_LEVEL=INFO

# Security
MAILREACTOR_API_KEY=your-secret-api-key
MAILREACTOR_PASSWORD=your-master-password  # For decrypting mailreactor.yaml

# Performance
MAILREACTOR_MAX_WORKERS=10
MAILREACTOR_REQUEST_TIMEOUT=30

# Features (Phase 2)
MAILREACTOR_ENABLE_WEBHOOKS=false
MAILREACTOR_ENABLE_IMAP_AS_DATABASE=false
```

**Account Config File (required - created by `mailreactor init`):**
```yaml
# mailreactor.yaml (project-local, in current directory)
email: user@gmail.com

imap:
  host: imap.gmail.com
  port: 993
  ssl: true
  username: user@gmail.com
  password: !encrypted gAAAAABhqK8s...  # Encrypted with master password

smtp:
  host: smtp.gmail.com
  port: 587
  starttls: true
  username: user@gmail.com
  password: !encrypted gAAAAABhSMTP...  # Encrypted with master password
```

**Multi-Account Deployment Pattern:**
```bash
# Run multiple instances for multiple accounts
# Each instance in its own directory with its own mailreactor.yaml

# Personal email (port 8000)
cd ~/mail-personal
MAILREACTOR_PASSWORD=personal-master mailreactor start --port 8000 &

# Work email (port 8001)
cd ~/mail-work
MAILREACTOR_PASSWORD=work-master mailreactor start --port 8001 &
```

## Development Environment

### Prerequisites

- **Python:** 3.10 or higher
- **pip:** Latest version (upgrade: `pip install --upgrade pip`)
- **Git:** For version control
- **Docker:** Optional, for containerized testing
- **Make:** Optional, for build automation

### Setup Commands

```bash
# Clone repository
git clone https://github.com/yourusername/mailreactor.git
cd mailreactor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies (development mode)
pip install -e ".[dev]"

# Install pre-commit hooks (code quality)
pre-commit install

# Run tests
pytest

# Initialize account configuration (interactive wizard)
mailreactor init

# Run with auto-reload (development)
mailreactor dev

# Run linting
ruff check .

# Run type checking
mypy src/

# Format code
ruff format .
```

### Development Tools

**Code Quality:**
- **ruff:** Fast Python linter and formatter
- **mypy:** Static type checker
- **pre-commit:** Git hooks for code quality

**Testing:**
- **pytest:** Test framework
- **pytest-asyncio:** Async test support
- **pytest-cov:** Coverage reporting
- **httpx:** API testing (TestClient)

**Documentation:**
- **mkdocs:** Documentation generator
- **mkdocs-material:** Material theme

### Development Workflow

1. **Create feature branch:** `git checkout -b feature/your-feature`
2. **Write tests first:** TDD approach
3. **Implement feature:** Follow patterns in this doc
4. **Run tests:** `pytest`
5. **Check types:** `mypy src/`
6. **Format code:** `ruff format .`
7. **Commit:** Pre-commit hooks run automatically
8. **Create PR:** Include tests and documentation

## Architecture Decision Records (ADRs)

### ADR-001: Use FastAPI for Web Framework

**Status:** Accepted

**Context:** Need modern Python web framework for REST API with excellent developer experience.

**Decision:** Use FastAPI 0.122.0 as the web framework.

**Rationale:**
- Automatic OpenAPI documentation generation
- Native async/await support
- Pydantic integration for validation
- Excellent performance
- Active development and community
- MIT licensed

**Consequences:**
- All API endpoints use FastAPI decorators
- Request/response validation via Pydantic
- OpenAPI docs auto-generated
- Dependency on Starlette and Pydantic

**Alternatives Considered:**
- Flask: Mature but synchronous, manual OpenAPI generation
- Django REST Framework: Too heavy, ORM not needed
- Litestar: Too new, smaller ecosystem

---

### ADR-002: Use IMAPClient with Async Executor Pattern

**Status:** Accepted

**Context:** Need reliable IMAP library compatible with FastAPI async model and MIT licensing.

**Decision:** Use IMAPClient 3.0.1 (BSD-3) with `asyncio.run_in_executor()` pattern.

**Rationale:**
- Production-stable, battle-tested library
- BSD-3 license (MIT-compatible, not GPL)
- Pythonic API with excellent parsing
- Transparent UID handling
- Comprehensive test suite
- Executor pattern maintains async benefits

**Consequences:**
- IMAP calls run in thread pool (slight overhead)
- Need to wrap all IMAPClient methods
- Good enough performance for MVP
- Could optimize with native async in Phase 2

**Alternatives Considered:**
- aioimaplib: GPL-3 licensed (incompatible with MIT goal)
- Custom async IMAP client: Too complex, reinventing wheel
- Sync-only approach: Poor FastAPI integration

---

### ADR-003: Stateless Architecture with Optional IMAP-as-Database

**Status:** Accepted

**Context:** Need to meet NFR-P1 (3-second startup) while allowing optional state persistence.

**Decision:** Stateless in-memory state management (MVP), with experimental IMAP-as-database opt-in (Phase 2).

**Rationale:**
- Zero dependencies (no Redis/PostgreSQL required)
- Instant startup (no database initialization)
- Horizontal scalability (stateless services)
- Self-hosted friendly (minimal infrastructure)
- IMAP-as-database for users who need persistence

**Consequences:**
- State lost on restart (acceptable for MVP use case)
- Cannot track webhook deliveries persistently (Phase 2 feature)
- Simpler deployment and operation
- Need to document state limitations clearly

**Alternatives Considered:**
- Redis: External dependency, slower startup
- SQLite: File I/O, not truly stateless
- PostgreSQL: Overkill, against self-hosted philosophy

---

### ADR-004: MIT License for Maximum Adoption

**Status:** Accepted

**Context:** Need to choose open-source license that maximizes developer adoption and aligns with positioning.

**Decision:** MIT License

**Rationale:**
- Simplest, most permissive license (11 lines)
- Python ecosystem norms (FastAPI, requests, Flask)
- No patent complexity (low risk domain)
- Developer-first positioning
- Competitive differentiation vs EmailEngine (AGPL)
- Maximum trust and adoption

**Consequences:**
- All dependencies must be MIT-compatible
- Users can fork and commercialize freely
- No patent protection (acceptable for email domain)
- Simple legal review for enterprises

**Alternatives Considered:**
- Apache 2.0: Patent clause complexity, less common in Python
- BSD-3: Similar to MIT, MIT slightly more popular
- GPL: Copyleft incompatible with positioning

---

### ADR-005: Typer for CLI Framework

**Status:** Accepted

**Context:** Need intuitive CLI for server management and developer operations.

**Decision:** Use Typer 0.20.0 for CLI framework.

**Rationale:**
- Same author as FastAPI (consistent philosophy)
- Type hint-based API (like FastAPI)
- Automatic help generation
- Subcommand support
- MIT licensed
- Excellent developer experience

**Consequences:**
- CLI commands use Typer decorators
- Consistent with FastAPI patterns
- Auto-generated help text
- Easy to extend with new commands

**Alternatives Considered:**
- Click: More verbose, manual help text
- argparse: Stdlib but verbose, poor DX
- Fire: Too magical, unclear API

---

### ADR-006: structlog for Structured Logging

**Status:** Accepted

**Context:** Need production-ready structured logging with async support.

**Decision:** Use structlog for all application logging.

**Rationale:**
- Structured JSON logs (machine-readable)
- Context binding (account_id, request_id)
- Async-safe
- Multiple output formats
- Excellent integration with log aggregators

**Consequences:**
- All logs use structlog API
- JSON format by default
- Need to configure processors
- Context bound to loggers

**Alternatives Considered:**
- Standard logging: Not structured, harder to parse
- loguru: Great DX but less structured
- python-json-logger: Less features than structlog

---

### ADR-007: Project-Local Configuration with Encrypted Credentials

**Status:** Accepted (Course Correction 2025-12-06, replaces original Epic 2 design)

**Context:** Original Epic 2 design used global config file (`~/.config/mailreactor/config.toml`) with account management REST API. This created complexity (hot-reload, StateManager, multi-account runtime management) that conflicted with Mail Reactor's "zero-configuration" positioning.

**Decision:** Use project-local `mailreactor.yaml` configuration with `mailreactor init` wizard and master password encryption.

**Rationale:**
- **Developer mental model:** Aligns with `git init`, `npm init`, `docker-compose.yaml` patterns
- **Simplicity:** No account management API, no runtime state, no hot-reload polling
- **Security:** Fernet + PBKDF2 encryption, master password never persisted
- **Project isolation:** Each directory = one account, config lives with usage
- **Zero-config promise:** `mailreactor init` → auto-detection → `mailreactor start`
- **Multi-account:** Multiple instances (different directories/ports) acceptable for MVP

**Consequences:**
- ✅ Simpler architecture: No StateManager, no account CRUD API, no hot-reload
- ✅ Faster implementation: 6 stories vs 8, less code to maintain
- ✅ Better UX: Wizard-driven setup, provider auto-detection
- ✅ Clearer mental model: One directory = one account
- ⚠️ Master password required at startup (env var or prompt)
- ⚠️ Multi-account via multiple instances (orchestrator can come in Phase 2)
- ⚠️ Lost master password = must re-run `mailreactor init`

**Alternatives Considered:**
- Global config + account API: Too complex, conflicts with stateless architecture
- OAuth2 only: Deferred to Phase 2, doesn't solve app password use case
- Plaintext config: Unacceptable security risk
- External KMS: Too heavy for self-hosted MVP

**Removed from Original Design:**
- `POST /accounts`, `GET /accounts`, `DELETE /accounts` REST endpoints
- `mailreactor account add/list/remove` CLI commands
- `~/.config/mailreactor/config.toml` global config
- Hot-reload polling mechanism (5-second file watching)
- StateManager with namespaced keys (`account:*`, `webhook:*`, `email:*`)
- Multi-account runtime orchestration

---

## Summary: Key Architectural Principles

1. **Developer Experience First:** Zero-config startup, intuitive APIs, excellent docs
2. **Async by Default:** FastAPI async endpoints, async SMTP, executor pattern for IMAP
3. **Type Safety Everywhere:** Pydantic models, Python type hints, mypy validation
4. **Stateless MVP:** In-memory state, no databases, 3-second startup
5. **Production-Ready Libraries:** Battle-tested dependencies (FastAPI, IMAPClient, aiosmtplib)
6. **Clear Error Handling:** Custom exception hierarchy, structured logging, user-friendly messages
7. **MIT Licensed:** Maximum adoption, Python ecosystem norms, developer trust
8. **Test-Driven:** Comprehensive test coverage, async test support, mock IMAP/SMTP

---

_Generated by BMAD Decision Architecture Workflow v1.0_  
_Date: November 25, 2025_  
_For: Mail Reactor Project_  
_Architect: Winston (BMAD AI Architect)_
