# SPIKE-003: CLI Account Management with Encrypted Storage

**Date:** 2025-12-05  
**Status:** Approved  
**Participants:** Winston (Architect), Amelia (Dev), Murat (TEA), Bob (SM), HC (Product Owner)

---

## Problem Statement

Currently, `mailreactor start` accepts `--account` flag for runtime configuration. This approach doesn't support:
- Multiple accounts per instance
- Persistent account storage
- Secure credential management
- Runtime account management without restart

We need a CLI-based account management system that supports future multi-tenant SaaS architecture while starting with single-tenant self-hosted deployment.

---

## Scope

**In Scope (SPIKE):**
- Single-tenant, single config file architecture
- Multiple accounts per config file
- CLI commands for account management (add/edit/remove/list)
- API endpoints for account management
- Encrypted password storage (Fernet + PBKDF2)
- Hot reload via polling
- HTTPS enforcement for production API usage

**Out of Scope:**
- Multi-tenant isolation (future: database-backed configs)
- Autodiscovery in API (CLI only)
- File watching mechanisms (watchdog, inotify)
- Signal-based reload commands
- Multi-instance per machine support

---

## Architecture Decision

### Config Storage

**Location:** `~/.config/mailreactor/config.toml` (default)

**Structure:**
```toml
[mailreactor]
encryption_key_salt = "randomly-generated-on-first-run"

[[accounts]]
email = "hc@vst.io"  # Email IS the account ID
encrypted_password = "fernet-encrypted-blob"
imap_host = "imap.gmail.com"
imap_port = 993
imap_use_tls = true
smtp_host = "smtp.gmail.com"
smtp_port = 587
smtp_use_tls = true

[[accounts]]
email = "admin@example.com"
encrypted_password = "fernet-encrypted-blob"
# ... additional account config
```

### Encryption Strategy

**Master Password:**
- Source: `MAILREACTOR_PASSWORD` environment variable or runtime prompt
- Never persisted to disk
- Required at startup to decrypt account passwords

**Encryption:**
- Algorithm: Fernet (symmetric encryption via `cryptography` library)
- Key Derivation: `PBKDF2(master_password + salt)` → Fernet key
- Salt: Stored in config.toml (not secret, prevents rainbow tables)
- Account passwords: Encrypted with derived Fernet key

### Memory + Persistence Pattern

**Runtime Storage:**
- Accounts loaded into memory at startup after decryption
- All runtime operations use in-memory account objects
- Config.toml is source of truth on disk

**Write Flow:**
```
CLI/API writes → config.toml (encrypted) → Reload mechanism → memory updated
```

### Hot Reload Mechanism

**Approach: 5-Second Polling**

**Why polling over file watching/signals:**
- ✅ Simple, predictable, cross-platform identical behavior
- ✅ Zero race conditions (file fully written before detection)
- ✅ No external dependencies (stdlib only)
- ✅ One `stat()` call per 5 seconds = negligible overhead
- ✅ Natural debouncing window

**Implementation:**
```python
# Background thread in mailreactor start
def config_poller():
    last_mtime = os.path.getmtime(config_path)
    while running:
        time.sleep(5)
        current_mtime = os.path.getmtime(config_path)
        if current_mtime > last_mtime:
            account_manager.reload_config()  # Atomic reload
            last_mtime = current_mtime
```

**Reload Behavior:**
- **API writes:** Write to config.toml → immediately call `reload_config()` → instant
- **CLI writes:** Write to config.toml → exit → polling detects within 5s → reload
- **Manual edits:** Edit config.toml → polling detects within 5s → reload

**Error Handling:**
- Malformed config during reload → **crash with error** (fail-fast)
- Invalid encryption → crash
- Missing required fields → crash
- Operator fixes config and restarts service

### CLI Commands

**Account Management:**
```bash
# List all accounts
mailreactor accounts list [--config PATH]

# Add account (runs autodiscover, prompts for password)
mailreactor accounts add EMAIL [--config PATH]

# Edit account (interactive prompts for fields to change)
mailreactor accounts edit EMAIL [--config PATH]

# Remove account
mailreactor accounts remove EMAIL [--config PATH]
```

**Autodiscovery:**
- CLI runs Mozilla Thunderbird autoconfig discovery
- Prompts user for password interactively
- Writes complete config to TOML (encrypted password)

**Atomic Writes:**
- Write to temporary file
- Atomic rename to config.toml
- Prevents partial reads during write

### API Endpoints

**Design Principle:** API is explicit, machine-to-machine interface. No autodiscovery magic.

**Endpoints:**
```
POST   /accounts       - Create account (all fields required)
GET    /accounts       - List all accounts (passwords omitted)
GET    /accounts/{email} - Get specific account
PUT    /accounts/{email} - Update account
DELETE /accounts/{email} - Remove account
```

**Create Account Request:**
```json
POST /accounts
{
  "email": "hc@vst.io",
  "password": "plaintext-password-over-https",
  "imap_host": "imap.gmail.com",
  "imap_port": 993,
  "imap_use_tls": true,
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_use_tls": true
}
```

**Requirements:**
- All fields required (no defaults, no autodiscovery)
- Password sent as plaintext (HTTPS required in prod)
- Server encrypts password before storing in config.toml
- Immediate reload triggered after write

**Security:**
- Production mode (`mailreactor start`): HTTPS required for account mutations
- Dev mode (`mailreactor dev`): HTTP allowed on localhost (127.0.0.1) only
- HTTPS detection via `X-Forwarded-Proto` header (reverse proxy pattern)

### Changes to Existing Commands

**Remove `--account` flag:**
```bash
# OLD (deprecated)
mailreactor start --account hc@vst.io

# NEW
mailreactor start [--config PATH]
# Loads all accounts from config.toml
```

**Startup Behavior:**
- If no accounts in config → start idle, wait for API account additions
- If accounts present → decrypt passwords, load into memory, start processing

---

## Implementation Checklist

### Core Components

1. **AccountConfig Module** (`account_config.py`)
   - TOML read/write operations
   - Encryption/decryption service (Fernet + PBKDF2)
   - Salt generation and storage
   - Atomic file writes

2. **AccountManager** (`account_manager.py`)
   - In-memory account storage (dict: email → Account)
   - `reload_config()` - atomic reload from disk
   - Account CRUD operations
   - Connection lifecycle management (close removed accounts, start new ones)

3. **CLI Commands** (`cli/accounts.py`)
   - `accounts list/add/edit/remove` subcommands
   - Autodiscovery integration
   - Interactive password prompts
   - Config file path resolution

4. **Config Poller** (`config_watcher.py`)
   - Background thread
   - 5-second polling loop
   - mtime-based change detection
   - Triggers `account_manager.reload_config()`

5. **API Endpoints** (`api/accounts.py`)
   - FastAPI routes for account CRUD
   - Request validation (all fields required)
   - HTTPS enforcement middleware
   - Immediate reload trigger after writes

6. **HTTPS Detection Middleware** (`middleware/https.py`)
   - Check `X-Forwarded-Proto` header
   - Reject account mutations over HTTP in prod mode
   - Allow localhost HTTP in dev mode

### Modified Components

- `cli/start.py` - Remove `--account` flag, add config loading
- `cli/dev.py` - Remove `--account` flag, add config loading
- `main.py` - Initialize AccountManager, start config poller thread

---

## Acceptance Criteria

**AC1: CLI Account Management**
- ✅ `mailreactor accounts add` runs autodiscovery and encrypts password in config.toml
- ✅ `mailreactor accounts list` displays all accounts (no passwords)
- ✅ `mailreactor accounts edit` updates account and re-encrypts password
- ✅ `mailreactor accounts remove` deletes account from config
- ✅ Email used as account ID (no UUIDs)

**AC2: API Account Management**
- ✅ `POST /accounts` with all required fields creates encrypted account
- ✅ API requires all fields (no autodiscovery)
- ✅ `GET /accounts` returns list without passwords
- ✅ `PUT /accounts/{email}` updates account
- ✅ `DELETE /accounts/{email}` removes account

**AC3: Hot Reload**
- ✅ API changes trigger immediate in-memory reload
- ✅ CLI changes detected within 6 seconds (5s polling + 1s buffer)
- ✅ Manual config edits detected within 6 seconds
- ✅ Running instance reflects account changes without restart

**AC4: Security**
- ✅ Passwords encrypted with Fernet in config.toml
- ✅ Master password from `MAILREACTOR_PASSWORD` or runtime prompt
- ✅ Passwords never appear in logs, API responses, or error messages
- ✅ API rejects account mutations over HTTP in prod mode
- ✅ API allows mutations over HTTP localhost in dev mode

**AC5: Error Handling**
- ✅ Malformed config during reload → process exits with error code
- ✅ Invalid encryption → process exits with error
- ✅ Missing required fields → process exits with error
- ✅ Clear error messages guide operator to fix config

**AC6: Startup Behavior**
- ✅ `mailreactor start` loads accounts from config at startup
- ✅ Starts successfully with zero accounts (idle mode)
- ✅ `--account` flag removed from start/dev commands

---

## Test Plan

### Unit Tests (15 tests)
- Encryption/decryption round-trip with various passwords
- Key derivation from master password + salt
- TOML read/write/update operations
- Account validation (email format, required fields, port ranges)
- Atomic file write operations

### Integration Tests (10 tests)
- CLI commands → config file changes → verify encrypted content
- Polling thread detects mtime changes within timeout
- `reload_config()` atomic swap (old → new accounts)
- Account connection lifecycle (close removed, start new)
- Config file locking during concurrent writes

### E2E Tests (8 tests)
- Full flow: `accounts add` → `start` → verify account active
- API add account → polling reload → account active in <6s
- CLI add account → polling reload → account active in <6s
- Malformed config → crash with exit code != 0
- Multi-account config → all accounts loaded correctly

### Security Tests (5 tests)
- Password never in plaintext (logs, responses, errors, debug output)
- Encryption key derivation meets PBKDF2 iteration minimum (100k+)
- HTTPS detection with/without `X-Forwarded-Proto` header
- HTTP rejection in prod mode for account mutations
- Master password prompt doesn't echo to terminal

**Total: 38 tests**

---

## Effort Estimate

**Implementation:** 3-5 days focused work

**Breakdown:**
- Day 1: AccountConfig + encryption service
- Day 2: AccountManager + reload logic
- Day 3: CLI commands + autodiscovery integration
- Day 4: API endpoints + HTTPS middleware
- Day 5: Config poller + integration testing

---

## Future Enhancements (Post-SPIKE)

**Multi-Tenant SaaS:**
- Replace TOML with database-backed config storage
- Tenant isolation at data layer
- Dynamic tenant provisioning API
- Per-tenant encryption keys

**Advanced Reload:**
- Explicit reload command (`mailreactor reload`)
- Signal-based reload (SIGHUP on Linux/Mac)
- Multi-instance support with state files

**Security Hardening:**
- Hardware security module (HSM) integration
- Credential rotation policies
- Audit logging for account changes

---

## Questions Resolved

**Q: Use UUID or email as account ID?**  
**A:** Email. Simple, user-friendly, no added complexity.

**Q: Should API include autodiscovery?**  
**A:** No. API is explicit machine-to-machine interface. CLI handles autodiscovery for humans.

**Q: Hot reload via file watching or polling?**  
**A:** Polling (5s interval). Simpler, more reliable, cross-platform identical.

**Q: What happens if config becomes malformed during reload?**  
**A:** Process crashes (fail-fast). Operator fixes config and restarts.

**Q: Should service start without accounts?**  
**A:** Yes. Idle mode allows API-driven account provisioning.

**Q: How to handle multiple instances with reload?**  
**A:** Out of scope. Single instance per machine for SPIKE. Multi-instance deferred to future enhancement.

**Q: API immediate reload vs wait for polling?**  
**A:** API triggers immediate reload. Polling is backup for CLI/manual edits.

---

## Sign-Off

**Architect (Winston):** ✅ Architecture approved. Clean separation of concerns, future-proof abstraction layer.

**Developer (Amelia):** ✅ Implementation plan clear. Effort estimate reasonable.

**Test Architect (Murat):** ✅ Test coverage adequate. Risk areas identified and mitigated.

**Scrum Master (Bob):** ✅ Scope locked. Ready for story creation.

**Product Owner (HC):** ✅ Approved for implementation.

---

**Next Steps:**
1. Create user story from this SPIKE
2. Break into subtasks if needed
3. Add to sprint backlog
4. Begin implementation
