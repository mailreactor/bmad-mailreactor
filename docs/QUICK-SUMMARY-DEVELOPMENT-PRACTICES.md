# Quick Summary: Development Practices for Mail Reactor

**Created:** 2025-11-26  
**For:** HC (before meeting)  
**Status:** Ready for team review

---

## Your Questions Answered

### 1. ✅ TDD (Test-Driven Development) - REQUIRED

**Answer:** YES, all developers MUST use TDD for Mail Reactor.

**What this means:**
- Write test FIRST (it fails - red)
- Write minimal code to pass test (green)
- Refactor code while keeping test green
- **Never** write production code without a test

**Enforcement:**
- Code review checks git history (test committed before implementation)
- Pre-commit hooks enforce 80% coverage minimum
- Sprint retrospectives track TDD compliance

**Where documented:** `docs/development-practices.md` Section 1

---

### 2. ✅ Nix Flakes + Direnv - REQUIRED

**Answer:** YES, all developers MUST use Nix for reproducible environments.

**What this means:**
- Every developer has identical Python version, dependencies, tools
- No "works on my machine" issues
- Setup: `git clone && direnv allow` → ready to code
- CI uses same `flake.nix` → local = CI

**Developer experience:**
```bash
cd mailreactor       # Navigate to project
# Environment auto-activates! (direnv magic)
pytest tests/        # Run tests (all tools available)
mailreactor start    # Start server
```

**Architecture (Hybrid Approach):**
- **Nix provides:** Python 3.10 interpreter + system tools
- **venv provides:** Python packages (via pip from pyproject.toml)
- **Version source of truth:** `pyproject.toml` (Nix reads from there)

**Sprint 0 task:** Create `flake.nix` and `.envrc` (3 hours)

**Where documented:** 
- `docs/development-practices.md` Section 2 (full guide)
- `docs/.nix-architecture-decisions.md` (design decisions)

---

### 3. ❌ Cucumber/BDD - NOT RECOMMENDED

**Answer:** NO, do NOT use Cucumber for Mail Reactor.

**Why not:**
- Mail Reactor's users are **developers** (not business analysts)
- No non-technical stakeholders need to read tests
- Cucumber adds complexity without benefit
- Pytest with BDD-style test names achieves same readability

**What to use instead:**

Pytest with clear test names and docstrings:

```python
def test_developer_can_add_gmail_account_with_auto_detection():
    """
    Scenario: Add Gmail account with auto-detection
    
    Given I am a developer using Mail Reactor
    When I POST to /accounts with email "user@gmail.com"
    Then the system auto-detects Gmail IMAP/SMTP settings
    And I receive a 201 Created response
    """
    # Test implementation in plain Python
    pass
```

**Benefits:**
- ✅ Same readability as Cucumber
- ✅ Pure Python (no Gherkin syntax to learn)
- ✅ Better IDE support
- ✅ Faster execution
- ✅ Compatible with TDD workflow

**Where documented:** `docs/development-practices.md` Section 3 (full analysis)

---

## Documents Created

### 1. `docs/development-practices.md` (MAIN DOCUMENT)

**Sections:**
1. TDD methodology with examples (red-green-refactor)
2. Nix flakes + direnv setup instructions
3. Cucumber/BDD assessment (why NOT to use it)

**Status:** Complete, ready for team review

---

### 2. `docs/test-design-system.md` (UPDATED)

**Changes:**
- Added reference to development practices
- Updated Sprint 0 tasks to include Nix + TDD setup
- Added note on Cucumber (not recommended)

**Sprint 0 updated total:** 19 hours (~2.5 days)

---

## Sprint 0 Tasks (Updated)

**Original 5 tasks:** 14 hours
- Mock IMAP/SMTP server (4h)
- Performance benchmarks (3h)
- Security scanning (2h)
- Test project structure (2h)
- CI pipeline (3h)

**NEW tasks for your requirements:** +5 hours
- **Task 6:** Nix flake configuration (3h)
- **Task 7:** TDD documentation and templates (2h)

**Updated total:** 19 hours (~2.5 days)

---

## Key Decisions Summary

| Topic | Decision | Rationale |
|-------|----------|-----------|
| **TDD** | ✅ REQUIRED | Prevents bugs, documents behavior, enables refactoring |
| **Nix Flakes** | ✅ REQUIRED | Reproducible environments, fast onboarding, CI/local parity |
| **Cucumber** | ❌ NOT RECOMMENDED | Developer audience doesn't need business-readable tests, Pytest is simpler |

---

## Action Items for Team

### Before Implementation Starts:

1. **Read:** `docs/development-practices.md` (all developers)
2. **Setup:** Install Nix and direnv (one-time, ~15 minutes)
3. **Review:** TDD workflow and examples
4. **Complete:** Sprint 0 tasks (19 hours total)

### Code Review Checklist (Updated):

- [ ] Tests written BEFORE implementation (check git history)
- [ ] All tests pass (green in CI)
- [ ] Coverage ≥80%
- [ ] Nix flake builds successfully
- [ ] No Cucumber/Gherkin files added

---

## Quick Reference for Meeting

**If asked:** "Do we use TDD?"  
**Answer:** YES, mandatory. Write test first (red), implement (green), refactor.

**If asked:** "How do we set up dev environment?"  
**Answer:** Nix flakes with direnv. Clone repo, run `direnv allow`, ready to code.

**If asked:** "Should we use Cucumber for BDD?"  
**Answer:** NO. Use Pytest with BDD-style test names instead (same readability, less complexity).

**If asked:** "Where is this documented?"  
**Answer:** `docs/development-practices.md` - complete guide with examples.

**If asked:** "What's the impact on Sprint 0?"  
**Answer:** +5 hours (total now 19 hours / ~2.5 days) for Nix + TDD setup.

---

## Files to Review After Meeting

1. **`docs/development-practices.md`** - Full guide (read this first)
2. **`docs/test-design-system.md`** - Test design with updated Sprint 0 tasks
3. **`docs/epics.md`** - Epic breakdown (already references TDD in stories)

---

## Next Steps

1. ✅ Development practices documented
2. ✅ Test design updated with new requirements
3. ⏭️ Team reviews documents
4. ⏭️ Sprint 0: Create `flake.nix`, `.envrc`, TDD templates
5. ⏭️ Implementation starts with TDD + Nix environment

---

**All your requirements are now captured and documented. Have a great meeting! 🚀**
