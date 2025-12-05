# Story 2.1.2: CLI Account Management with Encrypted Storage

Status: drafted

## Story

As a developer or system administrator,
I want to manage email accounts via CLI commands with encrypted password storage,
so that I can securely configure multiple accounts without restarting the service.

## Acceptance Criteria

**Given** a CLI account management system
**When** implementing encrypted account storage and management
**Then** `src/mailreactor/core/account_config.py` provides:
- TOML file operations (read/write from `~/.config/mailreactor/config.toml`)
- Encryption/decryption service using Fernet (symmetric encryption)
- Key derivation via PBKDF2 (master password + salt → Fernet key)
- Salt generation and storage in config.toml (randomly generated on first run)
- Atomic file writes (write to temp file → atomic rename)

**And** `src/mailreactor/core/account_manager.py` provides:
- In-memory account storage (dict: email → Account)
- `reload_config()` - atomic reload from disk (decrypt → update memory)
- Account CRUD operations (add/edit/remove/list)
- Connection lifecycle management (close removed accounts, start new ones)

**And** `src/mailreactor/cli/accounts.py` implements CLI commands:
- `mailreactor accounts list [--config PATH]` - displays all accounts (passwords hidden)
- `mailreactor accounts add EMAIL [--config PATH]` - runs autodiscovery, prompts for password, encrypts
- `mailreactor accounts edit EMAIL [--config PATH]` - interactive prompts for fields to change
- `mailreactor accounts remove EMAIL [--config PATH]` - deletes account from config

**And** `src/mailreactor/core/config_watcher.py` implements hot reload:
- Background thread with 5-second polling loop
- mtime-based change detection (`os.path.getmtime()`)
- Triggers `account_manager.reload_config()` on file changes
- Graceful shutdown on stop signal

**And** `src/mailreactor/api/accounts.py` implements API endpoints:
- `POST /accounts` - Create account (all fields required, no autodiscovery)
- `GET /accounts` - List all accounts (passwords omitted)
- `GET /accounts/{email}` - Get specific account
- `PUT /accounts/{email}` - Update account
- `DELETE /accounts/{email}` - Remove account
- Immediate reload triggered after writes

**And** `src/mailreactor/middleware/https.py` implements HTTPS enforcement:
- Check `X-Forwarded-Proto` header for HTTPS detection
- Reject account mutations (POST/PUT/DELETE) over HTTP in production mode
- Allow HTTP mutations on localhost (127.0.0.1) in dev mode

**And** Account encryption security:
- Master password from `MAILREACTOR_PASSWORD` env var or runtime prompt
- Master password never persisted to disk
- PBKDF2 iterations: 100,000+ (meets security standards)
- Passwords encrypted with Fernet before storage
- Passwords never appear in logs, API responses, or error messages

**And** Config file structure (`~/.config/mailreactor/config.toml`):
```toml
[mailreactor]
encryption_key_salt = "randomly-generated-on-first-run"

[[accounts]]
email = "user@example.com"  # Email is the account ID
encrypted_password = "fernet-encrypted-blob"
imap_host = "imap.gmail.com"
imap_port = 993
imap_use_tls = true
smtp_host = "smtp.gmail.com"
smtp_port = 587
smtp_use_tls = true
```

**And** CLI autodiscovery integration:
- `mailreactor accounts add` uses provider detection (from Story 2.1)
- Falls back to Mozilla Thunderbird autoconfig (from Story 2.2) if provider not found
- Prompts user for password interactively (no echo)
- Writes complete encrypted config to TOML

**And** Hot reload behavior:
- **API writes:** Write to config.toml → immediately call `reload_config()` → instant
- **CLI writes:** Write to config.toml → exit → polling detects within 5s → reload
- **Manual edits:** Edit config.toml → polling detects within 5s → reload

**And** Error handling:
- Malformed config during reload → process exits with error code (fail-fast)
- Invalid encryption → process exits with error
- Missing required fields → process exits with error
- Clear error messages guide operator to fix config

**And** Startup behavior:
- `mailreactor start` loads accounts from config at startup
- Prompts for master password if `MAILREACTOR_PASSWORD` not set
- Starts successfully with zero accounts (idle mode)
- `--account` flag removed from start/dev commands (deprecated)

**Prerequisites:** Story 2.1 (provider detection)

**Note:** This story can be implemented in parallel with Story 2.2 (Mozilla autoconfig). The CLI `add` command will initially only support provider detection from Story 2.1, and can be enhanced with Mozilla autoconfig fallback once Story 2.2 is complete.

## Tasks / Subtasks

- [ ] Create encryption service module (AC: Fernet encryption, PBKDF2 key derivation)
  - [ ] Create `src/mailreactor/core/encryption.py` module
  - [ ] Implement `generate_salt() -> str`: random bytes → base64
  - [ ] Implement `derive_key(master_password: str, salt: str) -> bytes`: PBKDF2 with 100k+ iterations
  - [ ] Implement `encrypt_password(password: str, key: bytes) -> str`: Fernet encryption
  - [ ] Implement `decrypt_password(encrypted: str, key: bytes) -> str`: Fernet decryption
  - [ ] Add error handling for invalid keys, malformed encrypted data
  - [ ] Add structlog logging (DEBUG level only - no password values)

- [ ] Create account config module (AC: TOML read/write, atomic operations)
  - [ ] Create `src/mailreactor/core/account_config.py` module
  - [ ] Implement `get_config_path() -> Path`: default ~/.config/mailreactor/config.toml
  - [ ] Implement `load_config(config_path: Path) -> Dict`: TOML → dict
  - [ ] Implement `save_config(config_path: Path, data: Dict)`: Atomic write (temp file → rename)
  - [ ] Implement `initialize_config(config_path: Path)`: Create default config with salt
  - [ ] Handle missing config file (create with defaults)
  - [ ] Add file locking for concurrent access protection
  - [ ] Add structlog logging for config operations

- [ ] Create account manager module (AC: In-memory storage, reload, CRUD)
  - [ ] Create `src/mailreactor/core/account_manager.py` module
  - [ ] Implement `AccountManager` class with in-memory dict (email → MailAccount)
  - [ ] Implement `reload_config(config_path: Path, master_password: str)`: Decrypt → update memory
  - [ ] Implement `add_account(account: MailAccount, master_password: str)`: Add to memory + persist
  - [ ] Implement `edit_account(email: str, updates: Dict, master_password: str)`: Update + persist
  - [ ] Implement `remove_account(email: str)`: Remove from memory + persist
  - [ ] Implement `list_accounts() -> List[MailAccount]`: Return all (passwords excluded)
  - [ ] Implement `get_account(email: str) -> Optional[MailAccount]`: Single account lookup
  - [ ] Add asyncio locks for thread-safe operations
  - [ ] Add connection lifecycle management (placeholder for Epic 2 stories)

- [ ] Create config watcher module (AC: 5-second polling, mtime detection)
  - [ ] Create `src/mailreactor/core/config_watcher.py` module
  - [ ] Implement `ConfigWatcher` class with background thread
  - [ ] Implement `start()`: Launch polling thread
  - [ ] Implement `stop()`: Graceful shutdown
  - [ ] Implement polling loop: 5-second interval, mtime comparison
  - [ ] Call `account_manager.reload_config()` on mtime change
  - [ ] Handle watcher errors (log but don't crash main process)
  - [ ] Add structlog logging for reload events

- [ ] Create CLI accounts commands (AC: add/edit/remove/list with autodiscovery)
  - [ ] Create `src/mailreactor/cli/accounts.py` module
  - [ ] Implement `accounts list` command: Display table of accounts (passwords hidden)
  - [ ] Implement `accounts add EMAIL` command:
    - [ ] Run provider detection (Story 2.1) or Mozilla autoconfig (Story 2.2)
    - [ ] Prompt for password interactively (getpass, no echo)
    - [ ] Create encrypted account via AccountManager
    - [ ] Display success message with account details
  - [ ] Implement `accounts edit EMAIL` command:
    - [ ] Interactive prompts for fields to change (host/port/etc)
    - [ ] Option to change password (re-encrypt)
    - [ ] Update via AccountManager
  - [ ] Implement `accounts remove EMAIL` command:
    - [ ] Confirmation prompt (y/n)
    - [ ] Remove via AccountManager
  - [ ] Add `--config PATH` option to all commands (override default location)
  - [ ] Add rich console output (tables, colors, success/error formatting)

- [ ] Create API account endpoints (AC: CRUD endpoints, HTTPS enforcement)
  - [ ] Create `src/mailreactor/api/accounts.py` router
  - [ ] Define Pydantic request/response models:
    - [ ] `AccountCreateRequest`: email, password, imap_host, imap_port, imap_use_tls, smtp_host, smtp_port, smtp_use_tls
    - [ ] `AccountUpdateRequest`: Optional fields for partial updates
    - [ ] `AccountResponse`: Account without password (for GET responses)
    - [ ] `AccountListResponse`: List of AccountResponse
  - [ ] Implement `POST /accounts`: Create account (all fields required)
  - [ ] Implement `GET /accounts`: List all accounts (passwords excluded)
  - [ ] Implement `GET /accounts/{email}`: Get single account
  - [ ] Implement `PUT /accounts/{email}`: Update account (partial allowed)
  - [ ] Implement `DELETE /accounts/{email}`: Remove account
  - [ ] Trigger immediate `reload_config()` after POST/PUT/DELETE
  - [ ] Return SuccessResponse envelopes (Story 1.7 pattern)
  - [ ] Add structlog logging for API operations

- [ ] Create HTTPS enforcement middleware (AC: X-Forwarded-Proto check)
  - [ ] Create `src/mailreactor/middleware/https.py` module
  - [ ] Implement `https_required` middleware:
    - [ ] Check `X-Forwarded-Proto` header
    - [ ] Detect production vs dev mode (from settings)
    - [ ] Allow mutations on localhost (127.0.0.1) in dev mode
    - [ ] Reject mutations over HTTP in production (403 Forbidden)
  - [ ] Apply middleware to account mutation endpoints (POST/PUT/DELETE)
  - [ ] Add structlog logging for rejected requests
  - [ ] Add clear error messages explaining HTTPS requirement

- [ ] Update start/dev commands (AC: remove --account flag, load from config)
  - [ ] Modify `src/mailreactor/cli/server.py`:
    - [ ] Remove `--account` flag from `start` command
    - [ ] Remove `--account` flag from `dev` command
    - [ ] Add config loading at startup
    - [ ] Add master password prompt if `MAILREACTOR_PASSWORD` not set
    - [ ] Initialize ConfigWatcher and start polling
    - [ ] Handle zero accounts gracefully (idle mode)
  - [ ] Update help text to mention config file location
  - [ ] Add deprecation warning if old usage detected

- [ ] Write unit tests for encryption service (AC: 15 tests per SPIKE-003)
  - [ ] Test `generate_salt()`: randomness, length, base64 format
  - [ ] Test `derive_key()`: same inputs → same key, different salts → different keys
  - [ ] Test `encrypt_password()` + `decrypt_password()`: round-trip, different passwords
  - [ ] Test encryption with invalid keys (wrong length, malformed)
  - [ ] Test decryption with wrong key (fails gracefully)
  - [ ] Test PBKDF2 iteration count (>= 100,000)
  - [ ] Test Fernet token format (base64, proper structure)
  - [ ] Test password validation (empty, very long, special characters)
  - [ ] Coverage target: 100% for encryption.py

- [ ] Write unit tests for account config module (AC: 15 tests per SPIKE-003)
  - [ ] Test `load_config()`: valid TOML, malformed TOML, missing file
  - [ ] Test `save_config()`: atomic write, temp file cleanup, file permissions
  - [ ] Test `initialize_config()`: creates default structure, generates salt
  - [ ] Test config path resolution (default, custom, env var)
  - [ ] Test concurrent writes (file locking)
  - [ ] Test TOML round-trip (write → read → same data)
  - [ ] Coverage target: 100% for account_config.py

- [ ] Write integration tests for account manager (AC: 10 tests per SPIKE-003)
  - [ ] Test full CRUD cycle: add → list → edit → remove
  - [ ] Test `reload_config()`: disk changes reflected in memory
  - [ ] Test atomic reload (old accounts → new accounts, no partial state)
  - [ ] Test encryption/decryption integration (save encrypted → reload decrypted)
  - [ ] Test multiple accounts in single config
  - [ ] Test thread safety (concurrent operations)
  - [ ] Test error handling (malformed config, wrong password)
  - [ ] Coverage target: 100% for account_manager.py

- [ ] Write integration tests for config watcher (AC: 10 tests per SPIKE-003)
  - [ ] Test polling detects mtime changes within 6 seconds (5s + 1s buffer)
  - [ ] Test reload triggered on config file modification
  - [ ] Test watcher ignores unchanged files (no unnecessary reloads)
  - [ ] Test watcher handles file deletion gracefully
  - [ ] Test watcher shutdown (clean thread termination)
  - [ ] Test concurrent API write + polling (no conflicts)
  - [ ] Coverage target: 100% for config_watcher.py

- [ ] Write E2E tests for CLI commands (AC: 8 tests per SPIKE-003)
  - [ ] Test `accounts add` → file created with encrypted password
  - [ ] Test `accounts list` → displays accounts (no passwords)
  - [ ] Test `accounts edit` → updates config file
  - [ ] Test `accounts remove` → deletes from config
  - [ ] Test autodiscovery integration (provider detection, Mozilla fallback can be added later)
  - [ ] Test interactive password prompt (mock getpass)
  - [ ] Test `--config` flag (custom path)
  - [ ] Test CLI with zero accounts (empty config)

- [ ] Write E2E tests for API endpoints (AC: 8 tests per SPIKE-003)
  - [ ] Test `POST /accounts` → config updated + immediate reload
  - [ ] Test `GET /accounts` → returns list (no passwords)
  - [ ] Test `GET /accounts/{email}` → single account
  - [ ] Test `PUT /accounts/{email}` → partial update works
  - [ ] Test `DELETE /accounts/{email}` → removed from config
  - [ ] Test API write → polling reload within 6 seconds
  - [ ] Test HTTPS enforcement (HTTP rejected in prod, allowed in dev)
  - [ ] Test multiple accounts via API

- [ ] Write security tests (AC: 5 tests per SPIKE-003)
  - [ ] Test password never in plaintext (logs, responses, errors)
  - [ ] Test PBKDF2 meets iteration minimum (100k+)
  - [ ] Test HTTPS detection with/without `X-Forwarded-Proto`
  - [ ] Test HTTP rejection in production mode
  - [ ] Test master password prompt doesn't echo to terminal

- [ ] Update documentation (AC: Clear setup and usage guide)
  - [ ] Add account management guide to user docs
  - [ ] Document config file location and structure
  - [ ] Document encryption security model
  - [ ] Document master password management (env var vs prompt)
  - [ ] Document hot reload behavior (API vs CLI vs manual)
  - [ ] Add troubleshooting section (malformed config, wrong password)
  - [ ] Update architecture.md with encryption pattern

## Dev Notes

### Learnings from Previous Stories

**From Story 2.2 (Mozilla Thunderbird Autoconfig):**
- **External API Integration**: Use aiohttp for async HTTP calls, handle network errors gracefully
- **Fallback Pattern**: Primary detection (provider) → fallback (Mozilla) → manual config
- **XML Parsing**: Use stdlib ElementTree, validate structure before parsing
- **Caching Strategy**: Cache successful lookups (short TTL) to reduce network calls
- **Testing External APIs**: Mock HTTP responses, test error conditions thoroughly

**From Story 2.1 (Provider Detection):**
- **Configuration Pattern**: YAML for static config (providers), TOML for user config (accounts)
- **Module-level Caching**: Load config once at import, cache in module variable
- **Domain Extraction**: Always lowercase, handle aliases via dictionary
- **Graceful Failures**: Return None for unknown cases, don't raise exceptions
- **Testing Approach**: Focus on behavior (our logic), not framework (Pydantic/YAML)

**Applying to Story 3.1:**
- **Encryption Pattern**: Single encryption service, reused by all modules
- **Atomic Operations**: Write to temp → rename (prevents partial reads)
- **Caching**: Master password in memory (process lifetime), never disk
- **Error Handling**: Fail-fast for malformed config (clear error → operator fix)
- **Testing**: Mock file I/O, test encryption round-trips, verify no password leaks

### Architecture Patterns and Constraints

**Encryption Pattern (from SPIKE-003):**

```python
# core/encryption.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.primitives import hashes
import base64
import secrets

def generate_salt() -> str:
    """Generate random salt for PBKDF2 (base64 encoded)."""
    return base64.b64encode(secrets.token_bytes(32)).decode('utf-8')

def derive_key(master_password: str, salt: str) -> bytes:
    """Derive Fernet key from master password + salt using PBKDF2."""
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=base64.b64decode(salt),
        iterations=100_000,  # OWASP recommendation
    )
    key = kdf.derive(master_password.encode('utf-8'))
    return base64.urlsafe_b64encode(key)

def encrypt_password(password: str, key: bytes) -> str:
    """Encrypt password with Fernet (symmetric encryption)."""
    f = Fernet(key)
    encrypted = f.encrypt(password.encode('utf-8'))
    return encrypted.decode('utf-8')

def decrypt_password(encrypted: str, key: bytes) -> str:
    """Decrypt password with Fernet."""
    f = Fernet(key)
    decrypted = f.decrypt(encrypted.encode('utf-8'))
    return decrypted.decode('utf-8')
```

**Account Manager Pattern (from SPIKE-003):**

```python
# core/account_manager.py
import asyncio
from typing import Dict, Optional, List
from pathlib import Path
import structlog

logger = structlog.get_logger(__name__)

class AccountManager:
    """Manage email accounts with encrypted storage."""
    
    def __init__(self):
        self._accounts: Dict[str, MailAccount] = {}
        self._lock = asyncio.Lock()
        self._master_password: Optional[str] = None
    
    def set_master_password(self, password: str):
        """Set master password for encryption (process lifetime)."""
        self._master_password = password
    
    async def reload_config(self, config_path: Path):
        """Reload accounts from disk (decrypt → update memory)."""
        async with self._lock:
            logger.info("reloading_config", config_path=str(config_path))
            
            # Load and decrypt
            config = load_config(config_path)
            salt = config["mailreactor"]["encryption_key_salt"]
            key = derive_key(self._master_password, salt)
            
            # Atomic swap
            new_accounts = {}
            for account_data in config.get("accounts", []):
                email = account_data["email"]
                decrypted_password = decrypt_password(
                    account_data["encrypted_password"], 
                    key
                )
                # Build MailAccount (details omitted)
                new_accounts[email] = account
            
            # Replace in-memory accounts atomically
            old_accounts = self._accounts
            self._accounts = new_accounts
            
            # Close removed account connections
            removed = set(old_accounts.keys()) - set(new_accounts.keys())
            for email in removed:
                # Close IMAP/SMTP connections (placeholder)
                logger.info("account_removed", email=email)
            
            logger.info("config_reloaded", account_count=len(self._accounts))
    
    async def add_account(self, account: MailAccount, config_path: Path):
        """Add account to memory and persist encrypted."""
        async with self._lock:
            self._accounts[account.email] = account
            await self._save_config(config_path)
    
    async def _save_config(self, config_path: Path):
        """Save all accounts to config (encrypted)."""
        # Load existing config
        config = load_config(config_path)
        salt = config["mailreactor"]["encryption_key_salt"]
        key = derive_key(self._master_password, salt)
        
        # Encrypt all accounts
        accounts_data = []
        for email, account in self._accounts.items():
            encrypted_password = encrypt_password(account.password, key)
            accounts_data.append({
                "email": email,
                "encrypted_password": encrypted_password,
                # ... other fields
            })
        
        config["accounts"] = accounts_data
        save_config(config_path, config)
```

**Config Watcher Pattern (from SPIKE-003):**

```python
# core/config_watcher.py
import threading
import time
from pathlib import Path
import structlog

logger = structlog.get_logger(__name__)

class ConfigWatcher:
    """Watch config file for changes and trigger reload."""
    
    def __init__(self, config_path: Path, account_manager):
        self.config_path = config_path
        self.account_manager = account_manager
        self._running = False
        self._thread = None
        self._last_mtime = 0
    
    def start(self):
        """Start polling thread."""
        if self.config_path.exists():
            self._last_mtime = self.config_path.stat().st_mtime
        
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        logger.info("config_watcher_started", interval_seconds=5)
    
    def stop(self):
        """Stop polling thread gracefully."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=10)
        logger.info("config_watcher_stopped")
    
    def _poll_loop(self):
        """5-second polling loop with mtime detection."""
        while self._running:
            time.sleep(5)
            
            if not self.config_path.exists():
                continue
            
            current_mtime = self.config_path.stat().st_mtime
            if current_mtime > self._last_mtime:
                logger.info("config_changed", path=str(self.config_path))
                try:
                    # Async reload from sync thread
                    asyncio.run(self.account_manager.reload_config(self.config_path))
                    self._last_mtime = current_mtime
                except Exception as e:
                    logger.error("reload_failed", error=str(e))
                    # Fail-fast: re-raise to crash process
                    raise
```

**CLI Accounts Commands Pattern:**

```python
# cli/accounts.py
import typer
from rich.console import Console
from rich.table import Table
import getpass

app = typer.Typer(name="accounts")
console = Console()

@app.command()
def list(config: str = typer.Option(None, help="Config file path")):
    """List all configured accounts."""
    config_path = Path(config) if config else get_config_path()
    account_manager = get_account_manager()  # Global singleton
    
    accounts = account_manager.list_accounts()
    
    table = Table(title="Mail Reactor Accounts")
    table.add_column("Email", style="cyan")
    table.add_column("IMAP Host", style="green")
    table.add_column("SMTP Host", style="yellow")
    table.add_column("Status", style="blue")
    
    for account in accounts:
        table.add_row(
            account.email,
            f"{account.imap_host}:{account.imap_port}",
            f"{account.smtp_host}:{account.smtp_port}",
            account.connection_status
        )
    
    console.print(table)

@app.command()
def add(
    email: str,
    config: str = typer.Option(None, help="Config file path")
):
    """Add email account with autodiscovery."""
    config_path = Path(config) if config else get_config_path()
    
    # Try provider detection (Story 2.1)
    provider_config = detect_provider(email)
    
    if not provider_config:
        # Try Mozilla autoconfig (Story 2.2)
        domain = extract_domain(email)
        provider_config = await fetch_mozilla_autoconfig(domain)
    
    if not provider_config:
        console.print(f"[red]Could not auto-detect settings for {email}[/red]")
        console.print("Please use manual configuration.")
        raise typer.Exit(1)
    
    # Prompt for password (no echo)
    password = getpass.getpass(f"Password for {email}: ")
    
    # Create account
    account = MailAccount(
        email=email,
        password=password,
        imap_host=provider_config.imap_host,
        # ... other fields
    )
    
    account_manager = get_account_manager()
    await account_manager.add_account(account, config_path)
    
    console.print(f"[green]✓[/green] Account {email} added successfully")
```

**API Accounts Endpoints Pattern:**

```python
# api/accounts.py
from fastapi import APIRouter, HTTPException, Request, Depends
from ..models.responses import SuccessResponse, ErrorResponse
from ..models.account import MailAccount, AccountResponse
from ..core.account_manager import get_account_manager
from ..middleware.https import require_https_for_mutations

router = APIRouter(prefix="/accounts", tags=["accounts"])

class AccountCreateRequest(BaseModel):
    email: EmailStr
    password: str
    imap_host: str
    imap_port: int
    imap_use_tls: bool
    smtp_host: str
    smtp_port: int
    smtp_use_tls: bool

@router.post("", response_model=SuccessResponse[AccountResponse])
async def create_account(
    request: Request,
    data: AccountCreateRequest,
    https_check = Depends(require_https_for_mutations)
):
    """Create email account (all fields required)."""
    account_manager = get_account_manager()
    
    # Check if account exists
    existing = await account_manager.get_account(data.email)
    if existing:
        raise HTTPException(status_code=409, detail="Account already exists")
    
    # Create account
    account = MailAccount(
        email=data.email,
        password=data.password,
        # ... map all fields
    )
    
    config_path = get_config_path()
    await account_manager.add_account(account, config_path)
    
    # Trigger immediate reload
    await account_manager.reload_config(config_path)
    
    # Return response (password excluded)
    response_data = AccountResponse.from_account(account)
    return SuccessResponse.create(
        data=response_data,
        request_id=request.state.request_id
    )

@router.get("", response_model=SuccessResponse[List[AccountResponse]])
async def list_accounts(request: Request):
    """List all accounts (passwords excluded)."""
    account_manager = get_account_manager()
    accounts = await account_manager.list_accounts()
    
    response_data = [AccountResponse.from_account(a) for a in accounts]
    return SuccessResponse.create(
        data=response_data,
        request_id=request.state.request_id
    )
```

**HTTPS Enforcement Middleware Pattern:**

```python
# middleware/https.py
from fastapi import Request, HTTPException
from ..config import settings

async def require_https_for_mutations(request: Request):
    """Require HTTPS for account mutations (POST/PUT/DELETE)."""
    # Check if in dev mode
    if settings.environment == "development":
        # Allow HTTP on localhost
        if request.client.host in ["127.0.0.1", "localhost"]:
            return
    
    # Production: require HTTPS
    proto = request.headers.get("X-Forwarded-Proto", "http")
    if proto != "https":
        raise HTTPException(
            status_code=403,
            detail="HTTPS required for account mutations. Use 'X-Forwarded-Proto: https' header or configure reverse proxy."
        )
```

[Source: docs/sprint-artifacts/SPIKE-003-cli-account-management.md]
[Source: docs/architecture.md#Security-Architecture]

### Project Structure Notes

**New Files (Story 3.1):**
```
src/mailreactor/
├── core/
│   ├── encryption.py          # NEW: Fernet encryption, PBKDF2 key derivation
│   ├── account_config.py      # NEW: TOML operations, atomic writes
│   ├── account_manager.py     # NEW: In-memory storage, CRUD, reload
│   └── config_watcher.py      # NEW: 5-second polling, mtime detection
├── cli/
│   └── accounts.py            # NEW: CLI commands (add/edit/remove/list)
├── api/
│   └── accounts.py            # NEW: API endpoints (CRUD)
└── middleware/
    └── https.py               # NEW: HTTPS enforcement

~/.config/mailreactor/
└── config.toml                # NEW: User config file (created at runtime)
```

**Modified Files:**
- `src/mailreactor/cli/server.py` - Remove `--account` flag, add config loading
- `src/mailreactor/main.py` - Initialize AccountManager, start ConfigWatcher
- `src/mailreactor/config.py` - Add `environment` setting (production/development)

**Dependencies:**
- `cryptography` - Fernet encryption, PBKDF2 (add to pyproject.toml)
- `toml` or `tomli` (Python 3.11+ has tomllib stdlib) - TOML parsing
- `rich` - Beautiful CLI tables and output (may already be installed)
- `aiofiles` - Async file operations (for atomic writes)

**Testing Structure:**
```
tests/
├── unit/
│   ├── test_encryption.py              # NEW: 15+ tests
│   ├── test_account_config.py          # NEW: 15+ tests
│   └── test_account_manager.py         # NEW: 10+ tests
├── integration/
│   ├── test_config_watcher.py          # NEW: 10+ tests
│   ├── test_cli_accounts.py            # NEW: 8+ tests
│   └── test_api_accounts.py            # NEW: 8+ tests
└── security/
    └── test_encryption_security.py     # NEW: 5+ tests
```

[Source: docs/architecture.md#Project-Structure]
[Source: docs/sprint-artifacts/SPIKE-003-cli-account-management.md#Implementation-Checklist]

### Technical Notes

**Key Implementation Requirements:**

1. **Encryption Security:**
   - Use `cryptography` library (industry standard, audited)
   - Fernet: Symmetric encryption (AES-128-CBC + HMAC-SHA256)
   - PBKDF2: 100,000+ iterations (OWASP recommendation)
   - Salt: 32 bytes random, base64 encoded
   - Master password: Never persisted, memory only

2. **TOML Config Structure:**
   - Single `[mailreactor]` section with `encryption_key_salt`
   - Array of `[[accounts]]` (TOML array of tables)
   - Email is account ID (unique identifier)
   - All IMAP/SMTP settings per account

3. **Atomic File Operations:**
   - Write to temp file (same filesystem as target)
   - Atomic rename (os.replace, POSIX atomic)
   - Prevents partial reads during concurrent access
   - File permissions: 0600 (user read/write only)

4. **Hot Reload Mechanism:**
   - Polling interval: 5 seconds (simple, cross-platform)
   - mtime detection: `os.path.getmtime()` comparison
   - Atomic memory swap: old dict → new dict (no partial state)
   - API writes: immediate reload (don't wait for polling)
   - CLI writes: polling detects within 6 seconds (5s + 1s buffer)

5. **Error Handling Strategy:**
   - **Fail-fast for config errors:** Malformed TOML → exit with code 1
   - **Clear error messages:** Guide operator to fix (line number, field name)
   - **Graceful for network errors:** Autodiscovery fails → manual config
   - **Never crash on reload:** Log error, keep old config, retry next poll

6. **CLI User Experience:**
   - Rich console output (colors, tables, spinners)
   - Interactive prompts (password via getpass, no echo)
   - Confirmation for destructive actions (remove account)
   - Progress indicators for network operations (autodiscovery)
   - Clear success/error messages

7. **API Design:**
   - No autodiscovery (explicit machine-to-machine interface)
   - All fields required for POST (no defaults, no magic)
   - Partial updates allowed for PUT (only changed fields)
   - Passwords in request body (plaintext over HTTPS)
   - Passwords excluded from responses (AccountResponse model)

**Testing Strategy (38 tests per SPIKE-003):**

**Unit Tests (15 encryption + 15 config = 30):**
- ✅ Test encryption round-trips (encrypt → decrypt → same password)
- ✅ Test key derivation (same inputs → same key, different salt → different key)
- ✅ Test TOML parsing (valid → dict, malformed → error)
- ✅ Test atomic writes (temp file → rename, cleanup on error)
- ❌ Don't test Fernet internals (cryptography library's job)
- ❌ Don't test TOML library (tomllib's job)

**Integration Tests (10 manager + 10 watcher = 20):**
- ✅ Test full CRUD cycle (add → reload → edit → reload → remove)
- ✅ Test polling detects changes (modify file → reload within 6s)
- ✅ Test concurrent operations (API write while polling)
- ✅ Test thread safety (multiple reload calls)
- ❌ Don't test actual IMAP/SMTP connections (that's Epic 2 stories)

**E2E Tests (8 CLI + 8 API = 16):**
- ✅ Test CLI commands end-to-end (add → list → edit → remove)
- ✅ Test API endpoints end-to-end (POST → GET → PUT → DELETE)
- ✅ Test autodiscovery integration (provider + Mozilla fallback)
- ✅ Test HTTPS enforcement (HTTP rejected in prod)
- ❌ Don't test UI rendering (Rich library's job)

**Security Tests (5):**
- ✅ Test password never in logs/responses/errors
- ✅ Test PBKDF2 iteration count >= 100,000
- ✅ Test file permissions (config.toml = 0600)
- ✅ Test master password prompt (no echo)
- ✅ Test HTTPS detection (X-Forwarded-Proto)

**Common Pitfalls to Avoid:**

1. **Race Conditions:**
   - Use asyncio locks for in-memory account dict
   - Use file locks for config file writes (flock on Unix)
   - Atomic rename prevents partial reads

2. **Password Leakage:**
   - Mark password fields with `Field(exclude=True)`
   - Never log passwords (even in DEBUG)
   - Redact passwords in error messages
   - Clear password from memory after encryption

3. **Config File Corruption:**
   - Validate TOML structure before parsing
   - Validate required fields (email, encrypted_password, hosts, ports)
   - Fail-fast with clear error message
   - Don't try to auto-fix (operator must correct)

4. **Master Password Handling:**
   - Prompt only once at startup (store in AccountManager)
   - Never write to disk (even temp files)
   - Clear from environment after reading
   - Handle Ctrl+C gracefully during prompt

5. **Polling Thread Lifecycle:**
   - Use daemon thread (exits with main process)
   - Graceful shutdown (stop signal + join)
   - Handle exceptions in thread (log + re-raise to crash)
   - Don't swallow errors (fail-fast philosophy)

**FR Coverage:**

This story implements:
- **New FR:** CLI account management (add/edit/remove/list)
- **New FR:** Encrypted password storage (Fernet + PBKDF2)
- **New FR:** Hot reload via polling (5-second interval)
- **New FR:** API account endpoints (CRUD)
- **New FR:** HTTPS enforcement for mutations

Depends on:
- FR-001: Provider auto-detection (Story 2.1)
- FR-002: Mozilla Thunderbird autoconfig (Story 2.2)

Enables:
- FR-003: Add account via REST API
- FR-006: Remove account
- FR-007: Manual configuration override (via API)

**Related Stories:**
- Story 2.1: Provider Configuration (provides autodiscovery)
- Story 2.2: Mozilla Thunderbird Autoconfig (autodiscovery fallback)
- Story 2.4: Account Connection Validation (tests encrypted credentials work)
- Story 2.5: Account Listing API (uses AccountManager)
- Story 2.7: Startup Configuration (deprecated by this story)

[Source: docs/sprint-artifacts/SPIKE-003-cli-account-management.md]
[Source: docs/architecture.md#Security-Architecture]
[Source: docs/architecture.md#Configuration-Pattern]

### References

- **SPIKE Document**: [Source: docs/sprint-artifacts/SPIKE-003-cli-account-management.md]
- **Architecture**: [Source: docs/architecture.md#Security-Architecture]
- **Configuration Pattern**: [Source: docs/architecture.md#Configuration-Pattern]
- **Epic Breakdown**: [Source: docs/epics.md#Epic-2-Email-Account-Connection]
- **Story 2.1 (Provider Detection)**: [Source: docs/sprint-artifacts/2-1-provider-configuration-and-basic-auto-detection.md]
- **Story 2.2 (Mozilla Autoconfig)**: [Source: docs/sprint-artifacts/2-2-mozilla-thunderbird-autoconfig-fallback.md]
- **Story 1.7 (Response Envelopes)**: [Source: docs/sprint-artifacts/1-7-response-envelope-and-error-handling-standards.md]
- **Cryptography Library**: https://cryptography.io/en/latest/fernet/
- **PBKDF2 (OWASP)**: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- **TOML Specification**: https://toml.io/en/
- **Rich CLI Library**: https://rich.readthedocs.io/

## Dev Agent Record

### Context Reference

- TBD: `docs/sprint-artifacts/2-1-2-cli-account-management-with-encrypted-storage.context.xml`

### Agent Model Used

TBD

### Debug Log References

TBD

### Completion Notes List

TBD

### File List

TBD

## Change Log

**2025-12-05:** Story 2.1.2 drafted by SM agent (Bob) from SPIKE-003
- Extracted requirements from SPIKE-003 (all sections)
- Aligned with architecture.md encryption and security patterns
- Incorporated learnings from Story 2.1 (config patterns) and Story 2.2 (fallback pattern)
- Key deliverables: encryption.py, account_config.py, account_manager.py, config_watcher.py, CLI commands, API endpoints, HTTPS middleware
- Implementation approach: Fernet encryption + PBKDF2 key derivation, 5-second polling for hot reload, atomic TOML writes
- Testing: 38 tests per SPIKE-003 (15 encryption, 15 config, 10 manager, 10 watcher, 8 CLI, 8 API, 5 security)
- Security focus: Master password in memory only, fail-fast on config errors, HTTPS enforcement for mutations
- Sequencing: Story 2.1.2 can run in parallel with Story 2.2 (Mozilla autoconfig). Initial implementation uses only Story 2.1 provider detection, Mozilla fallback can be added later.
- Status: drafted, ready for context generation and dev assignment
