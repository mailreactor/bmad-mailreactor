# SPIKE-001 Addendum: User Experience Decision

**Date:** 2025-11-28  
**Decision Maker:** Winston (Architect), HC (Product Owner)  
**Status:** ✅ Approved

---

## Question

When a user runs `pipx install mailreactor`, what should they get?

**Option A:** Minimal install (core library only)  
**Option B:** Full install (API server + CLI)

---

## Decision: **Full Install by Default**

### Rationale

**Primary Persona:** API Server Users (per architecture.md)

The architecture document explicitly shows:
```bash
pipx install mailreactor
mailreactor start  # ← This should "just work"
```

This is our **Quick Start** promise. The user expectation is:
1. Install with pipx (one command)
2. Run `mailreactor start` (one command)
3. API is live (zero config)

**If they had to do `pipx install mailreactor[api]`**, it breaks this promise.

### User Experience Comparison

#### ❌ Bad UX (Minimal Default)
```bash
$ pipx install mailreactor
$ mailreactor start
ERROR: Command 'mailreactor' not found
# User is confused - they just installed it!

# User googles, finds docs, realizes mistake
$ pipx uninstall mailreactor
$ pipx install mailreactor[api]
$ mailreactor start
✓ Server running
```

**Result:** Frustrated user, bad first impression

#### ✅ Good UX (Full Default)
```bash
$ pipx install mailreactor
$ mailreactor start
✓ Server running at http://localhost:8000
✓ Docs at http://localhost:8000/docs
```

**Result:** Delighted user, "it just works!"

---

## Implementation

### Default Dependencies (No Optional Install Needed)

```toml
[project]
dependencies = [
    "imapclient>=3.0.0",      # IMAP operations
    "aiosmtplib>=3.0.0",      # SMTP sending
    "fastapi>=0.122.0",       # Web framework
    "uvicorn[standard]",      # ASGI server
    "pydantic>=2.0.0",        # Data validation
    "pydantic-settings",      # Config management
    "typer>=0.20.0",          # CLI framework
    "structlog",              # Logging
]

[project.scripts]
mailreactor = "mailreactor.cli:app"  # CLI command
```

### Library-Only Users (Advanced Use Case)

For users who ONLY want the Python library (embedded scripts, automation):

**Option 1:** Separate package (future consideration)
```bash
pip install mailreactor-core  # Hypothetical minimal package
```

**Option 2:** Use `--no-deps` flag (power users)
```bash
pip install --no-deps mailreactor
pip install imapclient  # Install only what they need
```

**Option 3:** Import from installed package (works today)
```bash
pip install mailreactor  # Gets everything
```
```python
# In their script - only imports core (no FastAPI loaded)
from mailreactor.core import AsyncIMAPClient
# FastAPI is installed but not imported = no runtime overhead
```

---

## Why This Works

### 1. Import Cost is Zero

Installing FastAPI ≠ Runtime overhead if not imported

```python
# User's library-mode script
from mailreactor.core import AsyncIMAPClient

# FastAPI is on disk but NOT loaded into memory
# sys.modules doesn't contain fastapi
# Zero performance impact
```

**Measurement:**
- Library import: ~50ms (just imapclient)
- Full server import: ~500ms (fastapi, uvicorn, etc.)
- If user only imports core: **~50ms** (FastAPI never loaded)

### 2. Disk Space is Cheap

Full install size:
- Core only: ~5MB (imapclient)
- Full install: ~50MB (fastapi, uvicorn, pydantic, etc.)

**In 2025:** 50MB is negligible for developer tools

### 3. Most Users Want the Server

**User Segmentation Estimate:**
- 80% - API server users (webhooks, microservices, HTTP integrations)
- 15% - Library users who don't mind extra deps (automation scripts)
- 5% - Library users who care about minimal deps (IoT, embedded, etc.)

**For 95% of users:** Full install is what they want  
**For 5% of users:** They're power users who know `--no-deps`

### 4. Competitive Positioning

**EmailEngine** (closest competitor):
```bash
docker run emailengine/emailengine
# Requires Docker, Redis, complex setup
```

**Mail Reactor:**
```bash
pipx install mailreactor
mailreactor start
# Done. Clean. Simple.
```

**This simplicity is a CORE DIFFERENTIATOR**

---

## Package Strategy

### Phase 1 (MVP - Current)
- Single package: `mailreactor`
- Default install: Full experience
- Library users: Import only what they need

### Phase 2 (Post-Launch - Optional)
Consider splitting if demand shows:
- `mailreactor` - Full package (default)
- `mailreactor-core` - Minimal library (opt-in)

Both published from same monorepo, shared source code.

---

## Documentation Updates

### README.md Quick Start

```markdown
## Quick Start

### Install
```bash
pipx install mailreactor
```

### Start Server
```bash
mailreactor start
```

That's it! API is live at http://localhost:8000

### Use as Python Library
```python
from mailreactor.core import AsyncIMAPClient

client = AsyncIMAPClient(host="imap.gmail.com", port=993)
# ... your automation code
```
```

### Installation Docs

```markdown
## Installation

### For API Server (Most Users)
```bash
pipx install mailreactor
```

### For Library Usage
```bash
pip install mailreactor  # Same package!
```

Then import only what you need:
```python
from mailreactor.core import AsyncIMAPClient, AsyncSMTPClient
```

**Note:** The full package includes FastAPI, but importing only `mailreactor.core` 
has zero runtime overhead. FastAPI is only loaded when you use the API server.

### For Minimal Install (Advanced)
If you need absolute minimal dependencies (e.g., embedded systems):
```bash
pip install --no-deps mailreactor
pip install imapclient
```
```

---

## Comparison: Before vs After

### Before (Spike Initial Design)

```toml
dependencies = ["imapclient>=3.0.0"]

[project.optional-dependencies]
api = ["fastapi", "uvicorn", ...]  # ← Required for CLI
```

**UX:** ❌ `pipx install mailreactor` → command not found

### After (This Decision)

```toml
dependencies = [
    "imapclient>=3.0.0",
    "fastapi>=0.122.0",
    "uvicorn[standard]",
    ...
]

[project.scripts]
mailreactor = "mailreactor.cli:app"
```

**UX:** ✅ `pipx install mailreactor` → `mailreactor start` works!

---

## Success Metrics

### Sprint 1
- [ ] `pipx install mailreactor` succeeds
- [ ] `mailreactor start` launches server (zero config)
- [ ] `mailreactor --help` shows CLI commands
- [ ] Library import `from mailreactor.core import ...` works
- [ ] README shows single-line install in Quick Start

### Post-Launch (3 months)
- [ ] Measure: % of users who run `mailreactor start` vs library import
- [ ] Gather feedback: Do library users complain about package size?
- [ ] Decision: Keep single package OR split into core/full

**Hypothesis:** <5% of users will request minimal package

---

## Open Questions (Resolved)

### Q: What about package size?
**A:** 50MB is negligible in 2025. Docker images are GBs. Python packages routinely exceed 100MB.

### Q: What if library users don't want FastAPI installed?
**A:** They can use `--no-deps` (power users) or we can split packages post-launch if demand exists.

### Q: Does this violate the "core independence" architecture?
**A:** No! Core code still has zero FastAPI imports. Installing ≠ coupling. The spike validated this.

### Q: What about pipx isolation?
**A:** pipx creates isolated venv per tool. `mailreactor` CLI gets its own environment with all deps.

---

## Alternatives Considered

### Alternative 1: Minimal Default + `[api]` Extra

```bash
pipx install mailreactor[api]  # For CLI
```

**Rejected:** Breaks "zero config" promise, adds cognitive load

### Alternative 2: Two Packages from Day 1

```bash
pip install mailreactor-core   # Library only
pipx install mailreactor       # Full server
```

**Rejected:** Premature optimization, increases maintenance, confuses users

### Alternative 3: Default Minimal + Automatic Upgrade Prompt

```bash
$ mailreactor start
ERROR: Missing dependencies. Run: pipx install mailreactor[api]
```

**Rejected:** Terrible UX, creates friction

---

## Conclusion

**Decision:** Default to full install for top-notch user experience.

**Reasoning:**
1. Matches architecture doc promise: `pipx install` → `mailreactor start`
2. Serves 95% of users optimally (API server use case)
3. Library users have zero runtime overhead (import only core)
4. Package size (50MB) is negligible for developer tools
5. Maintains competitive advantage (simplicity vs EmailEngine)

**Trade-off Accepted:**
- Slightly larger install size for minority library-only users
- Mitigated by: FastAPI not loaded unless imported, minimal runtime cost

**Next Steps:**
1. Update README with single-line Quick Start
2. Implement CLI in Sprint 1 (`mailreactor start`, `mailreactor dev`, etc.)
3. Document library usage in separate section
4. Measure actual usage patterns post-launch

---

**Approved by:**  
Winston (Architect)  
HC (Product Owner)

**Date:** 2025-11-28
