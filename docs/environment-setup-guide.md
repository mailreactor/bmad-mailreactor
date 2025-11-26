# Mail Reactor - Environment Setup Guide

**Date:** 2025-11-26  
**Status:** Sprint 0 - Priority #1 (Must be tested FIRST)  
**Platforms:** Nix (macOS/Linux), Manual (Windows/WSL2/No-Nix)

---

## Overview

Mail Reactor supports **two setup methods**:

1. **Nix Flakes (Recommended)** - Reproducible, automated, all platforms
2. **Manual Setup** - Traditional Python workflow, fallback for Windows/no-Nix users

**Both methods MUST work perfectly before any implementation begins.**

---

## Sprint 0 Task #1: VERIFY BOTH SETUPS WORK

**Priority:** 🔴 **CRITICAL - BLOCKING**

**Success Criteria:**
- ✅ Nix setup works on macOS and Linux
- ✅ Manual setup works on Windows, WSL2, and Linux (no Nix)
- ✅ Both setups produce identical Python environment
- ✅ Tests run successfully in both environments
- ✅ Documentation verified step-by-step

**Verification:** HC will personally test Windows + WSL2, team tests macOS/Linux.

---

## Method 1: Nix Flakes Setup (Recommended)

**Platforms:** macOS, Linux, WSL2 (with Nix installed)

### Prerequisites

**One-time installation:**

```bash
# Install Nix (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install

# Install direnv
# macOS:
brew install direnv

# Linux:
sudo apt install direnv  # Debian/Ubuntu
# or
curl -sfL https://direnv.net/install.sh | bash

# Add to shell (~/.bashrc or ~/.zshrc)
eval "$(direnv hook bash)"   # for bash
eval "$(direnv hook zsh)"    # for zsh

# Install nix-direnv (IMPORTANT: Much faster Nix integration)
# This caches Nix environments and makes direnv 10-100x faster
nix-env -iA nixpkgs.nix-direnv

# Configure nix-direnv
mkdir -p ~/.config/direnv
cat > ~/.config/direnv/direnvrc << 'EOF'
source $HOME/.nix-profile/share/nix-direnv/direnvrc
EOF

# Verify installation
direnv version    # Should show direnv version
nix-direnv-reload # Should work if nix-direnv installed
```

### Setup Steps

```bash
# 1. Clone repository
git clone https://github.com/yourusername/mailreactor.git
cd mailreactor

# 2. Allow direnv (triggers Nix environment setup)
direnv allow

# Expected output:
# direnv: loading ~/mailreactor/.envrc
# 🚀 Mail Reactor Development Environment
# Project: mailreactor v0.1.0
# Python: Python 3.10.x
# Location: /nix/store/.../bin/python
#
# 📦 Creating virtualenv...
# 📦 Installing Python dependencies from pyproject.toml...
# ✅ Environment ready!

# 3. Verify setup
python --version        # Should be Python 3.10.x
which python            # Should point to Nix store
uv --version            # Should show uv version
pytest --version        # Should show pytest version

# 4. Run health check
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"

# 5. Run tests (should work immediately)
pytest tests/ -v

# 6. Start server (when implemented)
mailreactor start
```

### What Happens Automatically

When you run `direnv allow`:

1. **nix-direnv caches Nix environment:**
   - First run: Builds Nix environment (~30s)
   - Subsequent runs: Loads from cache (~1s)
   - 10-100x faster than plain direnv

2. **Nix provides:**
   - Python 3.10 interpreter (exact version)
   - System tools: git, docker-compose, just, jq, uv
   - Native libraries: openssl, libffi

3. **uv creates virtualenv:**
   - `.venv/` directory created (first time only)
   - Python packages installed from `pyproject.toml` via uv
   - Development tools: pytest, ruff, mypy

4. **Environment activated:**
   - `.venv/bin` added to PATH
   - `PYTHONPATH` configured
   - Ready to code immediately

**Performance:**
- First activation: ~30-60 seconds (Nix build + uv install)
- Subsequent activations: ~1 second (nix-direnv cache!)
- Changes to `flake.nix`: ~5 seconds (incremental rebuild)
- Changes to `pyproject.toml`: ~5 seconds (uv reinstall)

### Troubleshooting Nix Setup

**Issue: `direnv: error .envrc is blocked`**
```bash
# Solution: Allow direnv
direnv allow
```

**Issue: `python: command not found`**
```bash
# Solution: Reload direnv
direnv reload
```

**Issue: `uv: command not found`**
```bash
# Check flake.nix includes uv
# Should be in buildInputs
direnv reload
```

**Issue: Slow direnv activation (>10 seconds)**
```bash
# Solution: Install nix-direnv (caches environments)
nix-env -iA nixpkgs.nix-direnv

# Configure direnvrc
mkdir -p ~/.config/direnv
cat > ~/.config/direnv/direnvrc << 'EOF'
source $HOME/.nix-profile/share/nix-direnv/direnvrc
EOF

# Reload
direnv reload
# Should now be ~1 second (cached)
```

**Issue: `nix_direnv_version: command not found` in .envrc**
```bash
# nix-direnv not installed - fallback to plain use flake
# Either install nix-direnv (recommended) or edit .envrc to just "use flake"

# Option 1: Install nix-direnv (recommended)
nix-env -iA nixpkgs.nix-direnv

# Option 2: Use plain direnv (slower)
# Edit .envrc, replace first lines with just:
# use flake
```

**Issue: Packages not installing**
```bash
# Manually trigger install
source .venv/bin/activate
uv pip install -e ".[dev]"
```

**Issue: `GC Warning` messages on macOS**
```bash
# Harmless Nix garbage collection warnings
# Can be ignored or suppressed with:
export GC_DONT_GC=1
# Add to .envrc if annoying
```

---

## Method 2: Manual Setup (Windows/WSL2/No-Nix)

**Platforms:** Windows, WSL2, macOS, Linux (without Nix)

### Prerequisites

**Required:**
- Python 3.10 or higher ([python.org/downloads](https://python.org/downloads))
- Git ([git-scm.com](https://git-scm.com))
- pip (comes with Python)

**Recommended:**
- uv (faster than pip) - [docs.astral.sh/uv](https://docs.astral.sh/uv)

### Install uv (Recommended)

**Windows (PowerShell):**
```powershell
# Install uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify
uv --version
```

**macOS/Linux:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify
uv --version
```

**Fallback (if uv fails):**
```bash
# Use pip instead
pip install uv
```

### Setup Steps

#### Windows (PowerShell)

```powershell
# 1. Clone repository
git clone https://github.com/yourusername/mailreactor.git
cd mailreactor

# 2. Verify Python version
python --version
# Must be Python 3.10 or higher!

# 3. Create virtual environment
python -m venv .venv

# 4. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# If execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 5. Upgrade uv in venv
uv pip install --upgrade uv

# 6. Install dependencies
uv pip install -e ".[dev]"

# 7. Verify installation
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
pytest --version
ruff --version

# 8. Run tests
pytest tests\ -v

# 9. Start server (when implemented)
python -m mailreactor start
```

#### Linux/WSL2/macOS (No Nix)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/mailreactor.git
cd mailreactor

# 2. Verify Python version
python3 --version
# Must be Python 3.10 or higher!

# 3. Create virtual environment
python3 -m venv .venv

# 4. Activate virtual environment
source .venv/bin/activate

# 5. Upgrade uv in venv
uv pip install --upgrade uv

# 6. Install dependencies
uv pip install -e ".[dev]"

# 7. Verify installation
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
pytest --version
ruff --version

# 8. Run tests
pytest tests/ -v

# 9. Start server (when implemented)
mailreactor start
```

### Troubleshooting Manual Setup

**Issue: Python version too old (< 3.10)**
```bash
# Windows: Download from python.org
# macOS: brew install python@3.10
# Linux: sudo apt install python3.10 python3.10-venv
```

**Issue: `uv: command not found`**
```bash
# Fallback to pip
pip install -e ".[dev]"
```

**Issue: Permission denied (Linux/macOS)**
```bash
# Don't use sudo!
# Make sure you're in virtual environment
source .venv/bin/activate
```

**Issue: Module not found errors**
```bash
# Reinstall dependencies
uv pip install --upgrade -e ".[dev]"
```

---

## Why UV Instead of PIP?

**Answer:** ✅ **YES, use `uv` for all Python package management.**

### UV Benefits

| Aspect | pip | uv | Winner |
|--------|-----|----|----|
| **Speed** | Slow (minutes) | 10-100x faster (seconds) | ✅ **uv** |
| **Dependency resolution** | Can get stuck | Fast resolver | ✅ **uv** |
| **Cache** | Limited | Smart caching | ✅ **uv** |
| **Lockfile** | No | Yes (uv.lock) | ✅ **uv** |
| **Drop-in replacement** | - | Yes (`uv pip install`) | ✅ **uv** |

### Speed Comparison

```bash
# pip (traditional)
time pip install -e ".[dev]"
# Result: ~60 seconds

# uv (modern)
time uv pip install -e ".[dev]"
# Result: ~5 seconds
```

**10-100x faster dependency installation!**

### UV Commands

**uv is a drop-in replacement for pip:**

```bash
# Old way (pip)                  # New way (uv)
pip install package              uv pip install package
pip install -e ".[dev]"          uv pip install -e ".[dev]"
pip list                         uv pip list
pip freeze                       uv pip freeze
pip uninstall package            uv pip uninstall package
```

**Additional uv features:**

```bash
# Create venv and install in one command
uv venv
uv pip install -e ".[dev]"

# Sync dependencies from lockfile (if using uv.lock)
uv pip sync

# Compile dependencies to lockfile
uv pip compile pyproject.toml
```

---

## Verification Checklist (Sprint 0 Task #1)

**Both setups must pass ALL checks before continuing to other Sprint 0 tasks.**

### ✅ Nix Setup Verification

**Tester:** Team member with macOS or Linux

```bash
cd mailreactor

# 1. Environment loads
direnv allow
# ✅ PASS: No errors, environment activates

# 2. nix-direnv cache created (IMPORTANT!)
ls -la .direnv/
# ✅ PASS: Directory exists with flake-profile* files
# This confirms nix-direnv is working

# 3. Python version correct
python --version
# ✅ PASS: Python 3.10.x

# 4. Python from Nix store
which python
# ✅ PASS: Points to /nix/store/...

# 5. uv available
uv --version
# ✅ PASS: Shows version

# 6. Dependencies installed
python -c "import fastapi, uvicorn, pydantic, pytest"
# ✅ PASS: No import errors

# 7. Dev tools work
ruff --version
mypy --version
pytest --version
# ✅ PASS: All show versions

# 8. Project structure correct
ls -la src/mailreactor
# ✅ PASS: Directory exists (will be created in Epic 1)

# 9. Can run tests (once tests exist)
pytest tests/ -v
# ✅ PASS: Tests run (or "no tests collected" if none yet)

# 10. Can activate manually
source .venv/bin/activate
python --version
# ✅ PASS: Python works

# 11. nix-direnv caching works (CRITICAL TEST!)
cd .. && time (cd mailreactor && python --version)
# ✅ PASS: Takes ~1 second (not 30+ seconds)
# If this takes 30s, nix-direnv is NOT working!

# 12. Environment reproduced after clean
rm -rf .venv
direnv reload
python --version
# ✅ PASS: Environment recreates successfully
```

### ✅ Manual Setup Verification (Windows)

**Tester:** HC (Windows)

```powershell
cd mailreactor

# 1. Python version correct
python --version
# ✅ PASS: Python 3.10.x or higher

# 2. Virtual environment created
python -m venv .venv
# ✅ PASS: .venv\ directory created

# 3. Activation works
.\.venv\Scripts\Activate.ps1
# ✅ PASS: (venv) appears in prompt

# 4. uv available
uv --version
# ✅ PASS: Shows version (or fallback to pip)

# 5. Dependencies install
uv pip install -e ".[dev]"
# ✅ PASS: No errors, packages installed

# 6. Dependencies work
python -c "import fastapi, uvicorn, pydantic, pytest"
# ✅ PASS: No import errors

# 7. Dev tools work
ruff --version
mypy --version
pytest --version
# ✅ PASS: All show versions

# 8. Can run tests (once tests exist)
pytest tests\ -v
# ✅ PASS: Tests run (or "no tests collected")

# 9. Can deactivate/reactivate
deactivate
.\.venv\Scripts\Activate.ps1
python --version
# ✅ PASS: Python in venv

# 10. Clean reinstall works
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
uv pip install -e ".[dev]"
# ✅ PASS: Environment recreates successfully
```

### ✅ Manual Setup Verification (Linux/WSL2)

**Tester:** HC (WSL2)

```bash
cd mailreactor

# 1. Python version correct
python3 --version
# ✅ PASS: Python 3.10.x or higher

# 2. Virtual environment created
python3 -m venv .venv
# ✅ PASS: .venv/ directory created

# 3. Activation works
source .venv/bin/activate
# ✅ PASS: (venv) appears in prompt

# 4. uv available
uv --version
# ✅ PASS: Shows version (or fallback to pip)

# 5. Dependencies install
uv pip install -e ".[dev]"
# ✅ PASS: No errors, packages installed

# 6. Dependencies work
python -c "import fastapi, uvicorn, pydantic, pytest"
# ✅ PASS: No import errors

# 7. Dev tools work
ruff --version
mypy --version
pytest --version
# ✅ PASS: All show versions

# 8. Can run tests (once tests exist)
pytest tests/ -v
# ✅ PASS: Tests run (or "no tests collected")

# 9. Can deactivate/reactivate
deactivate
source .venv/bin/activate
python --version
# ✅ PASS: Python in venv

# 10. Clean reinstall works
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
uv pip install -e ".[dev]"
# ✅ PASS: Environment recreates successfully
```

---

## Environment Comparison

**Both setups must produce equivalent environments:**

| Aspect | Nix Setup | Manual Setup | Must Match? |
|--------|-----------|--------------|-------------|
| Python version | 3.10.x | 3.10.x | ✅ YES (major.minor) |
| FastAPI version | (from pyproject.toml) | (from pyproject.toml) | ✅ YES |
| All dependencies | (from pyproject.toml) | (from pyproject.toml) | ✅ YES |
| Dev tools | ruff, mypy, pytest | ruff, mypy, pytest | ✅ YES |
| Tests pass | ✅ | ✅ | ✅ YES |

**Command to verify parity:**

```bash
# In both environments, run:
uv pip list > packages.txt

# Compare outputs - should be identical (except Nix system packages)
```

---

## Sprint 0 Task #1 Deliverables

**MUST complete before any other Sprint 0 tasks:**

### 1. Working Configurations

- [ ] `flake.nix` - Nix configuration (using uv)
- [ ] `.envrc` - direnv auto-activation
- [ ] `pyproject.toml` - Project metadata and dependencies
- [ ] `.gitignore` - Ignore .venv, .direnv, etc.

### 2. Documentation

- [ ] This file: `docs/environment-setup-guide.md`
- [ ] `README.md` - Quick start for both methods
- [ ] `docs/troubleshooting.md` - Common setup issues

### 3. Verification Reports

- [ ] Nix setup verified on macOS (team member)
- [ ] Nix setup verified on Linux (team member)
- [ ] Manual setup verified on Windows (HC)
- [ ] Manual setup verified on WSL2 (HC)
- [ ] Manual setup verified on Linux without Nix (team member)

### 4. CI Configuration

- [ ] GitHub Actions uses Nix setup
- [ ] Includes matrix testing (Python 3.10, 3.11, 3.12)
- [ ] Runs on ubuntu-latest (Nix available)

---

## Estimated Effort (Updated)

**Sprint 0 Task #1: Environment Setup & Verification**

| Subtask | Effort | Owner |
|---------|--------|-------|
| Create flake.nix (with uv) | 2h | Dev |
| Create pyproject.toml | 1h | Dev |
| Create .envrc and .gitignore | 0.5h | Dev |
| Write setup documentation | 2h | Dev |
| Test Nix on macOS | 1h | Team |
| Test Nix on Linux | 1h | Team |
| Test Manual on Windows | 1h | HC |
| Test Manual on WSL2 | 1h | HC |
| Test Manual on Linux (no Nix) | 1h | Team |
| Fix issues and iterate | 2h | Team |
| Document troubleshooting | 1h | Dev |
| **Total** | **13.5h (~2 days)** | - |

**BLOCKING:** No other Sprint 0 tasks start until Task #1 is 100% verified.

---

## Success Criteria

**Task #1 is DONE when:**

✅ HC confirms: "Windows setup works perfectly"  
✅ HC confirms: "WSL2 setup works perfectly"  
✅ Team confirms: "Nix setup works on macOS"  
✅ Team confirms: "Nix setup works on Linux"  
✅ Team confirms: "Manual Linux (no Nix) works"  
✅ All verification checklists pass  
✅ Documentation is clear and complete  
✅ Both methods produce identical environments  

**Only then proceed to remaining Sprint 0 tasks (mock servers, CI, etc.).**

---

## Daily Development Workflow

**After initial setup, daily workflow is simple:**

### With Nix:
```bash
cd mailreactor   # direnv auto-activates
pytest tests/    # Just works
```

### Manual:
```bash
cd mailreactor
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1
pytest tests/
```

Both workflows should feel natural and "just work" after Sprint 0 verification.

---

## References

- **UV Documentation:** [docs.astral.sh/uv](https://docs.astral.sh/uv)
- **Nix Flakes:** [nixos.wiki/wiki/Flakes](https://nixos.wiki/wiki/Flakes)
- **Python venv:** [docs.python.org/3/library/venv.html](https://docs.python.org/3/library/venv.html)
- **direnv:** [direnv.net](https://direnv.net)

---

**This guide MUST be tested and working before any implementation begins.**

**HC will verify Windows/WSL2. Team verifies macOS/Linux.**
