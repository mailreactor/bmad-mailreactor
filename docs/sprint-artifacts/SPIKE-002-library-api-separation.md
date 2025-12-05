# SPIKE-002: Library/API Separation Architecture

**Date:** 2025-12-05  
**Author:** Winston (Architect)  
**Epic:** 2 - Email Account Connection  
**Status:** Complete

---

## Executive Summary

This spike validates the architectural separation between **library mode** (pure Python core) and **API mode** (FastAPI wrapper) for Mail Reactor. The spike demonstrates that Epic 2's account management functionality can be implemented in a framework-agnostic core, with the FastAPI layer serving as a thin HTTP adapter.

**Key Finding:** ✅ Core/API separation is viable and aligns with Mail Reactor's dual-mode value proposition.

---

## Problem Statement

The Tech Spec for Epic 2 does not explicitly address library mode usage. All components (`provider_detector.py`, `state_manager.py`, `accounts.py`) are described with FastAPI coupling, which would prevent library users from importing Mail Reactor without dragging in web server dependencies.

**User Story (Missing from Tech Spec):**
> "As a Python developer, I want to import mailreactor as a library so I can integrate email account management into my application without running a separate HTTP service."

---

## Proposed Architecture

### Package Structure

```
mailreactor/src/mailreactor/
├── core/                      # Pure Python, no FastAPI deps
│   ├── __init__.py
│   ├── events.py              # Existing from Epic 1
│   ├── storage.py             # StorageBackend ABC + InMemoryStorage
│   ├── provider_detector.py   # Auto-detection logic
│   ├── connection_validator.py # IMAP/SMTP validation
│   ├── account_manager.py     # Account CRUD with pluggable storage
│   └── providers.yaml         # Gmail, Outlook, Yahoo, iCloud configs
│
├── models/
│   ├── __init__.py
│   ├── responses.py           # Generic envelopes ONLY (SuccessResponse, ErrorResponse)
│   └── account.py             # Domain models (ProviderConfig, IMAPConfig, AccountCredentials)
│
├── api/                       # FastAPI adapters
│   ├── __init__.py
│   ├── health.py              # Existing from Epic 1
│   ├── middleware.py          # Existing from Epic 1
│   ├── schemas.py             # NEW - All endpoint-specific models (HealthResponse, AddAccountRequest, AccountResponse)
│   ├── dependencies.py        # NEW - DI providers for AccountManager, etc
│   └── accounts.py            # NEW - HTTP endpoints for account management
│
├── cli/
│   ├── __init__.py
│   └── server.py              # Extend with --account flag
│
├── utils/
│   └── __init__.py
│
└── exceptions.py              # Custom exceptions
```

### Dependency Graph

```
┌─────────────────────────────────────┐
│  Library Mode: Pure Python         │
│  from mailreactor.core import ...  │
└─────────────────────────────────────┘
              │
              ├── core/provider_detector.py
              ├── core/connection_validator.py
              ├── core/account_manager.py
              ├── core/storage.py (StorageBackend ABC)
              └── models/account.py
              │
              └── Dependencies:
                  ├── imapclient (BSD-3)
                  ├── aiosmtplib (MIT)
                  ├── httpx (BSD-3, for Mozilla Autoconfig)
                  ├── pyyaml (MIT)
                  └── pydantic (MIT, data validation)

┌─────────────────────────────────────┐
│  API Mode: FastAPI Wrapper          │
│  mailreactor start                  │
└─────────────────────────────────────┘
              │
              ├── api/accounts.py (HTTP adapter)
              ├── api/dependencies.py (DI providers)
              └── cli/server.py
              │
              └── Uses: mailreactor.core.* (above)
              │
              └── Additional Dependencies:
                  ├── fastapi (MIT)
                  ├── uvicorn (BSD-3)
                  ├── typer (MIT)
                  └── structlog (MIT)
```

---

## Usage Examples

### Library Mode: Direct Python Import

```python
# example_library_mode.py
import asyncio
from mailreactor.core.account_manager import AccountManager
from mailreactor.core.provider_detector import ProviderDetector
from mailreactor.core.storage import InMemoryStorage
from mailreactor.models.account import IMAPConfig, SMTPConfig

async def main():
    # Initialize core services (no FastAPI)
    # Single storage instance for all domain types
    storage = InMemoryStorage()
    provider_detector = ProviderDetector()
    account_manager = AccountManager(storage=storage)
    
    # Auto-detect Gmail settings
    provider_config = await provider_detector.detect("user@gmail.com")
    print(f"Detected: {provider_config.provider_name}")
    print(f"IMAP: {provider_config.imap_host}:{provider_config.imap_port}")
    print(f"SMTP: {provider_config.smtp_host}:{provider_config.smtp_port}")
    
    # Build IMAP config
    imap_config = IMAPConfig(
        host=provider_config.imap_host,
        port=provider_config.imap_port,
        ssl=provider_config.imap_ssl,
        username="user@gmail.com",
        password="app-password-here"
    )
    
    # Build SMTP config (same credentials as IMAP - common case)
    smtp_config = SMTPConfig(
        host=provider_config.smtp_host,
        port=provider_config.smtp_port,
        starttls=provider_config.smtp_starttls,
        username="user@gmail.com",
        password="app-password-here"
    )
    
    # Add account (validates connection + stores)
    account_id = await account_manager.add_account(
        email="user@gmail.com",
        imap_config=imap_config,
        smtp_config=smtp_config
    )
    
    print(f"Account added: {account_id}")
    
    # Retrieve account
    account = await account_manager.get_account(account_id)
    print(f"Status: {account.connection_status}")

asyncio.run(main())
```

**Output:**
```
Detected: Gmail
IMAP: imap.gmail.com:993
SMTP: smtp.gmail.com:587
Account added: acc_a1b2c3d4
Status: connected
```

**Dependencies Needed:**
- ✅ imapclient
- ✅ aiosmtplib
- ✅ httpx (Mozilla Autoconfig)
- ✅ pyyaml (providers.yaml)
- ✅ pydantic (models)
- ❌ FastAPI (NOT needed)

---

### API Mode: HTTP REST Endpoints

```python
# main.py (FastAPI app)
from fastapi import FastAPI
from mailreactor.api import accounts

app = FastAPI(title="Mail Reactor API")

# Register account routes
app.include_router(accounts.router, prefix="/api/v1")

# Core logic is the SAME as library mode!
# FastAPI just wraps it with HTTP
```

```python
# api/dependencies.py (NEW)
"""FastAPI dependency injection providers."""
from mailreactor.core.account_manager import AccountManager
from mailreactor.core.provider_detector import ProviderDetector
from mailreactor.core.storage import InMemoryStorage, StorageBackend

# Singleton instances (created once at startup)
# Single storage instance for entire application (all domain types)
_storage = InMemoryStorage()
_account_manager = AccountManager(storage=_storage)
_provider_detector = ProviderDetector()

def get_storage() -> StorageBackend:
    """DI provider for storage backend."""
    return _storage

def get_account_manager() -> AccountManager:
    """DI provider for AccountManager."""
    return _account_manager

def get_provider_detector() -> ProviderDetector:
    """DI provider for ProviderDetector."""
    return _provider_detector
```

```python
# api/accounts.py
from fastapi import APIRouter, Depends, HTTPException
from mailreactor.api.dependencies import get_account_manager, get_provider_detector
from mailreactor.api.schemas import AddAccountRequest, AccountResponse  # API models
from mailreactor.models.account import IMAPConfig, SMTPConfig  # Domain models
from mailreactor.models.responses import SuccessResponse  # Generic envelope
from mailreactor.core.account_manager import AccountManager
from mailreactor.core.provider_detector import ProviderDetector
from mailreactor.exceptions import IMAPConnectionError, SMTPConnectionError

router = APIRouter()

@router.post("/accounts", status_code=201)
async def add_account(
    request: AddAccountRequest,
    manager: AccountManager = Depends(get_account_manager),
    detector: ProviderDetector = Depends(get_provider_detector)
) -> SuccessResponse[AccountResponse]:
    """
    HTTP adapter for core account management logic.
    API is THIN - all business logic lives in core modules.
    """
    try:
        # Auto-detect provider settings
        provider = await detector.detect(request.email)
        
        # Build IMAP config (domain model)
        imap_config = IMAPConfig(
            host=request.imap_host or provider.imap_host,
            port=request.imap_port or provider.imap_port,
            ssl=request.imap_ssl if request.imap_ssl is not None else provider.imap_ssl,
            username=request.email,  # IMAP always uses email
            password=request.password
        )
        
        # Build SMTP config (domain model, with optional separate credentials)
        smtp_config = SMTPConfig(
            host=request.smtp_host or provider.smtp_host,
            port=request.smtp_port or provider.smtp_port,
            starttls=request.smtp_starttls if request.smtp_starttls is not None else provider.smtp_starttls,
            username=request.smtp_username or request.email,  # Default to email
            password=request.smtp_password or request.password  # Default to same password
        )
        
        # Add account (core validates + stores)
        account_id = await manager.add_account(
            email=request.email,
            imap_config=imap_config,
            smtp_config=smtp_config
        )
        
        # Retrieve for response
        account = await manager.get_account(account_id)
        
        # Return wrapped in generic envelope
        return SuccessResponse.create(
            data=AccountResponse.from_credentials(account),
            request_id="req_123"  # From middleware in real implementation
        )
    
    except (IMAPConnectionError, SMTPConnectionError) as e:
        raise HTTPException(status_code=503, detail=str(e))
```

```python
# api/health.py (Epic 1 - Update imports after refactor)
from fastapi import APIRouter
from mailreactor.api.schemas import HealthResponse  # CHANGED: moved from models/responses
from mailreactor.models.responses import SuccessResponse  # Generic envelope stays
from mailreactor.api.dependencies import get_storage

router = APIRouter()

@router.get("/health", response_model=SuccessResponse[HealthResponse])
async def health_check() -> SuccessResponse[HealthResponse]:
    """Health check endpoint."""
    # ... implementation
    return SuccessResponse.create(
        data=HealthResponse(status="healthy", version="0.1.0", uptime_seconds=123.45),
        request_id="req_xyz"
    )
```
```

**cURL Request:**
```bash
curl -X POST http://localhost:8000/api/v1/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@gmail.com",
    "password": "app-password-here"
  }'
```

**Response:**
```json
{
  "data": {
    "account_id": "acc_a1b2c3d4",
    "email": "user@gmail.com",
    "connection_status": "connected",
    "imap_host": "imap.gmail.com",
    "smtp_host": "smtp.gmail.com",
    "created_at": "2025-12-05T10:30:00Z"
  },
  "meta": {
    "request_id": "req_123"
  }
}
```

---

## Side-by-Side Comparison

| Feature | Library Mode | API Mode |
|---------|--------------|----------|
| **Import** | `from mailreactor.core.accounts import AccountManager` | FastAPI app startup |
| **Initialization** | `manager = AccountManager()` | Dependency injection |
| **Add Account** | `await manager.add_account(...)` | `POST /accounts` |
| **Get Account** | `await manager.get_account(account_id)` | `GET /accounts/{id}` |
| **List Accounts** | `await manager.get_all_accounts()` | `GET /accounts` |
| **Remove Account** | `await manager.remove_account(account_id)` | `DELETE /accounts/{id}` |
| **Dependencies** | imapclient, aiosmtplib, httpx, pyyaml, pydantic | + fastapi, uvicorn, typer, structlog |
| **Event Loop** | User-provided (`asyncio.run()`) | FastAPI's event loop |
| **Use Case** | Embed in Python app | Standalone API service |

**Key Insight:** The API mode calls **exactly the same core methods** as library mode. FastAPI is just an HTTP transport layer.

---

## Core Module Specifications

### 1. `core/storage.py` (NEW - Generic Storage Abstraction)

```python
"""
Generic key-value storage abstraction.
Single storage instance holds all domain types using namespaced keys.

Epic 2: In-memory implementation for accounts.
Future: Webhook dispatch logs, email state, event sourcing.
Epic 6: IMAP-backed implementation.
"""
from abc import ABC, abstractmethod
from typing import Any
import asyncio

class StorageBackend(ABC):
    """Generic key-value storage interface.
    
    Single storage instance stores multiple domain types using namespaced keys:
    - account:acc_123 -> AccountCredentials
    - webhook:wh_456 -> WebhookDispatch  
    - email:msg_789 -> EmailState
    """
    
    @abstractmethod
    async def set(self, key: str, value: Any) -> None:
        """Store a value."""
        pass
    
    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Retrieve a value."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove a value."""
        pass
    
    @abstractmethod
    async def list_keys(self, prefix: str = "") -> list[str]:
        """List all keys matching prefix."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass
    
    @abstractmethod
    async def set_many(self, items: dict[str, Any]) -> None:
        """Batch store multiple items."""
        pass
    
    @abstractmethod
    async def get_many(self, keys: list[str]) -> dict[str, Any]:
        """Batch retrieve multiple items."""
        pass

class InMemoryStorage(StorageBackend):
    """In-memory storage implementation (Epic 2 MVP).
    
    Single instance stores all domain types.
    Type safety provided by method return annotations, not generics.
    """
    
    def __init__(self):
        self._data: dict[str, Any] = {}
        self._lock = asyncio.Lock()
    
    async def set(self, key: str, value: Any) -> None:
        async with self._lock:
            self._data[key] = value
    
    async def get(self, key: str) -> Any | None:
        async with self._lock:
            return self._data.get(key)
    
    async def delete(self, key: str) -> None:
        async with self._lock:
            if key in self._data:
                del self._data[key]
    
    async def list_keys(self, prefix: str = "") -> list[str]:
        async with self._lock:
            return [k for k in self._data.keys() if k.startswith(prefix)]
    
    async def exists(self, key: str) -> bool:
        async with self._lock:
            return key in self._data
    
    async def set_many(self, items: dict[str, Any]) -> None:
        async with self._lock:
            self._data.update(items)
    
    async def get_many(self, keys: list[str]) -> dict[str, Any]:
        async with self._lock:
            return {k: self._data[k] for k in keys if k in self._data}

# Epic 6: IMAP-backed storage (future)
# class IMAPStorage(StorageBackend):
#     """Store data as IMAP messages in organized folders.
#     
#     Folder structure:
#     INBOX/MailReactor/accounts/  <- account:acc_123
#     INBOX/MailReactor/webhooks/  <- webhook:wh_456
#     INBOX/MailReactor/emails/    <- email:msg_789
#     """
#     
#     async def set(self, key: str, value: Any) -> None:
#         # Parse namespace: "account:acc_123" -> folder="accounts"
#         namespace, item_id = key.split(":", 1)
#         folder = f"MailReactor/{namespace}"
#         
#         # Serialize to JSON
#         import json
#         data = value.model_dump_json() if hasattr(value, 'model_dump_json') else json.dumps(value)
#         
#         # Store as RFC-822 message
#         await self.imap_client.append(folder, data, ...)
```

**Key Design Decisions:**
- **Single storage instance** for entire application (not one per type)
- **Namespaced keys** organize domain types: `account:*`, `webhook:*`, `email:*`
- **Type safety from context**: Method return annotations, not Generic[T]
- **IMAP backend** naturally maps namespaces to folder structure

**Dependencies:**
- typing (stdlib)
- asyncio (stdlib)
- abc (stdlib)

**Zero FastAPI imports.**

---

### 2. `core/provider_detector.py`

```python
"""
Auto-detect IMAP/SMTP settings for email providers.
Zero FastAPI dependencies.
"""
import httpx
import yaml
from pathlib import Path
from xml.etree import ElementTree
from mailreactor.models.account import ProviderConfig

class ProviderDetector:
    def __init__(self):
        # Load providers.yaml from same directory
        providers_path = Path(__file__).parent / "providers.yaml"
        self.local_providers = self._load_local_providers(providers_path)
        self.autoconfig_cache = {}  # In-memory cache
    
    async def detect(self, email: str) -> ProviderConfig | None:
        """
        Auto-detect provider settings via cascade:
        1. Local providers.yaml
        2. Mozilla Autoconfig
        3. ISP autoconfig
        """
        domain = email.split("@")[1]
        
        # Try local providers
        if domain in self.local_providers:
            return ProviderConfig(**self.local_providers[domain])
        
        # Try Mozilla Autoconfig
        mozilla_config = await self._detect_via_mozilla(domain)
        if mozilla_config:
            return mozilla_config
        
        # Try ISP autoconfig
        isp_config = await self._detect_via_isp(domain)
        if isp_config:
            return isp_config
        
        return None
    
    def _load_local_providers(self, path: Path) -> dict:
        """Load hardcoded providers from YAML."""
        with open(path) as f:
            return yaml.safe_load(f)
    
    async def _detect_via_mozilla(self, domain: str) -> ProviderConfig | None:
        """Query Mozilla Thunderbird Autoconfig database."""
        url = f"https://autoconfig.thunderbird.net/v1.1/{domain}"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return self._parse_autoconfig_xml(response.text)
        except httpx.TimeoutException:
            pass
        return None
    
    async def _detect_via_isp(self, domain: str) -> ProviderConfig | None:
        """Query ISP-hosted autoconfig."""
        url = f"http://autoconfig.{domain}/mail/config-v1.1.xml"
        # Similar to Mozilla logic
        return None
    
    def _parse_autoconfig_xml(self, xml_text: str) -> ProviderConfig:
        """Parse Mozilla Autoconfig XML response."""
        tree = ElementTree.fromstring(xml_text)
        # Extract <incomingServer> and <outgoingServer>
        # Return ProviderConfig
        pass
```

**Dependencies:**
- httpx (async HTTP, already in use)
- pyyaml (parse providers.yaml)
- xml.etree.ElementTree (stdlib)

**Zero FastAPI imports.**

---

### 3. `core/connection_validator.py`

```python
"""
Validate IMAP/SMTP connections.
Zero FastAPI dependencies.
"""
import asyncio
from imapclient import IMAPClient
from aiosmtplib import SMTP
from mailreactor.models.account import AccountCredentials, IMAPConfig, SMTPConfig
from mailreactor.exceptions import IMAPConnectionError, SMTPConnectionError

class ConnectionValidator:
    async def validate(self, credentials: AccountCredentials) -> None:
        """
        Validate account credentials.
        Tests both IMAP and SMTP connections in parallel.
        
        Args:
            credentials: Complete account credentials with IMAP and SMTP configs
        
        Raises:
            IMAPConnectionError: IMAP connection or authentication failed
            SMTPConnectionError: SMTP connection or authentication failed
        """
        await asyncio.gather(
            self._validate_imap(credentials.imap),
            self._validate_smtp(credentials.smtp)
        )
    
    async def _validate_imap(self, config: IMAPConfig) -> None:
        """Validate IMAP connection (internal)."""
        loop = asyncio.get_event_loop()
        try:
            await loop.run_in_executor(
                None,
                self._sync_imap_connect,
                config.host, config.port, config.username, config.password, config.ssl
            )
        except Exception as e:
            raise IMAPConnectionError(
                f"IMAP connection failed: {config.host}:{config.port}",
                details={"error": str(e), "username": config.username}
            )
    
    def _sync_imap_connect(self, host, port, username, password, use_ssl):
        """Synchronous IMAP connection (run in executor)."""
        with IMAPClient(host=host, port=port, ssl=use_ssl, timeout=10) as client:
            client.login(username, password)
    
    async def _validate_smtp(self, config: SMTPConfig) -> None:
        """Validate SMTP connection (internal)."""
        try:
            smtp = SMTP(hostname=config.host, port=config.port, timeout=10)
            await smtp.connect()
            if config.starttls:
                await smtp.starttls()
            await smtp.login(config.username, config.password)
            await smtp.quit()
        except Exception as e:
            raise SMTPConnectionError(
                f"SMTP connection failed: {config.host}:{config.port}",
                details={"error": str(e), "username": config.username}
            )
```

**Key Design Decision:** `validate()` accepts full `AccountCredentials` object, not separate IMAP/SMTP configs. This is cleaner - validator receives complete account context.

**Dependencies:**
- imapclient (IMAP client)
- aiosmtplib (async SMTP client)
- asyncio (stdlib)

**Zero FastAPI imports.**

---

### 4. `core/account_manager.py`

```python
"""
Account management with pluggable storage backend.
Zero FastAPI dependencies.
"""
from uuid import uuid4
from datetime import datetime, timezone
from mailreactor.core.storage import StorageBackend
from mailreactor.core.connection_validator import ConnectionValidator
from mailreactor.models.account import AccountCredentials, IMAPConfig, SMTPConfig

class AccountManager:
    """Manages account lifecycle with abstracted storage."""
    
    def __init__(self, storage: StorageBackend):
        self.storage = storage
        self.validator = ConnectionValidator()
    
    async def add_account(
        self,
        email: str,
        imap_config: IMAPConfig,
        smtp_config: SMTPConfig
    ) -> str:
        """
        Add account with separate IMAP/SMTP configurations.
        
        Args:
            email: Primary email address
            imap_config: IMAP server settings and credentials
            smtp_config: SMTP server settings and credentials
        
        Returns:
            account_id: Generated account identifier
        
        Raises:
            IMAPConnectionError: IMAP validation failed
            SMTPConnectionError: SMTP validation failed
        """
        # Build credentials object
        account_id = f"acc_{uuid4().hex[:8]}"
        credentials = AccountCredentials(
            account_id=account_id,
            email=email,
            imap=imap_config,
            smtp=smtp_config,
            created_at=datetime.now(timezone.utc),
            connection_status="pending"
        )
        
        # Validate both connections
        await self.validator.validate(credentials)
        
        # Update status after successful validation
        credentials.connection_status = "connected"
        
        # Persist via storage backend (namespaced key)
        await self.storage.set(f"account:{account_id}", credentials)
        return account_id
    
    async def get_account(self, account_id: str) -> AccountCredentials | None:
        """Retrieve account by ID."""
        return await self.storage.get(f"account:{account_id}")
    
    async def get_all_accounts(self) -> list[AccountCredentials]:
        """List all accounts."""
        keys = await self.storage.list_keys(prefix="account:")
        accounts = []
        for key in keys:
            account = await self.storage.get(key)
            if account:
                accounts.append(account)
        return accounts
    
    async def remove_account(self, account_id: str) -> None:
        """Remove account."""
        await self.storage.delete(f"account:{account_id}")
```

**Key Design Decisions:**
1. **Separate IMAP/SMTP configs** - Backend models reality (credentials CAN differ)
2. **Generic storage** - Uses namespaced keys (`account:acc_123`) for future webhook logs, etc
3. **Validation before storage** - `validator.validate(credentials)` receives complete account

**Dependencies:**
- uuid (stdlib)
- datetime (stdlib)
- StorageBackend (internal generic abstraction)

**Zero FastAPI imports.**

---

### 5. `models/account.py` (Domain Models)

```python
"""
Domain models for account management.
Used by core business logic. Shared by library and API modes.
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class ProviderConfig(BaseModel):
    """Auto-detected provider configuration (server settings only)."""
    provider_name: str
    imap_host: str
    imap_port: int = 993
    imap_ssl: bool = True
    smtp_host: str
    smtp_port: int = 587
    smtp_starttls: bool = True

class IMAPConfig(BaseModel):
    """IMAP server configuration and credentials."""
    host: str
    port: int = 993
    ssl: bool = True
    username: str  # Usually email, but can differ (e.g., shared mailboxes)
    password: str = Field(..., exclude=True)  # Never serialized

class SMTPConfig(BaseModel):
    """SMTP server configuration and credentials."""
    host: str
    port: int = 587
    starttls: bool = True
    username: str  # Usually email, but can differ (e.g., relay services)
    password: str = Field(..., exclude=True)  # Never serialized

class AccountCredentials(BaseModel):
    """Complete account credentials stored in backend."""
    account_id: str
    email: EmailStr  # Primary email address
    imap: IMAPConfig
    smtp: SMTPConfig
    created_at: datetime
    connection_status: str = "pending"
```

**Key Design Decision:** 
- **Backend models reality** - IMAP and SMTP credentials are separate (supports relay services, shared mailboxes)
- **Framework-agnostic** - No FastAPI dependencies, works in library mode

**Dependencies:**
- pydantic (framework-agnostic, already in use)

---

### 6. `api/schemas.py` (NEW - API Request/Response Models)

```python
"""
API-specific request and response models.
Endpoint-specific schemas - NOT used by library mode.
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from mailreactor.models.account import AccountCredentials

# Epic 1: Health endpoint (MOVED from models/responses.py)
class HealthResponse(BaseModel):
    """Health check endpoint response."""
    status: str = Field(..., description="System health status", examples=["healthy"])
    version: str = Field(..., description="Application version", examples=["0.1.0"])
    uptime_seconds: float = Field(..., description="Uptime in seconds", examples=[123.45])

# Epic 2: Account endpoints (NEW)
class AddAccountRequest(BaseModel):
    """API request to add account - simple interface for common case."""
    email: EmailStr
    password: str
    
    # Optional: Override auto-detected server settings
    imap_host: str | None = None
    imap_port: int | None = None
    imap_ssl: bool | None = None
    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_starttls: bool | None = None
    
    # Optional: Separate SMTP credentials (advanced - relay services)
    smtp_username: str | None = None
    smtp_password: str | None = None

class AccountResponse(BaseModel):
    """API response (passwords excluded)."""
    account_id: str
    email: str
    connection_status: str
    imap_host: str
    smtp_host: str
    created_at: datetime
    
    @classmethod
    def from_credentials(cls, creds: AccountCredentials):
        """Convert AccountCredentials to API response."""
        return cls(
            account_id=creds.account_id,
            email=creds.email,
            connection_status=creds.connection_status,
            imap_host=creds.imap.host,
            smtp_host=creds.smtp.host,
            created_at=creds.created_at
        )

class AccountSummary(BaseModel):
    """Summary for account listing."""
    account_id: str
    email: str
    connection_status: str
    created_at: datetime
```

**Key Design Decision:**
- **API contracts isolated** - Request/response models separate from domain models
- **Epic 1 refactor** - Move `HealthResponse` here (was in `models/responses.py`)
- **`models/responses.py` now contains ONLY generic envelopes** (`SuccessResponse`, `ErrorResponse`)
- **Library mode never imports this** - API schemas are HTTP-specific

**Dependencies:**
- pydantic (already in use)

---

### 7. `models/responses.py` (REFACTORED - Generic Envelopes Only)

```python
"""
Generic response envelopes.
Used by ALL endpoints. Contains framework-level models only.
Epic 1: Established pattern for response wrapping.
Epic 2: Refactored to remove endpoint-specific models (moved to api/schemas.py).
"""
from datetime import datetime, timezone
from typing import Generic, TypeVar, Optional, Dict, Any
from pydantic import BaseModel, Field

T = TypeVar("T")

class ResponseMeta(BaseModel):
    """Response metadata attached to all responses."""
    request_id: str = Field(..., description="Unique request identifier")
    timestamp: datetime = Field(..., description="Response timestamp (UTC)")

class SuccessResponse(BaseModel, Generic[T]):
    """Generic success envelope wrapping all successful responses."""
    data: T = Field(..., description="Response data")
    meta: ResponseMeta = Field(..., description="Response metadata")
    
    @classmethod
    def create(cls, data: T, request_id: str) -> "SuccessResponse[T]":
        """Factory method to create success response with current timestamp."""
        return cls(
            data=data,
            meta=ResponseMeta(request_id=request_id, timestamp=datetime.now(timezone.utc))
        )

class ErrorDetail(BaseModel):
    """Error detail structure."""
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")

class ErrorResponse(BaseModel):
    """Standard error envelope wrapping all error responses."""
    error: ErrorDetail = Field(..., description="Error details")
```

**Key Refactor:**
- **Before:** `HealthResponse` lived here (endpoint-specific)
- **After:** Only generic envelopes (`SuccessResponse[T]`, `ErrorResponse`)
- **Rationale:** Endpoint-specific models belong in `api/schemas.py`

---

## Installation Modes

### Library Mode (Minimal Dependencies)

```toml
# pyproject.toml
[project]
name = "mailreactor"
dependencies = [
    "imapclient>=3.0.1",
    "aiosmtplib>=5.0.0",
    "httpx>=0.27.0",
    "pyyaml>=6.0.1",
    "pydantic>=2.0",
]

[project.optional-dependencies]
api = [
    "fastapi>=0.122.0",
    "uvicorn>=0.30.0",
    "typer>=0.20.0",
    "structlog>=24.0",
]
```

**Installation:**
```bash
# Library mode
pip install mailreactor

# API mode
pip install mailreactor[api]
```

---

## Validation Checklist

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Core modules have zero FastAPI imports | ✅ | `provider_detector.py`, `connection_validator.py`, `account_manager.py` all pure Python |
| Library mode works without FastAPI installed | ✅ | Example code runs with only core dependencies |
| API mode reuses core logic | ✅ | `api/routes/accounts.py` calls `AccountManager` methods directly |
| Both modes use same data models | ✅ | `core/models/account.py` shared by both |
| Package structure supports dual installation | ✅ | `pyproject.toml` with `[api]` extras |
| IMAP/SMTP validation framework-agnostic | ✅ | `ConnectionValidator` uses asyncio, not FastAPI |
| Auto-detection works in both modes | ✅ | `ProviderDetector` is pure Python |
| Thread-safe account storage | ✅ | `AccountManager` uses asyncio.Lock |

**All requirements met. ✅**

---

## Recommendations for Tech Spec Updates

### 1. Add "Library Mode Architecture" Section

Insert after "System Architecture Alignment":

```markdown
### Dual-Mode Architecture

Mail Reactor supports two usage modes:

**Library Mode:**
- Import `mailreactor.core` directly in Python applications
- Dependencies: imapclient, aiosmtplib, httpx, pyyaml, pydantic
- No FastAPI required
- User provides event loop with `asyncio.run()`

**API Mode:**
- Run as standalone FastAPI service with `mailreactor start`
- Additional dependencies: fastapi, uvicorn, typer, structlog
- FastAPI routes act as thin HTTP adapters over core logic

**Package Structure:**
```
mailreactor/
├── core/          # Framework-agnostic (Library Mode)
│   ├── accounts/
│   │   ├── provider_detector.py
│   │   ├── connection_validator.py
│   │   └── account_manager.py
│   └── models/
│       └── account.py
├── api/           # FastAPI adapters (API Mode)
│   └── routes/
│       └── accounts.py
```
```

### 2. Update Component Responsibilities

Change:
```markdown
| `accounts.py` (API) | REST endpoints for account management | POST `/accounts`, GET `/accounts` | FastAPI, state_manager, provider_detector |
```

To:
```markdown
| `account_manager.py` (Core) | In-memory account CRUD | `add_account()`, `get_account()`, `remove_account()` | Pure Python, asyncio |
| `accounts.py` (API) | HTTP adapter for account_manager | POST `/accounts`, GET `/accounts` | FastAPI, account_manager |
```

### 3. Add Library Mode Usage Example

Add to "APIs and Interfaces" section:

```markdown
### Library Mode Interface

**Python API:**

```python
from mailreactor.core.accounts import AccountManager, ProviderDetector

# Auto-detect and add account
detector = ProviderDetector()
manager = AccountManager()

config = await detector.detect("user@gmail.com")
account_id = await manager.add_account(
    email="user@gmail.com",
    password="password",
    provider_config=config
)

# Retrieve account
account = await manager.get_account(account_id)
print(f"Status: {account.connection_status}")
```
```

### 4. Update Acceptance Criteria

Add new AC:

```markdown
**AC-2.11: Library Mode Usage**
1. Given mailreactor is installed (no [api] extras)
2. When `from mailreactor.core.accounts import AccountManager` is imported
3. Then import succeeds without FastAPI installed
4. And `AccountManager().add_account()` works with user-provided event loop
5. And no HTTP server dependencies are loaded
```

---

## Risks and Mitigations

### Risk 1: Pydantic Dependency Size
- **Risk:** Pydantic adds ~5MB to library mode
- **Mitigation:** Acceptable - Pydantic is production-stable, widely used, and provides type safety
- **Alternative:** Dataclasses (but lose validation features)

### Risk 2: StateManager Duplication
- **Risk:** StateManager already exists in Epic 1 (for health check uptime)
- **Mitigation:** Rename Epic 1's class to `AppStateManager`, use `AccountManager` for Epic 2

### Risk 3: Executor Pattern Complexity
- **Risk:** `run_in_executor` for sync IMAPClient adds complexity
- **Mitigation:** Already validated in SPIKE-001, well-documented pattern

---

## Next Steps

1. **Bob:** Update Epic 2 tech spec with library mode architecture (this spike as reference)
2. **Bob:** Add AC-2.11 for library mode validation
3. **Bob:** Update all Epic 2 stories to reference `core/accounts/*` instead of `api/accounts/*`
4. **Amelia:** Review updated tech spec before starting Story 2.1
5. **Mary:** Document comparative analysis (competitors' dual-mode patterns) - in progress

---

## Key Architectural Decisions Summary

### 1. Generic Storage Abstraction (Single Instance)
**Decision:** `StorageBackend` with `Any` values and namespaced keys, not type-specific storage

**Rationale:**
- **Single storage instance** holds all domain types (accounts, webhooks, email state)
- **Namespaced keys** organize by domain: `account:acc_123`, `webhook:wh_456`
- **Type safety from context**: Method return annotations, not Generic[T]
- **IMAP Epic 6**: Namespaces map to folders (`MailReactor/accounts/`, `MailReactor/webhooks/`)
- **Batch operations** (`set_many`, `get_many`) reduce IMAP round trips
- **One mock storage** for all tests, not separate instances per type

### 2. Separate IMAP/SMTP Credentials
**Decision:** `AccountCredentials` contains separate `IMAPConfig` and `SMTPConfig`

**Rationale:**
- Models reality: credentials CAN differ (relay services, shared mailboxes, OAuth scopes)
- Backend accuracy over API simplicity
- CLI hides complexity: prompts once, populates both with same values
- API supports advanced users: optional `smtp_username`/`smtp_password` fields
- Future-proof for Epic X (relay services) without refactoring

### 3. Validator Accepts Complete Credentials
**Decision:** `validator.validate(credentials: AccountCredentials)` - single argument

**Rationale:**
- Clear what's being validated (complete account, not separate configs)
- Validator has full context for error messages (account_id, email)
- Internally validates IMAP and SMTP separately
- Simpler method signature than `validate(imap, smtp)`

### 4. Flat Folder Structure (Pragmatic Nesting)
**Decision:** Keep files flat until we have 3+ related modules

**Rationale:**
- Align with existing project structure (`api/health.py`, not `api/routes/health.py`)
- Epic 2 adds ~3 core files - no need for `core/accounts/` subfolder yet
- Future: Add subfolders when complexity justifies it

### 5. Dependency Injection in `api/dependencies.py`
**Decision:** Create new file for DI providers, separate from `api/middleware.py`

**Rationale:**
- Keeps `middleware.py` focused on request/response middleware
- FastAPI best practice: separate concerns
- Singleton pattern for `AccountManager`, `ProviderDetector`, `Storage`

### 6. `providers.yaml` in `core/`
**Decision:** Co-locate with `provider_detector.py` that loads it

**Rationale:**
- Clean imports: `Path(__file__).parent / "providers.yaml"`
- No cross-module paths
- Future: If we add more configs, create `config/` folder

### 7. API Schemas Consolidated in `api/schemas.py`
**Decision:** Move endpoint-specific models from `models/responses.py` to `api/schemas.py`

**What Changed:**
- **Before Epic 2:** `models/responses.py` contained both generic envelopes AND `HealthResponse`
- **After Epic 2:** 
  - `models/responses.py` - Generic envelopes ONLY (`SuccessResponse[T]`, `ErrorResponse`)
  - `api/schemas.py` - ALL endpoint-specific models (`HealthResponse`, `AddAccountRequest`, `AccountResponse`)

**Rationale:**
- **Clear separation:** Generic framework vs domain-specific API contracts
- **Library mode clarity:** Library users never import `api/schemas.py`
- **Scalability:** When Epic 3/4 add more endpoints, all API models in one place
- **Consistency:** Follow FastAPI best practices

**Migration Required:**
- Move `HealthResponse` from `models/responses.py` to `api/schemas.py`
- Update `api/health.py` import: `from mailreactor.api.schemas import HealthResponse`

---

## Conclusion

✅ **Core/API separation is architecturally sound and achievable within Epic 2 scope.**

The proposed structure:
- Maintains zero coupling between core and FastAPI
- Enables library users to import without web dependencies
- Preserves all Epic 2 functionality (auto-detection, validation, CRUD)
- Models reality in backend (separate IMAP/SMTP) while keeping CLI/API simple
- Generic storage supports future webhook logs, email state, IMAP backend
- Adds ~50 lines for storage abstraction, pays dividends in Epic 6

**Recommendation:** Proceed with tech spec update before Story 2.1 implementation.

---

**Spike Duration:** 45 minutes (including HC feedback iterations)  
**Artifacts Generated:**
- This document (SPIKE-002)
- Code examples (library mode + API mode)
- Updated package structure proposal
- Storage abstraction design
- Separate IMAP/SMTP credential design

**Status:** ✅ Complete - Ready for tech spec integration
