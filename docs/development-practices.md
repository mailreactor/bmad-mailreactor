# Mail Reactor - Development Practices

**Date:** 2025-11-26  
**Author:** HC  
**Status:** Team Standard - Required for All Development  

---

## Overview

This document defines the **mandatory development practices** for Mail Reactor. All developers must follow these practices to ensure code quality, consistency, and maintainability.

---

## 1. Test-Driven Development (TDD) - REQUIRED

### Mandate

**All production code MUST be developed using TDD.** No exceptions for MVP.

### TDD Workflow (Red-Green-Refactor)

Every feature implementation follows this strict cycle:

#### Step 1: RED - Write Failing Test First

```python
# tests/unit/core/test_provider_detector.py
import pytest
from mailreactor.core.provider_detector import ProviderDetector

def test_gmail_detection_from_email():
    """Given Gmail email address, auto-detect IMAP/SMTP settings"""
    # ARRANGE
    detector = ProviderDetector()
    email = "user@gmail.com"
    
    # ACT
    settings = detector.detect(email)
    
    # ASSERT
    assert settings.imap_host == "imap.gmail.com"
    assert settings.imap_port == 993
    assert settings.imap_ssl is True
    assert settings.smtp_host == "smtp.gmail.com"
    assert settings.smtp_port == 587
    assert settings.smtp_starttls is True
```

**At this point:**
- ❌ Test fails (ProviderDetector doesn't exist yet)
- ✅ This is correct! You wrote the test FIRST

#### Step 2: GREEN - Write Minimal Code to Pass

```python
# src/mailreactor/core/provider_detector.py
class ProviderSettings:
    def __init__(self, imap_host, imap_port, imap_ssl, smtp_host, smtp_port, smtp_starttls):
        self.imap_host = imap_host
        self.imap_port = imap_port
        self.imap_ssl = imap_ssl
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_starttls = smtp_starttls

class ProviderDetector:
    def detect(self, email: str) -> ProviderSettings:
        # Minimal implementation - just make test pass
        if "@gmail.com" in email:
            return ProviderSettings(
                imap_host="imap.gmail.com",
                imap_port=993,
                imap_ssl=True,
                smtp_host="smtp.gmail.com",
                smtp_port=587,
                smtp_starttls=True
            )
        raise ValueError("Unknown provider")
```

**Run test:**
```bash
pytest tests/unit/core/test_provider_detector.py::test_gmail_detection_from_email
```

**Result:** ✅ Test passes

#### Step 3: REFACTOR - Improve Code Quality

```python
# src/mailreactor/core/provider_detector.py (refactored)
from pydantic import BaseModel
from typing import Dict
import yaml

class ProviderSettings(BaseModel):
    imap_host: str
    imap_port: int
    imap_ssl: bool
    smtp_host: str
    smtp_port: int
    smtp_starttls: bool

class ProviderDetector:
    def __init__(self):
        # Load provider configs from YAML
        with open("src/mailreactor/utils/providers.yaml") as f:
            self._providers: Dict = yaml.safe_load(f)
    
    def detect(self, email: str) -> ProviderSettings:
        domain = email.split("@")[1]
        
        # Check for known provider
        if domain in self._providers:
            config = self._providers[domain]
            return ProviderSettings(
                imap_host=config["imap"]["host"],
                imap_port=config["imap"]["port"],
                imap_ssl=config["imap"]["ssl"],
                smtp_host=config["smtp"]["host"],
                smtp_port=config["smtp"]["port"],
                smtp_starttls=config["smtp"]["starttls"],
            )
        
        raise ValueError(f"Unknown provider: {domain}")
```

**Run tests again:**
```bash
pytest tests/unit/core/test_provider_detector.py
```

**Result:** ✅ All tests still pass (refactoring preserved behavior)

---

### TDD Rules

#### Rule 1: No Production Code Without a Test

**Prohibited:**
```python
# ❌ WRONG: Writing implementation first
def send_email(to, subject, body):
    # Implementation...
    pass

# Then writing test later
def test_send_email():  # Test written AFTER implementation
    pass
```

**Required:**
```python
# ✅ CORRECT: Test first
def test_send_email_success():
    """Test MUST be written before implementation"""
    client = EmailClient()
    result = client.send_email(
        to="test@example.com",
        subject="Test",
        body="Hello"
    )
    assert result.status == "sent"

# THEN implement (and test fails until implementation is correct)
```

#### Rule 2: Write the Simplest Test First

Start with the **happy path**, then add edge cases:

```python
# Test 1: Happy path (write this first)
def test_send_email_with_valid_inputs():
    pass

# Test 2: Add edge case (write this second)
def test_send_email_with_missing_subject():
    pass

# Test 3: Add error case (write this third)
def test_send_email_with_invalid_recipient():
    pass
```

#### Rule 3: Run Tests Frequently

After **every** change:
```bash
# Run specific test
pytest tests/unit/core/test_provider_detector.py -v

# Run all tests in module
pytest tests/unit/core/ -v

# Run all tests (before commit)
pytest tests/
```

#### Rule 4: Commit Only Green Tests

**Never commit failing tests.** Your commit history should show:
```
✅ feat: Add Gmail provider detection with tests
✅ feat: Add Outlook provider detection with tests
✅ refactor: Extract provider config to YAML
```

Not:
```
❌ WIP: Half-finished provider detector (tests failing)
```

---

### TDD Benefits for Mail Reactor

1. **Prevents IMAP/SMTP Integration Bugs:**
   - Write mock tests BEFORE touching real IMAP servers
   - Catch edge cases (connection failures, timeouts) early

2. **Documents Behavior:**
   - Tests serve as executable specifications
   - New developers read tests to understand how code works

3. **Refactoring Safety:**
   - Change internal implementation confidently
   - Tests verify behavior unchanged

4. **Faster Debugging:**
   - Test failure pinpoints exact broken behavior
   - No manual testing with real email accounts

---

### TDD for Different Test Levels

#### Unit Tests (TDD Applied)

**Every business logic function:**
- Provider detection
- IMAP query builder
- Message parser
- Error classifier

**Example:**
```python
# FIRST: Write test
def test_imap_query_builder_unseen():
    builder = IMAPQueryBuilder()
    query = builder.build(unseen=True)
    assert query == ['UNSEEN']

# THEN: Implement
class IMAPQueryBuilder:
    def build(self, unseen=False):
        criteria = []
        if unseen:
            criteria.append('UNSEEN')
        return criteria
```

#### Integration Tests (TDD Applied)

**Every API endpoint:**
- Account creation
- Message sending
- Message retrieval

**Example:**
```python
# FIRST: Write test
@pytest.mark.asyncio
async def test_create_account_endpoint(client):
    response = await client.post("/accounts", json={
        "email": "test@gmail.com",
        "password": "test123"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "test@gmail.com"

# THEN: Implement endpoint
@router.post("/accounts", status_code=201)
async def create_account(account: AccountCreate):
    # Implementation...
    pass
```

#### E2E Tests (TDD Optional)

E2E tests can be written **after** implementation for critical paths, since they test system integration rather than individual components.

---

### TDD Enforcement

#### Pre-Commit Checks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ensure-tests-exist
        name: Ensure tests exist for new code
        entry: python scripts/check_test_coverage.py
        language: system
        pass_filenames: false
```

#### Code Review Checklist

**Reviewers must verify:**
- [ ] Tests written BEFORE implementation (check git history)
- [ ] All tests pass (`pytest` in CI)
- [ ] Coverage remains ≥80% (automated check)
- [ ] Tests follow AAA pattern (Arrange, Act, Assert)

#### Sprint Retrospective

Track TDD adoption:
- **Metric:** % of commits with tests written first (use git log analysis)
- **Goal:** 100% TDD compliance by Sprint 2

---

## 2. Nix Flakes + Direnv - REQUIRED

### Mandate

**All developers MUST use Nix flakes with direnv** for reproducible development environments.

### Why Nix?

- **Reproducibility:** Every developer has identical Python version, dependencies, tools
- **No "Works on My Machine":** Nix ensures consistency across macOS, Linux, Windows (WSL)
- **Declarative:** Environment defined in code (`flake.nix`), versioned with project
- **Fast:** Nix caches builds, instant environment activation with direnv

---

### Setup Instructions

#### 1. Install Nix (One-Time Setup)

**macOS/Linux:**
```bash
# Install Nix with flakes enabled (Determinate Systems installer - recommended)
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install

# Or official installer:
# sh <(curl -L https://nixos.org/nix/install) --daemon
# Then enable flakes:
# mkdir -p ~/.config/nix
# echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf
```

**Windows:**
Use WSL2 (Ubuntu) and follow Linux instructions.

#### 2. Install Direnv (One-Time Setup)

```bash
# macOS
brew install direnv

# Linux
sudo apt install direnv  # Ubuntu/Debian
# or
nix profile install nixpkgs#direnv

# Add to shell (~/.bashrc or ~/.zshrc)
eval "$(direnv hook bash)"  # or zsh
```

#### 3. Install nix-direnv (CRITICAL for Performance)

**This step is REQUIRED - makes direnv 10-100x faster!**

```bash
# Install nix-direnv
nix-env -iA nixpkgs.nix-direnv

# Or with nix profile (newer):
nix profile install nixpkgs#nix-direnv

# Configure direnv to use nix-direnv
mkdir -p ~/.config/direnv
cat > ~/.config/direnv/direnvrc << 'EOF'
source $HOME/.nix-profile/share/nix-direnv/direnvrc
EOF

# Verify installation
nix-direnv-reload --help
# Should show help text if installed correctly
```

**Why nix-direnv is critical:**
- **Without nix-direnv:** `direnv allow` takes 30-60 seconds every time
- **With nix-direnv:** First time 30s, subsequent times ~1 second (cached!)
- Caches Nix environment between directory changes
- Prevents expensive Nix rebuilds on every `cd`

#### 3. Clone and Activate Environment

```bash
# Clone repository
git clone https://github.com/yourusername/mailreactor.git
cd mailreactor

# Allow direnv (first time only)
direnv allow

# Environment automatically activates!
# You'll see: "direnv: loading ~/mailreactor/.envrc"
```

**That's it!** Python 3.10+, all dependencies, dev tools are now available.

---

### Project Configuration

#### `flake.nix` (Created in Sprint 0)

**Architecture Decision:** Hybrid Nix + venv approach with **UV**

- **Nix provides:** Python interpreter, system tools (git, docker-compose), **uv** (fast package manager)
- **venv provides:** Python packages via **uv** (10-100x faster than pip)
- **Version source of truth:** `pyproject.toml` (Nix reads from there)

```nix
{
  description = "Mail Reactor - Headless Email Client";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        
        # Python interpreter only (packages via uv/venv)
        python = pkgs.python310;
        
        # Read project metadata from pyproject.toml (single source of truth)
        projectMeta = builtins.fromTOML (builtins.readFile ./pyproject.toml);
        projectVersion = projectMeta.project.version;
        projectName = projectMeta.project.name;
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            # Python interpreter (Nix ensures version consistency)
            python
            
            # UV - Fast Python package manager (replaces pip)
            pkgs.uv
            
            # System-level tools (not Python packages)
            pkgs.git
            pkgs.docker-compose
            pkgs.pre-commit
            pkgs.just      # Command runner
            pkgs.jq        # JSON processing
            
            # Native libraries for Python packages
            pkgs.openssl   # For cryptography packages
            pkgs.libffi    # For cffi-based packages
            pkgs.stdenv.cc.cc.lib  # For compiled extensions
          ];

          shellHook = ''
            echo "🚀 Mail Reactor Development Environment"
            echo "Project: ${projectName} v${projectVersion}"
            echo "Python: $(python --version)"
            echo "UV: $(uv --version)"
            echo ""
            
            # Auto-install pre-commit hooks
            if [ ! -f .git/hooks/pre-commit ]; then
              echo "📦 Installing pre-commit hooks..."
              pre-commit install
            fi
            
            # Create and activate virtualenv (Python packages via uv)
            if [ ! -d .venv ]; then
              echo "📦 Creating virtualenv with uv..."
              uv venv .venv
              source .venv/bin/activate
              
              echo "📦 Installing Python dependencies (10-100x faster than pip!)..."
              uv pip install -e ".[dev]"
              
              echo "✅ Environment ready!"
            else
              source .venv/bin/activate
            fi
            
            echo ""
            echo "Available commands:"
            echo "  mailreactor start    - Start API server"
            echo "  pytest tests/        - Run tests"
            echo "  ruff check .         - Lint code"
            echo "  mypy src/            - Type check"
            echo ""
            echo "Package management (use uv, not pip!):"
            echo "  uv pip install <pkg> - Install package"
            echo "  uv pip list          - List packages"
            echo ""
          '';
          
          # Ensure Python uses Nix environment
          PYTHONPATH = "";
          
          # SSL certificates for uv
          SSL_CERT_FILE = "${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt";
          
          # Library path for compiled extensions
          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc.lib
            pkgs.openssl
            pkgs.libffi
          ];
        };

        # Package definition (for production builds)
        packages.default = python.pkgs.buildPythonApplication {
          pname = projectName;
          version = projectVersion;
          src = ./.;
          format = "pyproject";
          
          nativeBuildInputs = [
            python.pkgs.setuptools
            python.pkgs.wheel
          ];
          
          propagatedBuildInputs = with python.pkgs; [
            # Core dependencies (read from pyproject.toml in real implementation)
            fastapi
            uvicorn
            pydantic
            typer
            structlog
          ];
        };
        
        # Development app (using venv)
        apps.default = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/mailreactor";
        };
      }
    );
}
```

#### `.envrc` (Created in Sprint 0)

**Note:** Uses `nix-direnv` for fast, cached Nix environment loading (10-100x faster).

```bash
# Use nix-direnv for caching (IMPORTANT: Makes direnv 10-100x faster!)
# First time: ~30s to build, subsequent times: ~1s from cache
if ! has nix_direnv_version || ! nix_direnv_version 2.3.0; then
  source_url "https://raw.githubusercontent.com/nix-community/nix-direnv/2.3.0/direnvrc" "sha256-Dmd+j63L84wuzgyjITIfSxSD57Tx7v51DMxVZOsiUD8="
fi

# Load Nix flake environment (cached by nix-direnv)
use flake

# Load environment variables from .env (if exists)
if [ -f .env ]; then
  dotenv .env
fi

# Set Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"

# Activate virtualenv (created by flake shellHook)
if [ -d .venv ]; then
  source .venv/bin/activate
fi
```

---

### Architecture Decisions Explained

#### Decision 1: Version in `pyproject.toml` Only

**Question:** Should version be hardcoded in `flake.nix` or use another source of truth?

**Answer:** ✅ **Version lives in `pyproject.toml` ONLY. Nix reads from there.**

**Why this approach:**

```toml
# pyproject.toml (SINGLE SOURCE OF TRUTH)
[project]
name = "mailreactor"
version = "0.1.0"  # ← Version defined here
```

```nix
# flake.nix (READS from pyproject.toml)
let
  projectMeta = builtins.fromTOML (builtins.readFile ./pyproject.toml);
  projectVersion = projectMeta.project.version;  # ← Dynamically read
in
  packages.default = python.pkgs.buildPythonApplication {
    version = projectVersion;  # ← Uses pyproject.toml version
  };
```

**Benefits:**
- ✅ **DRY:** Version defined in exactly one place
- ✅ **Python standard:** `pyproject.toml` is ecosystem convention
- ✅ **No sync issues:** Impossible for versions to drift
- ✅ **CI/CD friendly:** `pip install .` uses same version as Nix build

**When you bump version:**
```bash
# 1. Edit pyproject.toml
[project]
version = "0.2.0"  # ← Bump here

# 2. Nix automatically picks up new version
nix flake check  # Uses 0.2.0

# 3. pip also uses new version
pip install -e .  # Uses 0.2.0
```

**Alternative (NOT RECOMMENDED):**
```nix
# ❌ BAD: Hardcoded version in flake.nix
packages.default = pkgs.python310Packages.buildPythonApplication {
  version = "0.1.0";  # Hardcoded - must manually sync with pyproject.toml
};
```

**Why not hardcode:**
- ❌ Two places to update version (error-prone)
- ❌ Easy to forget to sync
- ❌ CI could use different version than Nix

---

#### Decision 2: Hybrid Nix + venv Approach

**Question:** Should Python packages be defined in Nix or use `.venv` with `pyproject.toml`?

**Answer:** ✅ **Hybrid: Nix provides Python interpreter, venv provides packages.**

**Architecture:**

```
┌─────────────────────────────────────────────────────┐
│ Nix Flake (flake.nix)                               │
│                                                      │
│  ✅ Python 3.10 interpreter (ensures version)       │
│  ✅ System tools (git, docker-compose, just)        │
│  ✅ Native libraries (openssl, libffi)              │
│  ❌ NO Python packages                              │
└─────────────────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────┐
│ Virtual Environment (.venv)                         │
│                                                      │
│  ✅ Python packages (pip install -e ".[dev]")       │
│  ✅ Reads from pyproject.toml                       │
│  ✅ Editable install for development                │
└─────────────────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────┐
│ Source of Truth (pyproject.toml)                    │
│                                                      │
│  [project]                                           │
│  dependencies = ["fastapi>=0.122.0", ...]           │
│  [project.optional-dependencies]                     │
│  dev = ["pytest", "ruff", ...]                      │
└─────────────────────────────────────────────────────┘
```

**Why hybrid approach:**

**✅ Benefits:**

1. **Nix guarantees Python version:**
   - Every developer gets Python 3.10 (not 3.9, not 3.11)
   - CI uses exact same Python version
   - No "works on my Python" issues

2. **pip handles Python packages:**
   - Faster package installation (pip cache)
   - Better PyPI compatibility (some packages don't have Nix packages)
   - Editable installs work naturally (`pip install -e .`)
   - Familiar workflow for Python developers

3. **Single dependency list:**
   - `pyproject.toml` is the only place to list dependencies
   - No need to maintain Nix package list separately
   - `pip install -e ".[dev]"` installs everything

4. **Best of both worlds:**
   - Reproducible Python version (Nix)
   - Flexible package management (pip)

**Alternative 1: Pure Nix (NOT RECOMMENDED for this project):**
```nix
# ❌ NOT RECOMMENDED: All packages in Nix
pythonEnv = pkgs.python310.withPackages (ps: with ps; [
  fastapi
  uvicorn
  pydantic
  # ... 50+ packages listed here
]);
```

**Why not pure Nix:**
- ❌ Must maintain two dependency lists (pyproject.toml + flake.nix)
- ❌ Not all PyPI packages available in Nix
- ❌ Nix package updates lag behind PyPI
- ❌ Editable installs more complex
- ❌ Less familiar to Python developers

**Alternative 2: Pure venv without Nix (NOT RECOMMENDED):**
```bash
# ❌ NOT RECOMMENDED: Just python -m venv
python3 -m venv .venv  # Which Python? 3.9? 3.10? 3.11?
```

**Why not pure venv:**
- ❌ No guarantee of Python version consistency
- ❌ Developers use different Python versions (hard to debug)
- ❌ CI might use different Python than local
- ❌ System dependencies (openssl, libffi) version varies

---

### Developer Workflow with Nix

#### Daily Development

```bash
# Navigate to project
cd mailreactor

# Environment auto-activates (direnv)
# No manual activation needed!

# Run tests (Python/pytest available automatically)
pytest tests/

# Start server
mailreactor start

# Type checking
mypy src/

# Linting
ruff check .
```

#### Adding Dependencies

**Standard workflow (Python packages):**

```toml
# pyproject.toml (ONLY place to add dependencies)
[project]
dependencies = [
    "fastapi>=0.122.0",
    "new-package>=1.0.0",  # ← Add runtime dependency here
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "new-dev-tool>=2.0.0",  # ← Add dev dependency here
]
```

```bash
# Install new dependencies
pip install -e ".[dev]"

# Or if venv needs refresh
rm -rf .venv
direnv reload  # Nix will recreate venv and install deps
```

**When to update `flake.nix`:**

Only for **system-level tools** (not Python packages):

```nix
# flake.nix
buildInputs = [
  python
  pkgs.git
  pkgs.docker-compose
  pkgs.new-system-tool  # ← Add system tools here (e.g., ripgrep, fd)
];
```

**Examples:**

| Dependency | Where to Add | Why |
|------------|--------------|-----|
| `requests` | `pyproject.toml` | Python package → pip |
| `pytest` | `pyproject.toml` (dev) | Python package → pip |
| `ripgrep` | `flake.nix` | System tool → Nix |
| `postgresql` | `flake.nix` | System service → Nix |
| `fastapi` | `pyproject.toml` | Python package → pip |

**Rule of thumb:** If it's `pip install <package>`, add to `pyproject.toml`. If it's a system command, add to `flake.nix`.

#### CI Configuration (GitHub Actions)

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Nix
        uses: cachix/install-nix-action@v24
        with:
          extra_nix_config: |
            experimental-features = nix-command flakes
      
      - name: Build Nix environment
        run: nix build
      
      - name: Run tests
        run: nix develop --command pytest tests/
```

---

### Benefits for Mail Reactor

1. **Consistent Python Version:**
   - Everyone uses Python 3.10+ (specified in `flake.nix`)
   - No "pip install failed because wrong Python version" issues

2. **Reproducible Dependencies:**
   - Exact versions locked in `flake.lock`
   - `nix flake update` updates all dependencies atomically

3. **Fast Onboarding:**
   - New developer: `git clone && direnv allow` → ready to code
   - No manual Python installation, virtualenv creation, dependency hunting

4. **CI/CD Parity:**
   - Same `flake.nix` used in CI and locally
   - "Works in CI" = "Works locally"

---

## 3. Cucumber/BDD Assessment

### Question: Do We Need Cucumber?

**Short Answer:** ❌ **No, Cucumber is NOT recommended for Mail Reactor MVP.**

### Analysis

#### What is Cucumber/BDD?

**Cucumber** uses **Gherkin syntax** to write human-readable test scenarios:

```gherkin
# Example Cucumber test (NOT recommended for Mail Reactor)
Feature: Send Email
  As a developer
  I want to send emails via API
  So that my application can notify users

  Scenario: Send plain text email
    Given I have a valid Gmail account configured
    When I send a POST request to /accounts/acc123/messages
    And the request body contains:
      | to      | recipient@example.com |
      | subject | Test Email            |
      | body    | Hello World           |
    Then the response status should be 200
    And the response should contain a message_id
    And the email should be delivered to SMTP server
```

**Then you write Python "step definitions":**
```python
@given("I have a valid Gmail account configured")
def step_impl(context):
    context.account = create_test_account("gmail")

@when("I send a POST request to /accounts/{account_id}/messages")
def step_impl(context, account_id):
    context.response = requests.post(f"/accounts/{account_id}/messages", ...)
```

---

### Why NOT Cucumber for Mail Reactor?

#### Reason 1: Target Audience is Developers (Not Business Stakeholders)

**Cucumber/BDD is designed for:**
- Business analysts to write requirements
- Non-technical stakeholders to understand tests
- Bridging communication gap between business and engineering

**Mail Reactor's audience:**
- **Developers** building applications (technical users)
- **No business analysts** writing requirements
- **No non-technical stakeholders** needing test readability

**Verdict:** BDD's main benefit (business-readable tests) is irrelevant here.

---

#### Reason 2: API Backend = Better Alternatives Exist

**For API testing, these are superior:**

**Option A: Pytest with Clear Test Names (RECOMMENDED)**
```python
# tests/integration/test_send_email.py
@pytest.mark.asyncio
async def test_send_plain_text_email_via_api_returns_message_id(client):
    """
    GIVEN a valid Gmail account configured
    WHEN developer sends POST to /accounts/acc123/messages with plain text
    THEN API returns 200 with message_id
    AND email is delivered to SMTP server
    """
    # Arrange
    account = await create_test_account("gmail")
    
    # Act
    response = await client.post(f"/accounts/{account.id}/messages", json={
        "to": "recipient@example.com",
        "subject": "Test Email",
        "body": "Hello World"
    })
    
    # Assert
    assert response.status_code == 200
    assert "message_id" in response.json()
    
    # Verify SMTP delivery
    assert_email_sent_to_smtp_server(response.json()["message_id"])
```

**Advantages over Cucumber:**
- ✅ Same readability (test name + docstring)
- ✅ No extra framework complexity
- ✅ Faster execution (no Gherkin parsing)
- ✅ Better IDE support (autocomplete, refactoring)
- ✅ Easier debugging (Python debugger works directly)

---

**Option B: OpenAPI Contract Testing (RECOMMENDED)**
```python
# tests/contract/test_openapi_compliance.py
import schemathesis

schema = schemathesis.from_uri("http://localhost:8000/openapi.json")

@schema.parametrize()
def test_api_conforms_to_openapi_spec(case):
    """Auto-generate tests from OpenAPI spec"""
    response = case.call()
    case.validate_response(response)
```

**Advantages over Cucumber:**
- ✅ Auto-generates tests from OpenAPI spec
- ✅ Catches API contract violations automatically
- ✅ No manual test writing for standard CRUD operations
- ✅ Keeps tests in sync with API spec

---

#### Reason 3: Maintenance Burden

**Cucumber requires:**
- Writing Gherkin features (`.feature` files)
- Writing Python step definitions (`@given`, `@when`, `@then`)
- Maintaining mapping between features and steps
- Learning Gherkin syntax (extra cognitive load)

**Pytest requires:**
- Writing Python tests (developers already know Python)

**Verdict:** Cucumber is 2x the work for no benefit in this project.

---

#### Reason 4: TDD Compatibility

**With TDD, you write tests first:**
```python
# TDD with Pytest: Natural
def test_send_email():
    # Write test, run (fails), implement, run (passes)
    pass
```

**With Cucumber, you write:**
1. Gherkin feature file
2. Python step definitions
3. Implementation

**Verdict:** Cucumber adds extra step (Gherkin) to TDD cycle, slowing down red-green-refactor loop.

---

### When WOULD Cucumber Be Appropriate?

**Use Cucumber/BDD if:**
- ✅ Product managers write acceptance tests (Mail Reactor: No PMs writing tests)
- ✅ Business stakeholders need to validate behavior (Mail Reactor: Developers are the stakeholders)
- ✅ Regulated industry requires business-readable test documentation (Mail Reactor: No regulation)
- ✅ Large team with dedicated QA writing tests (Mail Reactor: Small team, TDD developers write tests)

**None of these apply to Mail Reactor.**

---

### Recommendation: Use Pytest with BDD-Style Test Names

Get BDD benefits without Cucumber overhead:

```python
# tests/features/test_account_management.py
class TestAccountManagement:
    """Feature: Account Management"""
    
    @pytest.mark.asyncio
    async def test_developer_can_add_gmail_account_with_auto_detection(self, client):
        """
        Scenario: Add Gmail account with auto-detection
        
        Given I am a developer using Mail Reactor
        When I POST to /accounts with email "user@gmail.com"
        Then the system auto-detects Gmail IMAP/SMTP settings
        And I receive a 201 Created response
        And the account is ready to send/receive emails
        """
        # Test implementation...
        pass
    
    @pytest.mark.asyncio
    async def test_developer_receives_clear_error_for_invalid_credentials(self, client):
        """
        Scenario: Invalid credentials error
        
        Given I provide incorrect password for Gmail account
        When I attempt to connect
        Then I receive a 401 Unauthorized response
        And the error message suggests checking app password settings
        """
        # Test implementation...
        pass
```

**This gives you:**
- ✅ Human-readable test scenarios (in docstrings)
- ✅ BDD structure (Given/When/Then)
- ✅ No Cucumber framework overhead
- ✅ Full Python IDE support
- ✅ Compatible with TDD workflow

---

### Final Verdict on Cucumber

| Aspect | Cucumber | Pytest (BDD-style) | Recommendation |
|--------|----------|-------------------|----------------|
| **Readability** | High (Gherkin) | High (docstrings) | **Pytest** (same benefit, less overhead) |
| **Developer DX** | Medium (extra syntax) | High (pure Python) | **Pytest** |
| **TDD Compatible** | Medium (3 steps) | High (2 steps) | **Pytest** |
| **Maintenance** | High (features + steps) | Low (just tests) | **Pytest** |
| **Tool Support** | Medium (special IDE plugins) | High (all Python tools) | **Pytest** |
| **Execution Speed** | Slower (Gherkin parsing) | Fast (native Python) | **Pytest** |

**Conclusion:** ❌ **Do NOT use Cucumber for Mail Reactor.** Use Pytest with BDD-style test names and docstrings instead.

---

## Summary: Development Practices

### Required Practices

1. ✅ **TDD (Test-Driven Development):**
   - Write tests FIRST (red-green-refactor)
   - No production code without tests
   - Enforced via code review and pre-commit hooks

2. ✅ **Nix Flakes + Direnv:**
   - Reproducible development environment
   - All developers use same Python/dependencies
   - Setup: `git clone && direnv allow`

3. ❌ **Cucumber: NOT REQUIRED**
   - Use Pytest with BDD-style test names instead
   - Same readability, less complexity
   - Better TDD workflow

---

## Sprint 0 Tasks (Updated)

### Additional Sprint 0 Tasks for Development Practices

**Task 6: Create Nix Flake Configuration**
- Create `flake.nix` with Python 3.10+ and dependencies
- Create `.envrc` for direnv auto-activation
- Test on macOS and Linux
- Document Nix installation in `README.md`
- **Estimated Effort:** 3 hours

**Task 7: TDD Documentation and Templates**
- Create `docs/tdd-guide.md` with examples
- Add test templates to `tests/templates/`
- Configure pre-commit hook for test coverage enforcement
- **Estimated Effort:** 2 hours

**Total Additional Sprint 0 Effort:** 5 hours

**Updated Total Sprint 0:** 14 hours (original) + 5 hours = **19 hours (~2.5 days)**

---

## Where This is Captured

### Documentation Locations

1. **This Document:** `docs/development-practices.md`
   - TDD methodology and examples
   - Nix flakes setup instructions
   - Cucumber/BDD assessment

2. **Test Design Document:** `docs/test-design-system.md`
   - References TDD requirement
   - Updated Sprint 0 tasks with Nix/TDD setup

3. **README.md** (to be created in Sprint 0):
   - Quick start with Nix
   - TDD workflow summary
   - Link to full development practices

4. **Architecture Document:** `docs/architecture.md`
   - References this document in "Development Workflow" section

---

## Enforcement

### Code Review Checklist

**Reviewers must verify:**
- [ ] Tests written BEFORE implementation (check git history)
- [ ] All tests pass (`pytest` green in CI)
- [ ] Coverage ≥80% (automated check)
- [ ] Nix flake builds successfully (`nix flake check`)
- [ ] No Cucumber/Gherkin files added (use Pytest instead)

### CI Checks

**Automated enforcement:**
- Coverage report fails if <80%
- Nix flake check runs on every PR
- Ruff/mypy linting passes
- Pre-commit hooks prevent bad commits

---

**This document is the single source of truth for Mail Reactor development practices.**

All developers must read and follow these practices before contributing code.
