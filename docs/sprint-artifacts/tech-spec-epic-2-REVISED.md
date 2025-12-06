# Epic Technical Specification: Email Account Connection

Date: 2025-12-05
Author: John (PM)
Epic ID: 2
Status: Draft - Course Corrected
Replaces: tech-spec-epic-2.md (2025-12-04)

---

## Overview

Epic 2 enables developers to connect their email accounts to Mail Reactor with minimal friction through an elegant `mailreactor init` wizard. The epic implements intelligent auto-detection of IMAP/SMTP settings (local providers → Mozilla Autoconfig → ISP fallback → manual configuration) that covers thousands of email providers while maintaining the zero-configuration philosophy critical to Mail Reactor's developer experience.

This epic delivers the foundation for all email operations by establishing secure, validated connections to email accounts through a **project-local configuration file** (`mailreactor.yaml`). The design follows the mental model of tools like `git init`, `npm init`, and `docker-compose.yaml` - configuration lives where you use it, not in a global location.

**Key Design Principle:** Single account per Mail Reactor instance. Multi-account support is achieved by running multiple instances (different directories, different ports) rather than complex runtime account management.

**Security Model:** Account passwords are encrypted at rest using Fernet symmetric encryption with PBKDF2 key derivation from a user-provided master password. Master password supplied via `MAILREACTOR_PASSWORD` environment variable or interactive prompt at startup.

## Objectives and Scope

**In Scope:**
- `mailreactor init` interactive wizard with smart prompts based on auto-detection
- Auto-detection for major providers (Gmail, Outlook, Yahoo, iCloud) via local YAML configuration
- Mozilla Thunderbird Autoconfig database integration for broader provider coverage (1000+ providers)
- ISP-hosted autoconfig fallback for provider-specific configurations
- Manual IMAP/SMTP configuration for unknown providers
- Connection validation during `init` with immediate feedback and clear error messages
- Project-local `mailreactor.yaml` config file with encrypted passwords
- Master password encryption (PBKDF2 + Fernet) with `!encrypted` YAML tag
- `mailreactor start` reads and decrypts config from current directory
- Master password via `MAILREACTOR_PASSWORD` env var or interactive prompt
- Provider-specific error guidance (Gmail App Passwords, Outlook 2FA hints)
- Library mode support (programmatic config without file)

**Out of Scope (Future Phases):**
- OAuth2 authentication (Phase 2 - Epic TBD)
- Multi-account orchestration in single instance (Phase 2)
- Account management REST API (removed - config file is source of truth)
- Runtime account CRUD operations (Phase 2 orchestrator if needed)
- Persistent state beyond config file (Phase 2 - Epic 6: IMAP-as-database)
- Connection pooling and keep-alive (Phase 2 optimization)
- Web UI for account configuration (Phase 2+)

**Out of Scope (Removed from Original Epic 2):**
- ❌ Account management REST API (`POST /accounts`, `GET /accounts`, `DELETE /accounts`)
- ❌ CLI account commands (`mailreactor account add/list/remove`)
- ❌ Global config directory (`~/.config/mailreactor/`)
- ❌ Hot-reload polling mechanism
- ❌ `StorageBackend` abstraction with namespaced keys (simplified to single-account)
- ❌ Runtime StateManager with multi-account support

## System Architecture Alignment

### Configuration Model

Mail Reactor uses **project-local configuration** following established developer tool patterns:

**Pattern Alignment:**
- `git init` → `.git/` directory
- `npm init` → `package.json`
- `docker-compose.yaml` → `docker-compose up`
- **`mailreactor init` → `mailreactor.yaml` → `mailreactor start`**

**Configuration Lifecycle:**

```
mailreactor init (wizard)
    ↓
Auto-detect provider settings
    ↓
Validate IMAP/SMTP connections
    ↓
Encrypt passwords with master password
    ↓
Write mailreactor.yaml to current directory
    ↓
mailreactor start (reads config)
    ↓
Prompt for master password (or read from MAILREACTOR_PASSWORD)
    ↓
Decrypt credentials
    ↓
Start server with account configured
```

### Dual-Mode Architecture

Mail Reactor supports two usage modes with project-local config as the foundation:

**API Mode (Primary):**
- Run `mailreactor init` to create `mailreactor.yaml`
- Run `mailreactor start` to start API server
- Server operates on single account from config
- Multi-account: Run multiple instances on different ports

**Library Mode (Advanced):**
- Import `mailreactor.core` directly in Python applications
- Option 1: Load config from file: `MailReactor.from_config("mailreactor.yaml")`
- Option 2: Programmatic config: `MailReactor(email="...", imap_config=..., smtp_config=...)`
- No file required - config can be built in code

### Package Structure

```
mailreactor/src/mailreactor/
├── core/                          # Pure Python, no FastAPI deps
│   ├── provider_detector.py       # Auto-detection logic
│   ├── connection_validator.py    # IMAP/SMTP validation
│   ├── config.py                  # YAML file operations (load, save)
│   ├── encryption.py              # Password encryption/decryption (PBKDF2 + Fernet)
│   └── providers.yaml             # Gmail, Outlook, Yahoo, iCloud configs
│
├── models/
│   └── account.py                 # Domain models (ProviderConfig, IMAPConfig, SMTPConfig, AccountConfig)
│
├── cli/
│   ├── init.py                    # mailreactor init wizard
│   └── server.py                  # mailreactor start (reads config)
│
└── main.py                        # FastAPI app (uses config from server.py)
```

**Core Components:**

| Module | Responsibility | Mode |
|--------|---------------|------|
| `core/provider_detector.py` | Auto-detect IMAP/SMTP settings from email domain | Both |
| `core/connection_validator.py` | Validate IMAP/SMTP credentials by connecting | Both |
| `core/config.py` | Load/save `mailreactor.yaml`, handle `!encrypted` tag | Both |
| `core/encryption.py` | Encrypt/decrypt passwords with master password | Both |
| `core/providers.yaml` | Hardcoded configs for Gmail, Outlook, Yahoo, iCloud | Both |
| `cli/init.py` | Interactive wizard for account setup | API |
| `cli/server.py` | Start server with config from file | API |
| `models/account.py` | Pydantic models for config schema | Both |

**Integration Points:**
- **IMAPClient:** Connection validation via sync client wrapped with asyncio executor (both modes)
- **aiosmtplib:** SMTP connection validation (native async, both modes)
- **httpx:** Async HTTP client for Mozilla Autoconfig queries (both modes)
- **PyYAML:** YAML parsing with custom `!encrypted` tag constructor (both modes)
- **cryptography:** Fernet encryption, PBKDF2 key derivation (both modes)
- **Typer:** CLI framework for `init` and `start` commands (API mode only)
- **getpass:** Hidden password input (API mode only)
- **Pydantic:** Data validation and models (both modes)

**Architectural Constraints:**
- **Framework-agnostic core:** Zero FastAPI imports in `core/` modules (library mode requirement)
- **Single account per instance:** Simplifies architecture, no runtime account management
- **Config file as source of truth:** No REST API for account CRUD, file is authoritative
- **Encrypted at rest:** Passwords in `mailreactor.yaml` always encrypted with Fernet
- **Master password required:** Decryption requires master password (env var or prompt)
- **Stateless beyond config:** No runtime state storage, server operates on config
- **Project-local config:** Each directory has own `mailreactor.yaml`, isolated instances

---

## Detailed Design

### Services and Modules

| Module | Responsibility | Key Methods | Dependencies | Mode |
|--------|---------------|-------------|--------------|------|
| `core/provider_detector.py` | Auto-detect IMAP/SMTP settings | `detect(email)`, `_detect_local(domain)`, `_detect_mozilla(domain)`, `_detect_isp(domain)` | httpx, PyYAML, xml.etree.ElementTree | Both |
| `core/connection_validator.py` | IMAP/SMTP connection validation | `validate(account_config)`, `_validate_imap(imap_config)`, `_validate_smtp(smtp_config)` | imapclient, aiosmtplib, asyncio | Both |
| `core/config.py` | YAML file operations | `load_config(path)`, `save_config(path, config)`, `decrypt_passwords(config, master_password)` | PyYAML, Pydantic | Both |
| `core/encryption.py` | Password encryption/decryption | `generate_salt()`, `derive_key(password, salt)`, `encrypt(plaintext, master_password)`, `decrypt(encrypted, master_password)` | cryptography (Fernet, PBKDF2) | Both |
| `cli/init.py` | Interactive account setup wizard | `wizard()`, `prompt_credentials()`, `prompt_manual_config()` | Typer, getpass, rich (optional), ProviderDetector, ConnectionValidator | API |
| `cli/server.py` | Start server with config | `start(config_path)`, `load_and_decrypt_config()` | Typer, getpass, Config | API |
| `models/account.py` | Domain data models | ProviderConfig, IMAPConfig, SMTPConfig, AccountConfig | Pydantic, EmailStr | Both |

### Data Models and Contracts

**ProviderConfig (Domain Model - `models/account.py`):**
```python
from pydantic import BaseModel

class ProviderConfig(BaseModel):
    """Auto-detected IMAP/SMTP configuration for a provider (server settings only)."""
    provider_name: str  # "Gmail", "Outlook", "Yahoo", etc.
    imap_host: str
    imap_port: int = 993
    imap_ssl: bool = True
    smtp_host: str
    smtp_port: int = 587
    smtp_starttls: bool = True
```

**IMAPConfig (Domain Model - `models/account.py`):**
```python
from pydantic import BaseModel, Field

class IMAPConfig(BaseModel):
    """IMAP server configuration and credentials."""
    host: str
    port: int = 993
    ssl: bool = True
    username: str  # Usually email, but can differ (shared mailboxes)
    password: str = Field(..., exclude=True)  # Never serialized (in-memory only)
```

**SMTPConfig (Domain Model - `models/account.py`):**
```python
from pydantic import BaseModel, Field

class SMTPConfig(BaseModel):
    """SMTP server configuration and credentials."""
    host: str
    port: int = 587
    starttls: bool = True
    username: str  # Usually email, but can differ (relay services)
    password: str = Field(..., exclude=True)  # Never serialized (in-memory only)
```

**AccountConfig (Domain Model - `models/account.py`):**
```python
from pydantic import BaseModel, EmailStr

class AccountConfig(BaseModel):
    """Complete account configuration (in-memory after decryption)."""
    email: EmailStr
    imap: IMAPConfig
    smtp: SMTPConfig
    
    @classmethod
    def from_yaml(cls, yaml_data: dict, master_password: str):
        """Load from mailreactor.yaml, decrypt passwords."""
        # Decrypt IMAP password
        imap_encrypted = yaml_data["imap"]["password"]  # !encrypted value
        imap_password = decrypt(imap_encrypted, master_password)
        
        # Decrypt SMTP password
        smtp_encrypted = yaml_data["smtp"]["password"]  # !encrypted value
        smtp_password = decrypt(smtp_encrypted, master_password)
        
        return cls(
            email=yaml_data["email"],
            imap=IMAPConfig(**{**yaml_data["imap"], "password": imap_password}),
            smtp=SMTPConfig(**{**yaml_data["smtp"], "password": smtp_password})
        )
```

### YAML Configuration File

**mailreactor.yaml (after `mailreactor init`):**

```yaml
email: personal@gmail.com

imap:
  host: imap.gmail.com
  port: 993
  ssl: true
  username: personal@gmail.com
  password: !encrypted gAAAAABhqK8s...  # Salt + Fernet token

smtp:
  host: smtp.gmail.com
  port: 587
  starttls: true
  username: personal@gmail.com
  password: !encrypted gAAAAABhSMTPpass...  # Salt + Fernet token
```

**Custom YAML Tag (`!encrypted`):**

```python
import yaml
from typing import Any

class EncryptedValue:
    """Wrapper for encrypted values in YAML."""
    def __init__(self, value: str):
        # value = <32-byte-base64-salt><fernet-token>
        self.salt = value[:44]  # Base64-encoded 32 bytes = 44 chars
        self.ciphertext = value[44:]

def encrypted_constructor(loader: yaml.Loader, node: yaml.Node) -> EncryptedValue:
    """Parse !encrypted tag."""
    value = loader.construct_scalar(node)
    return EncryptedValue(value)

# Register custom tag
yaml.add_constructor('!encrypted', encrypted_constructor)
```

**Loading Config:**

```python
import yaml
from pathlib import Path

def load_config(path: Path = Path("mailreactor.yaml")) -> dict:
    """Load mailreactor.yaml with custom tag support."""
    if not path.exists():
        raise FileNotFoundError(f"Configuration not found: {path}")
    
    with path.open("r") as f:
        config = yaml.safe_load(f)
    
    return config
```

**Saving Config (during `init`):**

```python
def save_config(path: Path, config: AccountConfig, master_password: str) -> None:
    """Save AccountConfig to YAML with encrypted passwords."""
    # Encrypt IMAP password
    imap_encrypted = encrypt(config.imap.password, master_password)
    
    # Encrypt SMTP password
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
    
    # Set file permissions to 0600 (user read/write only)
    path.chmod(0o600)
```

### Encryption Implementation

**Algorithm:** Fernet (symmetric encryption from `cryptography` library)

**Key Derivation:** PBKDF2-HMAC-SHA256, 100,000+ iterations (OWASP standard)

**Encryption Flow:**

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
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
        iterations=100_000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    return key

def encrypt(plaintext: str, master_password: str) -> str:
    """Encrypt plaintext password with master password.
    
    Returns: <base64-salt><fernet-token> (single string for YAML)
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
    """Decrypt encrypted value with master password.
    
    Args:
        encrypted: <base64-salt><fernet-token> string
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
- Master password never persisted to disk (env var or prompt only)
- Passwords encrypted at rest (`mailreactor.yaml`)
- Passwords decrypted in memory (process lifetime only)
- Salt prevents rainbow table attacks
- PBKDF2 iterations slow down brute-force attacks
- File permissions 0600 prevent casual reading

### APIs and Interfaces

**No REST API for Account Management (Removed from Original Spec)**

Epic 2 no longer includes account management REST endpoints. Configuration is managed via:
1. `mailreactor init` wizard (creates/updates `mailreactor.yaml`)
2. Manual editing of `mailreactor.yaml` (advanced users)
3. Programmatic config in library mode (Python API)

**CLI Interface:**

**1. `mailreactor init` - Account Setup Wizard**

**Scenario 1: Gmail (Auto-detected)**

```bash
$ mailreactor init

Email: personal@gmail.com
Password: ****

Auto-detected: Gmail ✓
Testing IMAP connection... ✓
Testing SMTP connection... ✓

Master password (for encryption): ****
Confirm master password: ****

✓ Configuration saved to mailreactor.yaml

To start the server:
  mailreactor start
  
The master password will be required at startup.
You can provide it via prompt or set MAILREACTOR_PASSWORD environment variable.
```

**Scenario 2: Unknown Domain (Manual Configuration)**

```bash
$ mailreactor init

Email: me@customdomain.com
Password: ****

Unable to auto-detect mail server settings.

IMAP server: imap.customdomain.com
IMAP port [993]: 
IMAP SSL [Y/n]: 
IMAP username [me@customdomain.com]: 

Testing IMAP connection... ✓

SMTP server: smtp.customdomain.com
SMTP port [587]: 
SMTP STARTTLS [Y/n]: 
SMTP username [me@customdomain.com]: 
Use same password for SMTP? [Y/n] y

Testing SMTP connection... ✓

Master password (for encryption): ****
Confirm master password: ****

✓ Configuration saved to mailreactor.yaml

To start the server:
  mailreactor start
  
The master password will be required at startup.
You can provide it via prompt or set MAILREACTOR_PASSWORD environment variable.
```

**Scenario 3: Relay Service (Different SMTP Credentials)**

```bash
$ mailreactor init

Email: me@mydomain.com
Password: ****

Auto-detected IMAP: imap.gmail.com ✓
Testing IMAP connection... ✓

SMTP server [smtp.gmail.com]: smtp.sendgrid.net
SMTP port [587]: 
SMTP STARTTLS [Y/n]: 
SMTP username [me@mydomain.com]: apikey
SMTP password [use IMAP password]: ****

Testing SMTP connection... ✓

Master password (for encryption): ****
Confirm master password: ****

✓ Configuration saved to mailreactor.yaml

To start the server:
  mailreactor start
  
The master password will be required at startup.
You can provide it via prompt or set MAILREACTOR_PASSWORD environment variable.
```

**2. `mailreactor start` - Start Server with Config**

**Interactive (no env var):**

```bash
$ mailreactor start

Master password: ****

[INFO] Decrypting credentials...
[INFO] Server ready: http://localhost:8000
[INFO] Account: personal@gmail.com
[INFO] Docs: http://localhost:8000/docs
```

**Automated (with env var):**

```bash
$ MAILREACTOR_PASSWORD=secret mailreactor start

[INFO] Decrypting credentials...
[INFO] Server ready: http://localhost:8000
[INFO] Account: personal@gmail.com
[INFO] Docs: http://localhost:8000/docs
```

**Error: Wrong Master Password**

```bash
$ mailreactor start

Master password: ****

[ERROR] Failed to decrypt credentials. Incorrect master password.
```

**Error: Missing Config**

```bash
$ mailreactor start

[ERROR] No configuration found in current directory.
[ERROR] Run 'mailreactor init' to create mailreactor.yaml
```

**Library Mode Python API:**

```python
import asyncio
from mailreactor.core.config import load_config, decrypt_passwords
from mailreactor.models.account import AccountConfig

async def main():
    # Option 1: Load from file
    config_dict = load_config("mailreactor.yaml")
    master_password = "user-master-password"
    account_config = AccountConfig.from_yaml(config_dict, master_password)
    
    print(f"Email: {account_config.email}")
    print(f"IMAP: {account_config.imap.host}:{account_config.imap.port}")
    print(f"SMTP: {account_config.smtp.host}:{account_config.smtp.port}")
    
    # Option 2: Programmatic config (no file)
    from mailreactor.models.account import IMAPConfig, SMTPConfig
    
    account_config = AccountConfig(
        email="user@example.com",
        imap=IMAPConfig(
            host="imap.example.com",
            port=993,
            ssl=True,
            username="user@example.com",
            password="imap-password"
        ),
        smtp=SMTPConfig(
            host="smtp.example.com",
            port=587,
            starttls=True,
            username="user@example.com",
            password="smtp-password"
        )
    )

asyncio.run(main())
```

### Workflows and Sequencing

**`mailreactor init` Wizard Flow:**

```
1. Prompt for email address
2. Prompt for password (hidden input via getpass)
3. Auto-detection cascade:
   a) Check core/providers.yaml for known domains
      - Gmail, Outlook, Yahoo, iCloud → Use hardcoded config
   b) If not found, query Mozilla Autoconfig
      - https://autoconfig.thunderbird.net/v1.1/{domain}
      - Parse XML for IMAP/SMTP settings
   c) If Mozilla fails, query ISP autoconfig
      - http://autoconfig.{domain}/mail/config-v1.1.xml
   d) If all fail, prompt for manual configuration
4. If auto-detection succeeded:
   - Use detected settings (IMAP host/port, SMTP host/port)
   - Assume username = email for both IMAP and SMTP
   - Assume same password for IMAP and SMTP
5. If auto-detection failed OR user wants to override:
   - Prompt for IMAP server, port, SSL
   - Prompt for IMAP username (default: email)
   - Prompt for SMTP server, port, STARTTLS
   - Prompt for SMTP username (default: email)
   - Prompt for separate SMTP password (default: use IMAP password)
6. Validate IMAP connection (async)
   - Connect to IMAP server with SSL
   - Attempt login with credentials
   - Disconnect
   - On failure: Show error with provider-specific hints
7. Validate SMTP connection (async, parallel with IMAP)
   - Connect to SMTP server with STARTTLS
   - Attempt authentication with credentials
   - Disconnect
   - On failure: Show error with provider-specific hints
8. If validation fails for either:
   - Display error message
   - Ask if user wants to retry or edit settings
   - Loop back to manual configuration
9. If validation succeeds for both:
   - Prompt for master password (hidden input)
   - Prompt to confirm master password
   - If mismatch: Re-prompt
10. Encrypt IMAP password with master password
11. Encrypt SMTP password with master password
12. Build mailreactor.yaml structure
13. Write to file (atomic write if possible)
14. Set file permissions to 0600
15. Display success message with next steps
```

**`mailreactor start` Startup Flow:**

```
1. Check for mailreactor.yaml in current directory
2. If not found:
   - Display error: "Run 'mailreactor init' to create mailreactor.yaml"
   - Exit with code 1
3. Load mailreactor.yaml with custom !encrypted tag handler
4. Check for MAILREACTOR_PASSWORD environment variable
5. If env var not set:
   - Prompt for master password (hidden input via getpass)
6. Attempt to decrypt IMAP password with master password
7. If decryption fails (InvalidToken exception):
   - Display error: "Incorrect master password"
   - Exit with code 1
8. Attempt to decrypt SMTP password with master password
9. Build AccountConfig object (in-memory, passwords decrypted)
10. Pass AccountConfig to FastAPI app initialization
11. Start Uvicorn server
12. Log: "Server ready: http://localhost:8000"
13. Log: "Account: {email}"
```

**Auto-Detection Cascade (Detailed):**

```
detect_provider(email: str) → Optional[ProviderConfig]
    ↓
1. Extract domain from email (e.g., "gmail.com")
    ↓
2. Load core/providers.yaml
    ↓
3. Check if domain in providers.yaml
   - If match found:
     - Return ProviderConfig with hardcoded settings
     - No network calls (instant, offline-capable)
    ↓
4. If not in local providers.yaml:
   - Query Mozilla Autoconfig via httpx
   - URL: https://autoconfig.thunderbird.net/v1.1/{domain}
   - Timeout: 5 seconds
    ↓
5. If Mozilla returns 200 OK:
   - Parse XML response
   - Extract IMAP server (type="imap"), port, socketType
   - Extract SMTP server (type="smtp"), port, socketType
   - Build ProviderConfig
   - Return ProviderConfig
    ↓
6. If Mozilla returns 404 or times out:
   - Query ISP autoconfig
   - URL: http://autoconfig.{domain}/mail/config-v1.1.xml
   - Timeout: 5 seconds
    ↓
7. If ISP returns 200 OK:
   - Parse XML (same format as Mozilla)
   - Build ProviderConfig
   - Return ProviderConfig
    ↓
8. If all methods fail:
   - Return None (manual configuration required)
```

**Connection Validation (Parallel):**

```
validate(account_config: AccountConfig) → tuple[bool, bool, Optional[str]]
    ↓
Run IMAP and SMTP validation in parallel using asyncio.gather()
    ↓
IMAP Validation (async):
    1. Create IMAPClient instance
    2. Run in asyncio executor (IMAPClient is sync)
    3. Connect to host:port with SSL
    4. Attempt login(username, password)
    5. If success: Logout and disconnect
    6. Return (True, None) for success
    7. On exception:
       - socket.timeout → (False, "Connection timeout")
       - ConnectionRefusedError → (False, "Connection refused")
       - AuthenticationError → (False, "Authentication failed")
       - SSLError → (False, "SSL certificate error")
    ↓
SMTP Validation (async):
    1. Create SMTP instance from aiosmtplib
    2. Connect to host:port
    3. If STARTTLS: Upgrade connection
    4. Attempt login(username, password)
    5. If success: Disconnect
    6. Return (True, None) for success
    7. On exception:
       - asyncio.TimeoutError → (False, "Connection timeout")
       - ConnectionRefusedError → (False, "Connection refused")
       - SMTPAuthenticationError → (False, "Authentication failed")
       - SSLError → (False, "SSL certificate error")
    ↓
Combine results:
    - If both True: Return success
    - If either False: Return failure with error messages
```

**Provider-Specific Error Hints:**

```python
def get_provider_hint(email: str, error_type: str) -> str:
    """Return provider-specific troubleshooting hints."""
    domain = email.split("@")[1].lower()
    
    if domain == "gmail.com" and error_type == "authentication_failed":
        return (
            "For Gmail with 2FA enabled, you must use an App Password.\n"
            "Create one at: https://myaccount.google.com/apppasswords"
        )
    
    if domain in ["outlook.com", "hotmail.com"] and error_type == "authentication_failed":
        return (
            "For Outlook/Hotmail with 2FA, use an App Password.\n"
            "Enable at: https://account.microsoft.com/security"
        )
    
    if error_type == "connection_timeout":
        return (
            "Connection timed out. Check:\n"
            "  - Internet connectivity\n"
            "  - Firewall allows outbound connections\n"
            "  - Server hostname is correct"
        )
    
    if error_type == "ssl_error":
        return (
            "SSL certificate verification failed. Check:\n"
            "  - Server hostname matches certificate\n"
            "  - System certificates are up to date\n"
            "  - Consider using IP address if hostname fails"
        )
    
    return "Check credentials and server settings."
```

---

## Non-Functional Requirements

### Performance

**NFR-P1: Startup Time (3 seconds)**
- `mailreactor start` from cold boot to operational health endpoint within 3 seconds
- Decryption overhead: <100ms (PBKDF2 with 100k iterations)
- Config file parsing: <50ms
- Total acceptable: IMAP/SMTP connections in Epic 3+ may add latency, but init/decrypt must be fast

**NFR-P2: Auto-Detection Latency**
- Local providers.yaml lookup: <1ms (in-memory dict)
- Mozilla Autoconfig query: <5s (enforced timeout)
- ISP autoconfig query: <5s (enforced timeout)
- Total cascade worst-case: <10s (acceptable for one-time `init`)

**NFR-P3: Wizard Responsiveness**
- User input prompts: Instant (<10ms)
- Connection validation feedback: Real-time (show "Testing..." immediately)
- Validation timeout: 10s per service (IMAP, SMTP run in parallel)

**NFR-P4: Memory Footprint**
- Decrypted passwords in memory only (no disk writes)
- AccountConfig object: ~1KB
- Epic 2 modules: <5MB RAM total
- Target: Maintain <100MB baseline from Epic 1

### Security

**NFR-S1: Credential Storage**
- ✅ Passwords encrypted at rest (Fernet with PBKDF2-derived key)
- ✅ Master password never persisted to disk
- ✅ File permissions 0600 (user read/write only)
- ✅ Pydantic `exclude=True` on password fields (never serialized)
- ✅ Never logged (structlog filters sensitive fields)
- ⚠️ Vulnerability: Decrypted passwords in memory (acceptable for self-hosted MVP)

**NFR-S2: Encryption Strength**
- Algorithm: Fernet (AES-128-CBC with HMAC-SHA256)
- Key derivation: PBKDF2-HMAC-SHA256, 100,000 iterations (OWASP 2023 minimum)
- Salt: 32 bytes random per password (prevents rainbow tables)
- Master password entropy: User responsibility (recommend passphrase or password manager)

**NFR-S3: Network Security**
- ✅ IMAP connections use SSL by default (port 993)
- ✅ SMTP connections use STARTTLS by default (port 587)
- ✅ TLS certificate verification enabled
- ⚠️ Mozilla/ISP autoconfig queries over HTTP (no sensitive data transmitted)

**NFR-S4: Dependency Security**
- cryptography: Actively maintained, industry-standard library
- PyYAML: Maintained, use safe_load to prevent code execution
- httpx: Maintained, used only for autoconfig queries
- All dependencies vetted in ADR decisions

**NFR-S5: Data Privacy**
- ✅ No telemetry in MVP
- ✅ Passwords never leave localhost (IMAP/SMTP connections go directly to email servers)
- ✅ Mozilla Autoconfig query only sends domain (no email address, no credentials)

### Reliability/Availability

**NFR-R1: Connection Resilience**
- Auto-detection failures gracefully fall back to manual configuration
- Connection validation failures provide clear error messages with remediation hints
- Network timeouts (5s for auto-detection, 10s for validation) prevent indefinite hangs
- Provider-specific error guidance (Gmail App Passwords, Outlook 2FA hints)

**NFR-R2: Error Handling**
- ✅ Clear error messages for all failure modes
  - Wrong master password: "Incorrect master password"
  - Missing config: "Run 'mailreactor init' to create mailreactor.yaml"
  - IMAP connection failed: Provider-specific hint
  - SMTP connection failed: Provider-specific hint
- ✅ Wizard allows retry without losing progress
- ✅ Validation errors don't create partial config (atomic write on success only)

**NFR-R3: Configuration Integrity**
- Atomic file writes (write to temp, rename) to prevent corruption
- YAML validation on load (Pydantic schema enforcement)
- File permissions check on load (warn if not 0600)
- Decryption failure exits immediately (fail-fast, no partial state)

**NFR-R4: Graceful Degradation**
- Auto-detection failure → Manual configuration (wizard adapts)
- Mozilla Autoconfig timeout → ISP autoconfig fallback
- ISP autoconfig timeout → Manual configuration
- Connection validation failure → Clear error, retry option

### Observability

**NFR-O1: Logging**
- ✅ Structured logging with structlog (JSON-capable)
- Log events:
  - INFO: Wizard started (email domain)
  - INFO: Auto-detection result (provider detected or failed)
  - INFO: Connection validation started (IMAP, SMTP)
  - INFO: Account configured successfully
  - INFO: Server started with account (email)
  - ERROR: Connection validation failed (error type, host, port, hint)
  - ERROR: Decryption failed (wrong master password)
  - ERROR: Config file not found
- Context binding: email, domain, provider
- Sensitive data filtering: passwords never logged, master password never logged

**NFR-O2: User Feedback**
- Wizard progress indicators: "Testing IMAP connection... ✓"
- Real-time validation feedback (not silent 10s waits)
- Success confirmation with clear next steps
- Error messages with actionable hints

**NFR-O3: Developer Experience**
- Clear error messages (no cryptic stack traces)
- Wizard prompts explain what's needed
- Defaults suggested in brackets: `IMAP port [993]:`
- Master password reminder: "You'll need this to start the server"

---

## Dependencies and Integrations

### External Dependencies

| Dependency | Version | License | Purpose | Mode |
|-----------|---------|---------|---------|------|
| imapclient | >=3.0.1 | BSD-3 | IMAP connection validation | Both |
| aiosmtplib | >=5.0.0 | MIT | SMTP connection validation | Both |
| httpx | >=0.27.0 | BSD-3 | Mozilla/ISP autoconfig HTTP queries | Both |
| PyYAML | >=6.0.1 | MIT | Parse/write mailreactor.yaml | Both |
| cryptography | >=41.0.0 | BSD/Apache-2.0 | Fernet encryption, PBKDF2 | Both |
| Pydantic | >=2.0 | MIT | Data validation, config models | Both |
| Typer | >=0.20.0 | MIT | CLI framework (init, start commands) | API |
| rich | >=13.0.0 (optional) | MIT | Pretty CLI output (progress bars, colors) | API |

**Python Version:** >=3.11 (for `tomllib` stdlib, modern async)

**Dependency Constraints:**
```toml
# pyproject.toml
[project.dependencies]
imapclient = "^3.0.1"
aiosmtplib = "^5.0.0"
httpx = "^0.27.0"
pyyaml = "^6.0.1"
cryptography = "^41.0.0"
pydantic = "^2.0"
typer = "^0.20.0"

[project.optional-dependencies]
cli = ["rich>=13.0.0"]  # Pretty output for wizard
```

### Integration Points

**No External Services (Beyond Autoconfig Queries):**
- Mozilla Autoconfig: Read-only HTTP queries, no authentication
- ISP Autoconfig: Read-only HTTP queries, no authentication
- IMAP/SMTP validation: Direct connections to user's email servers

**No Database:**
- Config file (`mailreactor.yaml`) is the only persistent state
- No migrations, no schema evolution beyond YAML structure

**No REST API for Accounts (Removed):**
- Original Epic 2 had account management endpoints
- Now removed: Config file is source of truth
- Multi-account: Run multiple instances with different configs

**Future Integration Hooks:**
- Epic 3 (Email Sending): Reads AccountConfig from startup
- Epic 4 (Email Retrieval): Reads AccountConfig from startup
- Epic 6 (IMAP-as-database): Uses IMAP credentials from AccountConfig

---

## Acceptance Criteria (Authoritative)

**AC-2.1: `mailreactor init` Wizard - Gmail Auto-Detection**
1. Given user runs `mailreactor init` in empty directory
2. When user enters `user@gmail.com` and password
3. Then Gmail provider is auto-detected from local providers.yaml
4. And IMAP/SMTP settings are populated automatically
5. And connection validation succeeds
6. And user is prompted for master password (with confirmation)
7. And `mailreactor.yaml` is created with encrypted passwords
8. And file permissions are set to 0600
9. And success message displays next steps

**AC-2.2: `mailreactor init` Wizard - Unknown Domain Manual Config**
1. Given user runs `mailreactor init`
2. When user enters `user@unknowndomain.com` and password
3. Then auto-detection fails (not in providers.yaml, Mozilla/ISP return 404)
4. And wizard prompts for IMAP server, port, SSL
5. And wizard prompts for SMTP server, port, STARTTLS
6. And wizard validates IMAP connection with provided settings
7. And wizard validates SMTP connection with provided settings
8. And user is prompted for master password (with confirmation)
9. And `mailreactor.yaml` is created with encrypted passwords

**AC-2.3: `mailreactor init` Wizard - Relay Service (Separate SMTP Credentials)**
1. Given user runs `mailreactor init`
2. When user enters `user@example.com` with IMAP credentials
3. And user overrides SMTP server to `smtp.sendgrid.net`
4. And user provides different SMTP username/password
5. Then wizard validates IMAP connection
6. And wizard validates SMTP connection with different credentials
7. And `mailreactor.yaml` contains separate encrypted passwords for IMAP and SMTP

**AC-2.4: `mailreactor start` - Successful Decryption**
1. Given valid `mailreactor.yaml` exists in current directory
2. When user runs `mailreactor start`
3. And provides correct master password (via prompt or `MAILREACTOR_PASSWORD`)
4. Then credentials are decrypted successfully
5. And server starts with AccountConfig loaded
6. And logs display: "Server ready: http://localhost:8000"
7. And logs display: "Account: user@example.com"

**AC-2.5: `mailreactor start` - Wrong Master Password**
1. Given valid `mailreactor.yaml` exists
2. When user runs `mailreactor start`
3. And provides incorrect master password
4. Then decryption fails with InvalidToken exception
5. And error message displays: "Incorrect master password"
6. And server does not start (exit code 1)

**AC-2.6: `mailreactor start` - Missing Config File**
1. Given no `mailreactor.yaml` in current directory
2. When user runs `mailreactor start`
3. Then error message displays: "No configuration found"
4. And error message suggests: "Run 'mailreactor init' to create mailreactor.yaml"
5. And server does not start (exit code 1)

**AC-2.7: Encryption Security - Passwords Encrypted at Rest**
1. Given user runs `mailreactor init` and creates config
2. When inspecting `mailreactor.yaml` in text editor
3. Then IMAP password field shows: `password: !encrypted gAAAAA...`
4. And SMTP password field shows: `password: !encrypted gAAAAA...`
5. And plaintext passwords are not visible
6. And file permissions are 0600 (user read/write only)

**AC-2.8: Encryption Security - Master Password Not Persisted**
1. Given user completes `mailreactor init` wizard
2. When inspecting filesystem and environment
3. Then master password is not written to any file
4. And master password is not set in environment variables automatically
5. And master password must be provided each time `mailreactor start` runs

**AC-2.9: Auto-Detection - Local Providers Fast Path**
1. Given user enters email with known domain (gmail.com, outlook.com, yahoo.com, icloud.com)
2. When auto-detection runs
3. Then provider config is returned from local providers.yaml
4. And no network calls are made (offline-capable)
5. And detection completes in <1ms

**AC-2.10: Auto-Detection - Mozilla Fallback**
1. Given user enters email with unknown domain
2. And domain is not in local providers.yaml
3. When auto-detection runs
4. Then Mozilla Autoconfig is queried via HTTPS
5. And if response is 200 OK, XML is parsed
6. And ProviderConfig is built from XML data
7. And ProviderConfig is returned (no manual config needed)

**AC-2.11: Connection Validation - IMAP Failure with Provider Hint**
1. Given Gmail user enters incorrect password
2. When IMAP validation runs
3. Then authentication fails
4. And error message includes: "Authentication failed"
5. And hint includes: "For Gmail with 2FA, use App Password"
6. And hint includes link to Google App Passwords page

**AC-2.12: Connection Validation - Parallel IMAP and SMTP**
1. Given user completes wizard with valid credentials
2. When connection validation runs
3. Then IMAP and SMTP validation run concurrently (asyncio.gather)
4. And total validation time is max(imap_time, smtp_time), not sum
5. And both validations complete within 10 seconds

**AC-2.13: Library Mode - Load Config from File**
1. Given valid `mailreactor.yaml` exists
2. When library mode code calls `AccountConfig.from_yaml(config_dict, master_password)`
3. Then AccountConfig object is created with decrypted passwords
4. And IMAP/SMTP credentials are accessible in memory
5. And no FastAPI dependencies are imported

**AC-2.14: Library Mode - Programmatic Config (No File)**
1. Given library mode code
2. When user creates `AccountConfig(email=..., imap=IMAPConfig(...), smtp=SMTPConfig(...))`
3. Then AccountConfig is created without reading any file
4. And credentials are used directly from code
5. And no encryption/decryption is needed

**AC-2.15: YAML Custom Tag - `!encrypted` Parsing**
1. Given `mailreactor.yaml` with `password: !encrypted gAAAAA...`
2. When YAML is loaded with custom tag constructor
3. Then `!encrypted` value is parsed into EncryptedValue object
4. And salt is extracted from first 44 characters
5. And ciphertext is extracted from remaining characters
6. And decryption succeeds with correct master password

---

## Traceability Mapping

| Acceptance Criteria | Spec Section | Component | Test Strategy |
|---------------------|--------------|-----------|---------------|
| AC-2.1: Gmail auto-detection | Workflows, Data Models | `cli/init.py`, `core/provider_detector.py` | E2E test: Mock user input, verify YAML created |
| AC-2.2: Unknown domain manual | Workflows | `cli/init.py`, `core/provider_detector.py` | E2E test: Mock httpx 404, verify manual prompts |
| AC-2.3: Relay service | Workflows, Data Models | `cli/init.py`, `models/account.py` | E2E test: Different SMTP credentials, verify YAML |
| AC-2.4: Start success | Workflows | `cli/server.py`, `core/config.py`, `core/encryption.py` | E2E test: Load config, decrypt, verify server starts |
| AC-2.5: Wrong master password | NFR-R2, Workflows | `core/encryption.py`, `cli/server.py` | Unit test: Trigger InvalidToken, verify error message |
| AC-2.6: Missing config | NFR-R2, Workflows | `cli/server.py` | Unit test: No file exists, verify error |
| AC-2.7: Passwords encrypted | NFR-S1, Data Models | `core/encryption.py`, `core/config.py` | Unit test: Inspect YAML text, verify !encrypted tag |
| AC-2.8: Master password not persisted | NFR-S1 | `cli/init.py`, `cli/server.py` | Security test: Check filesystem, env vars |
| AC-2.9: Local providers fast | NFR-P2, Workflows | `core/provider_detector.py` | Unit test: Time detection, assert <1ms |
| AC-2.10: Mozilla fallback | Workflows, Dependencies | `core/provider_detector.py`, httpx | Integration test: Mock httpx, parse XML |
| AC-2.11: IMAP failure hint | NFR-R1, Workflows | `core/connection_validator.py` | Unit test: Mock auth failure, verify hint |
| AC-2.12: Parallel validation | NFR-P3, Workflows | `core/connection_validator.py` | Performance test: Verify asyncio.gather usage |
| AC-2.13: Library load config | APIs, Data Models | `models/account.py`, `core/config.py` | Unit test: Load YAML, decrypt, verify AccountConfig |
| AC-2.14: Library programmatic | APIs, Data Models | `models/account.py` | Unit test: Create AccountConfig in code |
| AC-2.15: !encrypted tag | Data Models, Workflows | `core/config.py` | Unit test: YAML parsing, verify EncryptedValue |

**PRD FR Coverage:**
- FR-001: Auto-detection (AC-2.1, AC-2.9, AC-2.10)
- FR-002: CLI account configuration (AC-2.1, AC-2.2, AC-2.3) - via `init` wizard, not `--account` flag
- FR-005: IMAP connection validation (AC-2.1, AC-2.11, AC-2.12)
- FR-006: SMTP connection validation (AC-2.1, AC-2.11, AC-2.12)
- FR-007: Manual override (AC-2.2, AC-2.3)
- FR-008: Validation with clear errors (AC-2.11, AC-2.5, AC-2.6)

**Removed FRs (No Longer in Epic 2):**
- ❌ FR-003: Add account via REST API (removed)
- ❌ FR-004: In-memory credential storage (now encrypted file storage)
- ❌ FR-009: Retrieve list of accounts via API (removed)
- ❌ FR-010: Retrieve specific account details via API (removed)

---

## Risks, Assumptions, Open Questions

### Risks

**R1: Master Password Forgotten**
- Risk: User forgets master password, cannot decrypt `mailreactor.yaml`
- Probability: Medium (common with password-protected files)
- Impact: High (must re-run `mailreactor init`, reconfigure account)
- Mitigation: Document clearly, suggest password manager, no recovery mechanism (by design)

**R2: Mozilla Autoconfig Availability**
- Risk: Mozilla's autoconfig service could be unavailable or slow
- Probability: Low (stable service, used by Thunderbird)
- Impact: Medium (fallback to ISP autoconfig or manual config)
- Mitigation: 5-second timeout, ISP fallback, manual config option

**R3: Provider Configuration Accuracy**
- Risk: Hardcoded providers.yaml settings could become outdated
- Probability: Medium (providers occasionally change servers)
- Impact: Low (connection validation would fail, user can manual override)
- Mitigation: Document provider configs, accept community PRs for updates, Mozilla fallback

**R4: File Permissions Weakness**
- Risk: User accidentally makes `mailreactor.yaml` world-readable (chmod 644)
- Probability: Medium (if checked into version control or shared carelessly)
- Impact: Medium (encrypted, but salt is visible, makes brute-force easier)
- Mitigation: Warn on startup if permissions are too open, documentation emphasizes 0600

**R5: Multi-Account UX Confusion**
- Risk: Users expect multi-account in single instance, confused by "run multiple instances"
- Probability: Medium (coming from tools with multi-account UI)
- Impact: Low (documentation clarifies, orchestrator can come in Phase 2)
- Mitigation: Clear docs, FAQ, future orchestrator epic

### Assumptions

**A1: Single Account Primary Use Case (MVP)**
- Assumption: Most MVP users will manage 1-2 accounts maximum
- Justification: Self-hosted, personal use, multi-account via multiple instances acceptable
- Impact: Architecture simplified, no complex runtime state management

**A2: Master Password Acceptable UX**
- Assumption: Users willing to enter master password at startup (or set env var)
- Justification: Similar to SSH key passphrases, database passwords
- Impact: More secure than plaintext, acceptable friction for self-hosted

**A3: Project-Local Config Acceptable**
- Assumption: Users understand "one directory = one account" model
- Justification: Matches Docker Compose, git, npm mental models
- Impact: Config location is intuitive, version control friendly (with care)

**A4: Network Connectivity for Auto-Detection**
- Assumption: Server has outbound internet for Mozilla/ISP autoconfig during `init`
- Justification: One-time operation, most deployments have internet
- Impact: Auto-detection fails gracefully offline (manual config works)

**A5: App Passwords for 2FA Providers**
- Assumption: Users with Gmail/Outlook 2FA will use App Passwords (not OAuth2)
- Justification: OAuth2 is Phase 2 (Epic TBD)
- Impact: Error messages guide users to App Password setup

### Open Questions

**Q1: Should `mailreactor init` Support Re-Configuration?**
- Question: If `mailreactor.yaml` exists, should `init` allow editing or force manual edit?
- Status: Recommend `init` detect existing file and offer to overwrite or cancel
- Action: Implement "Config exists. Overwrite? [y/N]" prompt

**Q2: Should Master Password Have Minimum Strength Requirements?**
- Question: Enforce minimum length (e.g., 12 characters) or complexity?
- Status: Recommend warning for short passwords (<8 chars), but allow override
- Action: Display warning, user decides

**Q3: Should YAML Support Comments for User Notes?**
- Question: Allow users to add comments like `# Work email` in `mailreactor.yaml`?
- Status: Yes - YAML naturally supports comments, don't strip on write
- Action: Preserve comments when possible (PyYAML may not preserve, acceptable)

**Q4: Should Library Mode Support `mailreactor.yaml` Discovery?**
- Question: Should `AccountConfig.from_yaml()` search parent directories for config?
- Status: No - explicit path required, avoids magic behavior
- Action: User must specify path or default to `mailreactor.yaml` in cwd

**Q5: Should `mailreactor start` Support `--config` Flag?**
- Question: Allow `mailreactor start --config /path/to/custom.yaml`?
- Status: Yes - useful for testing, multiple configs
- Action: Add `--config` optional flag, default to `mailreactor.yaml` in cwd

**Q6: Mozilla Autoconfig Rate Limiting**
- Question: Does Mozilla enforce rate limits on autoconfig queries?
- Status: Unknown (not documented publicly), no evidence of limits
- Action: Monitor in production, no caching needed for one-time `init`

**Q7: Should Wizard Support Non-Interactive Mode?**
- Question: CLI flags to bypass prompts (e.g., `mailreactor init --email ... --password ...`)?
- Status: Deferred to user feedback - interactive is MVP, flags can come later
- Action: Document as potential enhancement

---

## Test Strategy Summary

### Unit Tests (Story-Level)

**core/provider_detector.py:**
- Test local providers.yaml lookup (gmail, outlook, yahoo, icloud)
- Test domain extraction from email addresses
- Test Mozilla Autoconfig XML parsing (mock httpx response)
- Test ISP autoconfig XML parsing (mock httpx response)
- Test fallback cascade (local → Mozilla → ISP → None)
- Test error handling (network timeout, invalid XML, 404)

**core/connection_validator.py:**
- Test IMAP validation success (mock IMAPClient)
- Test IMAP validation failures (timeout, auth failed, connection refused)
- Test SMTP validation success (mock aiosmtplib)
- Test SMTP validation failures (timeout, auth failed, connection refused)
- Test parallel validation with asyncio.gather
- Test provider-specific hint generation

**core/encryption.py:**
- Test salt generation (32 bytes random)
- Test key derivation (PBKDF2 with correct iterations)
- Test encrypt/decrypt round-trip (same password succeeds)
- Test decrypt with wrong password (InvalidToken exception)
- Test encrypted value format (salt + ciphertext)

**core/config.py:**
- Test load_config from valid YAML file
- Test load_config with missing file (FileNotFoundError)
- Test save_config creates valid YAML
- Test save_config sets file permissions to 0600
- Test custom !encrypted tag parsing
- Test AccountConfig.from_yaml decryption

**models/account.py:**
- Test ProviderConfig validation (Pydantic)
- Test IMAPConfig validation
- Test SMTPConfig validation
- Test AccountConfig validation
- Test password field exclusion (exclude=True)

### Integration Tests (Epic-Level)

**End-to-End: `mailreactor init` Wizard - Gmail**
1. Mock user input: `user@gmail.com`, password, master password
2. Mock IMAPClient success, aiosmtplib success
3. Run wizard
4. Verify `mailreactor.yaml` created
5. Verify file contains !encrypted passwords
6. Verify file permissions are 0600
7. Verify can load and decrypt with master password

**End-to-End: `mailreactor init` Wizard - Unknown Domain**
1. Mock user input: `user@unknowndomain.com`, password, manual config, master password
2. Mock httpx 404 for Mozilla and ISP autoconfig
3. Mock manual prompts for IMAP/SMTP settings
4. Mock IMAPClient success, aiosmtplib success
5. Run wizard
6. Verify `mailreactor.yaml` created with manual settings

**End-to-End: `mailreactor start` with Correct Master Password**
1. Create valid `mailreactor.yaml` (encrypted)
2. Mock master password input or set MAILREACTOR_PASSWORD
3. Run `mailreactor start`
4. Verify credentials decrypted
5. Verify server starts
6. Verify AccountConfig passed to FastAPI app

**End-to-End: `mailreactor start` with Wrong Master Password**
1. Create valid `mailreactor.yaml` (encrypted)
2. Mock incorrect master password input
3. Run `mailreactor start`
4. Verify InvalidToken exception caught
5. Verify error message displayed
6. Verify server does not start (exit code 1)

**Auto-Detection Integration:**
1. Mock httpx to return valid Mozilla Autoconfig XML
2. Call provider_detector.detect() with unknown domain
3. Verify ProviderConfig built from XML
4. Verify no local providers.yaml match needed

**Connection Validation Integration:**
1. Use real IMAPClient and aiosmtplib (or test doubles)
2. Mock IMAP server (success and failure scenarios)
3. Mock SMTP server (success and failure scenarios)
4. Verify validation results and error messages

### Security Tests

**Encryption Security:**
- Verify master password never written to disk
- Verify decrypted passwords never written to disk
- Verify `mailreactor.yaml` file permissions are 0600
- Verify wrong master password cannot decrypt
- Verify salt is unique per password (no reuse)

**YAML Parsing Security:**
- Use yaml.safe_load (no code execution vulnerabilities)
- Test with malicious YAML (!!python/object attacks)
- Verify custom !encrypted tag only constructs EncryptedValue

**Password Exclusion:**
- Verify AccountConfig.dict(exclude={'imap': {'password'}}) excludes password
- Verify logs never contain passwords
- Verify error messages never expose passwords

### Performance Tests

**Auto-Detection Latency:**
- Measure local providers.yaml lookup (<1ms target)
- Measure Mozilla Autoconfig query (<5s timeout enforced)
- Measure ISP autoconfig query (<5s timeout enforced)

**Encryption Performance:**
- Measure encrypt() time (<100ms target)
- Measure decrypt() time (<100ms target)
- Measure key derivation time (PBKDF2 100k iterations)

**Wizard Responsiveness:**
- Measure time from prompt to next prompt (<10ms target)
- Measure validation feedback latency (immediate "Testing..." display)

**Startup Time (NFR-P1):**
- Measure `mailreactor start` to health endpoint ready
- Ensure decryption overhead <100ms
- Maintain <3s total startup time from Epic 1

### Test Coverage Goals

- Unit test coverage: 85%+ for core modules
- Integration test coverage: All user-facing workflows (init, start, errors)
- Security test coverage: All encryption/decryption paths, permission checks
- Error path coverage: All failure scenarios (wrong password, missing config, connection failures)

### Test Organization

```
tests/
├── unit/
│   ├── test_provider_detector.py      # Auto-detection logic
│   ├── test_connection_validator.py   # IMAP/SMTP validation
│   ├── test_encryption.py             # Encrypt/decrypt
│   ├── test_config.py                 # YAML load/save
│   └── test_models.py                 # Pydantic validation
├── integration/
│   ├── test_init_wizard.py            # E2E init flows
│   ├── test_start_command.py          # E2E start flows
│   ├── test_autodetection.py          # Mozilla/ISP integration
│   └── test_validation.py             # IMAP/SMTP integration
├── security/
│   ├── test_encryption_security.py    # Crypto strength
│   ├── test_file_permissions.py       # 0600 enforcement
│   └── test_password_exclusion.py     # No leaks
└── performance/
    ├── test_autodetection_latency.py  # Detection speed
    ├── test_encryption_speed.py       # Crypto speed
    └── test_startup_time.py            # NFR-P1 validation
```

---

## Story Breakdown (Preliminary)

**Story 2.1: Provider Auto-Detection**
- Implement `core/provider_detector.py`
- Create `core/providers.yaml` with Gmail, Outlook, Yahoo, iCloud
- Implement local provider lookup (fast path)
- Implement Mozilla Autoconfig fallback (HTTP query, XML parsing)
- Implement ISP autoconfig fallback
- Unit tests for all detection paths

**Story 2.2: Connection Validation**
- Implement `core/connection_validator.py`
- IMAP validation (sync client, asyncio executor)
- SMTP validation (async client)
- Parallel validation (asyncio.gather)
- Provider-specific error hints
- Unit tests for validation logic

**Story 2.3: Encryption Implementation**
- Implement `core/encryption.py`
- Salt generation, key derivation (PBKDF2)
- Fernet encrypt/decrypt
- Error handling (InvalidToken)
- Security tests (no disk writes, unique salts)

**Story 2.4: YAML Config File Operations**
- Implement `core/config.py`
- Custom !encrypted YAML tag constructor
- load_config() with tag parsing
- save_config() with atomic write
- File permissions enforcement (0600)
- Unit tests for YAML operations

**Story 2.5: `mailreactor init` Wizard**
- Implement `cli/init.py`
- Interactive prompts (email, password, master password)
- Smart wizard logic (auto-detect → manual fallback)
- Integration with provider_detector and connection_validator
- Password confirmation
- Success message with next steps
- E2E tests for wizard flows

**Story 2.6: `mailreactor start` Command**
- Implement `cli/server.py` enhancements
- Load config from file (default or --config flag)
- Master password prompt or MAILREACTOR_PASSWORD env var
- Decrypt credentials
- Pass AccountConfig to FastAPI app
- Error handling (missing config, wrong password)
- E2E tests for start flows

---

## Document Status

**Status:** Draft - Course Corrected
**Replaces:** tech-spec-epic-2.md (2025-12-04)
**Next Review:** Post-approval by Scrum Master (HC)
**Change Log:**
- 2025-12-05: Complete rewrite based on course correction analysis
  - Removed: Account management REST API, StateManager, hot-reload, global config
  - Added: `mailreactor init` wizard, project-local YAML config, master password encryption
  - Simplified: Single account per instance, config file as source of truth
  - Aligned: Developer mental model (git init, npm init patterns)
  - Maintained: Auto-detection, connection validation, library mode support

**Approval Required From:**
- Scrum Master (HC) - Epic scope and story breakdown
- Architect (Winston) - Technical soundness and architecture.md alignment
- Dev Team - Feasibility and effort estimates

---

**End of Epic 2 Technical Specification (Revised)**
