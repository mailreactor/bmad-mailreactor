# Mail Reactor Architecture

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

# Start the server (zero configuration)
mailreactor start

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
| **Provider Detection** | JSON/YAML config | - | ACCOUNT-* | Simple, maintainable, covers Gmail/Outlook/Yahoo/iCloud/custom |
| **Credential Storage** | In-memory only (MVP) | - | AUTH-* | Per NFR-S1, stateless architecture requirement |
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
│       │   └── state_manager.py     # In-memory state (MVP)
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
│       │   ├── account_cli.py       # Account management CLI
│       │   └── utils.py             # CLI utilities
│       │
│       └── utils/                   # Shared utilities
│           ├── __init__.py
│           ├── logging.py           # structlog configuration
│           ├── providers.yaml       # Email provider configurations
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
| **ACCOUNT-\*** (Account Management) | `core/account.py`, `api/accounts.py`, `models/account.py` | FastAPI, IMAPClient, Pydantic |
| **EMAIL-SEND-\*** (Email Sending) | `core/smtp_client.py`, `api/send.py`, `models/message.py` | aiosmtplib, FastAPI, Pydantic |
| **EMAIL-RETRIEVE-\*** (Email Retrieval) | `core/imap_client.py`, `api/messages.py`, `models/message.py` | IMAPClient, asyncio executor, FastAPI |
| **EMAIL-SEARCH-\*** (Email Search) | `core/imap_client.py`, `api/messages.py` | IMAPClient SEARCH command, FastAPI query params |
| **SYSTEM-MONITOR-\*** (Health & Monitoring) | `api/health.py`, `utils/logging.py` | FastAPI, structlog |
| **INSTALL-\*** (Installation & Deployment) | `cli/server.py`, `__main__.py` | Typer, Uvicorn, setuptools |
| **AUTH-\*** (Authentication & Security) | `config.py`, `api/dependencies.py` | Pydantic Settings, FastAPI dependencies |
| **STATE-\*** (State Management) | `core/state_manager.py` | Python dict (in-memory), asyncio locks |
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

**Provider Auto-Detection**
```yaml
# utils/providers.yaml
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

yahoo:
  imap:
    host: imap.mail.yahoo.com
    port: 993
    ssl: true
  smtp:
    host: smtp.mail.yahoo.com
    port: 587
    starttls: true

# ... more providers
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

### 3. Logging Pattern
```python
# utils/logging.py
import structlog
from structlog.stdlib import BoundLogger

def configure_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

# Usage throughout application
logger: BoundLogger = structlog.get_logger(__name__)

# Context binding
logger = logger.bind(account_id=account_id, folder=folder)
logger.info("fetching_messages", limit=limit)

# Error logging
logger.error("imap_connection_failed", error=str(e), host=host, port=port)
```

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

### 5. Testing Pattern
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

### State Management (MVP - In-Memory)

**State Structure:**
```python
# core/state_manager.py
from typing import Dict
import asyncio

class StateManager:
    """Thread-safe in-memory state management"""
    
    def __init__(self):
        self._accounts: Dict[str, AccountCredentials] = {}
        self._lock = asyncio.Lock()
    
    async def add_account(self, account_id: str, credentials: AccountCredentials):
        async with self._lock:
            self._accounts[account_id] = credentials
    
    async def get_account(self, account_id: str) -> Optional[AccountCredentials]:
        async with self._lock:
            return self._accounts.get(account_id)
    
    async def remove_account(self, account_id: str):
        async with self._lock:
            self._accounts.pop(account_id, None)

# Singleton instance
state_manager = StateManager()
```

**State Lifecycle:**
1. Application starts → empty state
2. API calls add accounts → stored in-memory
3. Application stops → state lost (by design for MVP)

**Phase 2 Enhancement:** IMAP-as-database for optional persistence

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

**Account Management:**
- `POST /api/v1/accounts` - Add email account
- `GET /api/v1/accounts/{account_id}` - Get account details
- `DELETE /api/v1/accounts/{account_id}` - Remove account
- `POST /api/v1/accounts/{account_id}/test` - Test connection

**Email Retrieval:**
- `GET /api/v1/accounts/{account_id}/messages` - List messages
- `GET /api/v1/accounts/{account_id}/messages/{message_id}` - Get message
- `GET /api/v1/accounts/{account_id}/folders` - List folders
- `GET /api/v1/accounts/{account_id}/search` - Search messages

**Email Sending:**
- `POST /api/v1/accounts/{account_id}/send` - Send email
- `POST /api/v1/accounts/{account_id}/reply/{message_id}` - Reply to email
- `POST /api/v1/accounts/{account_id}/forward/{message_id}` - Forward email

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

2. **Credential Storage**
   - In-memory only (not persisted to disk)
   - Passwords marked with `exclude=True` in Pydantic
   - Never logged or serialized in responses

3. **TLS/SSL for Email**
   - IMAP: SSL by default (port 993)
   - SMTP: STARTTLS by default (port 587)
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
    volumes:
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

# Performance
MAILREACTOR_MAX_WORKERS=10
MAILREACTOR_REQUEST_TIMEOUT=30

# Features (Phase 2)
MAILREACTOR_ENABLE_WEBHOOKS=false
MAILREACTOR_ENABLE_IMAP_AS_DATABASE=false
```

**Config File (optional):**
```yaml
# mailreactor.yaml
server:
  host: 0.0.0.0
  port: 8000
  log_level: INFO

security:
  api_key: ${MAILREACTOR_API_KEY}  # From env var

performance:
  max_workers: 10
  request_timeout: 30
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
