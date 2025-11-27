# Sprint 0 Agent Collaboration Guide

**Project:** Mail Reactor  
**Date:** 2025-11-26  
**Purpose:** Guide for collaborating with AI agents during Sprint 0 infrastructure setup

---

## Overview

You can collaborate with AI agents on Sprint 0 tasks. Agents handle the "thinking" work (generating configs, writing documentation, debugging), while you handle the "doing" work (running commands on real machines, verifying on actual hardware).

---

## Sprint 0 Agent Collaboration Guide

### **Task #1: Environment Setup & Verification (10h)**

**Best Agent:** 🔧 **Dev Agent** (`dev`)  
**Command:** `/bmad:bmm:workflows:dev-story` (or just chat with dev agent)

**What Dev can help with:**
- ✅ Review/improve `flake.nix` configuration
- ✅ Review/improve `pyproject.toml` dependencies
- ✅ Troubleshoot Nix flakes issues
- ✅ Debug Python virtual environment problems
- ✅ Fix import errors or dependency conflicts

**What Dev CANNOT do:**
- ❌ Actually run commands on your Windows machine
- ❌ Verify setup on real hardware (you must test)
- ❌ Install Nix on your system (manual step)

**How to collaborate:**
1. Create the config files using checklist templates
2. Ask Dev: "Review my `flake.nix` - does it look correct?"
3. Try setup on your machine
4. If errors: "Dev, I'm getting error X when running Y command, help debug"

---

### **TDD Training Workshop (2-4h)**

**Best Agent:** 🧪 **TEA Agent** (`tea`) - Test/Quality Expert  
**Alternative:** Dev Agent can also help

**What TEA can help with:**
- ✅ Create TDD workshop content/slides
- ✅ Generate example red-green-refactor exercises
- ✅ Explain pytest patterns and best practices
- ✅ Review test code quality
- ✅ Design test scenarios for stories

**How to collaborate:**
1. Ask TEA: "Create a 2-hour TDD workshop agenda for Mail Reactor team"
2. Ask TEA: "Generate a red-green-refactor example using Story 2.1 (Provider Detection)"
3. Deliver workshop to your team (you present, using TEA's materials)

---

### **Task #2: TDD Infrastructure (2h)**

**Best Agent:** 🧪 **TEA Agent** (`tea`)  
**Alternative:** Dev Agent for technical config

**What TEA can help with:**
- ✅ Write `docs/tdd-guide.md` content
- ✅ Create test templates (unit, integration, E2E)
- ✅ Design pre-commit hook configuration
- ✅ Write code review checklist items

**What Dev can help with:**
- ✅ Debug pre-commit hook failures
- ✅ Configure Ruff, mypy settings
- ✅ Fix pytest configuration issues

**How to collaborate:**
1. Ask TEA: "Write a comprehensive TDD guide for `docs/tdd-guide.md`"
2. Ask TEA: "Create test templates for `tests/templates/`"
3. Ask Dev: "My pre-commit hook is failing with error X, help fix"

---

### **Task #3: Mock IMAP/SMTP Server Setup (4h)**

**Best Agent:** 🧪 **TEA Agent** (`tea`)  
**Why:** Test infrastructure is TEA's domain

**What TEA can help with:**
- ✅ Review/improve Docker Compose configuration
- ✅ Create pytest fixtures for mock servers
- ✅ Write integration test examples
- ✅ Document mock server API usage

**What you must do:**
- ❌ Actually run `docker-compose up` on your machine
- ❌ Verify mock servers are accessible (manual test)

**How to collaborate:**
1. Ask TEA: "Review my `docker-compose.test.yml` - is Greenmail configured correctly?"
2. Ask TEA: "Create pytest fixtures in `conftest.py` for IMAP/SMTP mocking"
3. Test manually: Run Docker, verify ports accessible
4. If issues: "TEA, mock IMAP connection failing with error X, help debug"

---

### **Task #4: Test Project Structure (2h)**

**Best Agent:** 🧪 **TEA Agent** (`tea`)

**What TEA can help with:**
- ✅ Design optimal test directory structure
- ✅ Write testing philosophy documentation
- ✅ Create example tests for each category
- ✅ Explain test distribution strategy (50% unit, 35% integration, 15% E2E)

**How to collaborate:**
1. Ask TEA: "Write testing philosophy documentation for `tests/README.md`"
2. Ask TEA: "Create example unit, integration, and E2E tests"
3. You create the directories (simple `mkdir` commands)

---

### **Task #5: Security Scanning Setup (2h)**

**Best Agent:** 🧪 **TEA Agent** (`tea`)  
**Alternative:** Architect for security review

**What TEA can help with:**
- ✅ Create log scanning integration tests
- ✅ Define credential regex patterns
- ✅ Write security test cases
- ✅ Configure `detect-secrets` baseline

**What Architect can help with:**
- ✅ Review security testing strategy
- ✅ Validate credential handling patterns
- ✅ Architecture-level security review

**How to collaborate:**
1. Ask TEA: "Create `tests/security/test_credential_leaks.py` with regex patterns"
2. Ask Architect: "Review our security scanning approach for NFR-S1 compliance"

---

### **Task #6: Performance Benchmark Infrastructure (3h)**

**Best Agent:** 🧪 **TEA Agent** (`tea`)

**What TEA can help with:**
- ✅ Create pytest-benchmark tests
- ✅ Write performance test cases (startup time, API latency)
- ✅ Design GitHub Actions benchmark workflow
- ✅ Document performance testing approach

**How to collaborate:**
1. Ask TEA: "Create `tests/performance/test_startup.py` with NFR-P1 validation"
2. Ask TEA: "Write GitHub Actions workflow for performance benchmarks"
3. You run benchmarks manually to establish baseline

---

### **Task #7: CI/CD Pipeline Configuration (3h)**

**Best Agent:** 🏗️ **Architect Agent** (`architect`)  
**Alternative:** Dev for GitHub Actions syntax

**What Architect can help with:**
- ✅ Design CI/CD pipeline stages
- ✅ Review GitHub Actions workflow configuration
- ✅ Configure branch protection strategy
- ✅ Validate pipeline aligns with architecture

**What Dev can help with:**
- ✅ Debug GitHub Actions YAML syntax
- ✅ Fix Nix-specific CI issues
- ✅ Troubleshoot Docker in CI

**How to collaborate:**
1. Ask Architect: "Review my `.github/workflows/ci.yml` - does it meet NFR requirements?"
2. Ask Dev: "CI failing on Python 3.11 with error X, help debug"
3. You configure branch protection in GitHub UI (manual step)

---

## Optimal Sprint 0 Agent Workflow

**Recommended collaboration pattern:**

### **Phase 1: Configuration Generation (Day 1 morning - ~2h)**

**Chat with Dev Agent:**
```
You: "I'm starting Sprint 0 Task #1. Review my flake.nix and pyproject.toml from the checklist. Any improvements needed for Mail Reactor?"

Dev: [Reviews configs, suggests improvements]

You: "Great, I'll test these on my Windows machine now."
```

**Chat with TEA Agent:**
```
You: "Create comprehensive content for docs/tdd-guide.md, test templates, and conftest.py fixtures per Sprint 0 checklist."

TEA: [Generates all test infrastructure content]

You: "Perfect, I'll commit these files."
```

---

### **Phase 2: Troubleshooting (Day 1-2 - as needed)**

**When you hit issues:**
```
You: "Dev, my Nix flake is giving error: 'attribute python310 missing'. How do I fix?"

Dev: [Provides fix, updated config]

You: "TEA, my pytest fixtures aren't working with the mock IMAP server. Here's the error..."

TEA: [Debugs fixture code, provides correction]
```

---

### **Phase 3: Documentation & CI (Day 3 - ~3h)**

**Chat with TEA:**
```
You: "Write testing philosophy for tests/README.md and performance testing documentation."

TEA: [Generates documentation]
```

**Chat with Architect:**
```
You: "Review my GitHub Actions CI workflow. Does it enforce all NFRs and quality gates?"

Architect: [Reviews, validates against architecture requirements]
```

---

## Quick Reference: Agent Specialties

| Task | Primary Agent | Alternative | Human Must Do |
|------|---------------|-------------|---------------|
| **Environment configs** | Dev | - | Test on real machines |
| **TDD workshop** | TEA | Dev | Deliver workshop |
| **Test templates** | TEA | - | Commit files |
| **Mock servers** | TEA | - | Run Docker, verify |
| **Test structure** | TEA | - | Create directories |
| **Security tests** | TEA | Architect | Configure GitHub |
| **Performance tests** | TEA | - | Run benchmarks |
| **CI/CD pipeline** | Architect | Dev | GitHub UI config |

---

## Revised Sprint 0 Timeline (With Agent Help)

**Day 1 Morning (2h):**
- Chat with Dev: Generate/review environment configs
- Chat with TEA: Generate test infrastructure content
- **You:** Create files from agent output

**Day 1 Afternoon (4h):**
- **You:** Test environment setup on Windows ← **Manual**
- Chat with Dev: Debug any issues
- **You:** Have team test macOS/Linux ← **Manual**

**Day 2 Morning (2h):**
- Chat with TEA: Generate TDD workshop materials
- **You:** Deliver workshop to team ← **Manual** (optional)

**Day 2 Afternoon (3h):**
- **You:** Install Docker, start mock servers ← **Manual**
- Chat with TEA: Debug any mock server issues
- **You:** Run example tests, verify working

**Day 3 (3h):**
- Chat with TEA: Generate documentation
- Chat with Architect: Review CI/CD workflow
- **You:** Configure GitHub branch protection ← **Manual** (UI clicks)
- **You:** Push to GitHub, verify CI runs ← **Manual**

**Total Time: Still ~3 days, but agents do the "thinking" work**

---

## Agent Communication Tips

### **How to Get Best Results from Agents**

**Be Specific:**
- ❌ Bad: "Help with tests"
- ✅ Good: "Create pytest fixtures in conftest.py for mock IMAP server at localhost:3143"

**Provide Context:**
- ❌ Bad: "This isn't working"
- ✅ Good: "Running `uv venv` on Windows gives error 'python310 not found'. I'm using Python 3.11. Here's my flake.nix: [paste file]"

**Reference Checklist:**
- ✅ "Per Sprint 0 Task #3 Subtask 3.2, create the mock server documentation for tests/README.md"

**Share Errors:**
- ✅ "Here's the full error output: [paste traceback]"

---

### **Which Agent for Debugging?**

**Environment/Dependency Issues → Dev**
- Python import errors
- Virtual environment problems
- Nix flakes issues
- Package conflicts

**Test Infrastructure Issues → TEA**
- Pytest configuration
- Mock server setup
- Fixture problems
- Test coverage issues

**Architecture/Design Questions → Architect**
- "Does this CI pipeline meet NFR requirements?"
- "Is this security approach aligned with ADR-002?"
- "Should we defer Epic 6?"

**Process/Workflow Questions → SM (Bob)**
- Sprint planning
- Story estimation
- Backlog prioritization
- (Note: Not involved in Sprint 0)

---

## Your Next Move

**Recommended approach:**

### **Option A: Start Now with Agent Help (RECOMMENDED)**

**Step 1: Environment Setup (Day 1)**
   - Open `docs/sprint-artifacts/sprint-0-checklist.md`
   - Copy `flake.nix`, `pyproject.toml` templates
   - Ask Dev agent: "Review these configs for Mail Reactor"
   - Test on your Windows machine
   - Report results, ask for help if issues

**Step 2: Test Infrastructure (Day 1-2)**
   - Ask TEA: "Generate all content for Sprint 0 Tasks #2-6"
   - Review TEA's output, commit to repo
   - Test manually (Docker, pre-commit, etc.)

**Step 3: CI/CD (Day 3)**
   - Ask Architect: "Review my GitHub Actions workflow"
   - Configure GitHub UI (branch protection)
   - Verify CI runs successfully

---

### **Option B: Do Task #1 Solo, Then Get Help**

**Step 1: Environment Setup (You, Day 1)**
   - Create configs from checklist
   - Test on Windows/Linux
   - Document any issues

**Step 2: Come Back for Help (Day 2)**
   - Ask agents: "Here's what worked/didn't work, help with Tasks #2-7"

---

### **Option C: Review Checklist More Thoroughly First**

**Step 1: Deep Read**
   - Read full Sprint 0 checklist
   - Read Implementation Readiness Report
   - Understand all 7 tasks in detail

**Step 2: Decide Approach**
   - Full Sprint 0 now vs minimal Sprint 0
   - Solo vs agent collaboration
   - Timeline preferences

---

## Decision Checkpoint

**Where are you now:**
- ✅ Phase 2 (Solutioning) complete
- ✅ Implementation Readiness Report generated
- ✅ Sprint 0 Checklist created
- ✅ Agent Collaboration Guide created (this document)

**What happens next:**
1. **You decide:** Full Sprint 0 now, minimal Sprint 0, or review first?
2. **Sprint 0 execution:** You + agents collaborate (3-3.5 days)
3. **Epic 6 decision:** Defer to Phase 2 (recommended) or include in MVP?
4. **Sprint Planning:** Chat with Bob (SM agent) after Sprint 0 complete
5. **Start coding:** Epic 1 implementation begins!

---

## Important Reminders

**Agents CANNOT:**
- ❌ Run commands on your actual machine
- ❌ Install software (Nix, Docker, etc.) on your system
- ❌ Click GitHub UI buttons for branch protection
- ❌ Test on real hardware (Windows, macOS, Linux verification)

**Agents CAN:**
- ✅ Generate all configuration files
- ✅ Write all documentation
- ✅ Create all test code
- ✅ Debug errors (given logs/output)
- ✅ Review and improve your work
- ✅ Explain concepts and best practices

**You MUST:**
- ✅ Execute commands on real machines
- ✅ Verify platform compatibility
- ✅ Run Docker and test mock servers
- ✅ Configure GitHub repository settings
- ✅ Confirm all checklists pass

---

## Final Note

**Sprint 0 is NOT coding features** - it's infrastructure setup. This investment pays off immediately:
- Epic 1-5 implementation goes smoothly
- No "works on my machine" issues
- Automated quality gates prevent bad code
- TDD workflow enforces best practices

**With agent help, Sprint 0 is much easier:**
- Agents write configs, tests, documentation
- You verify on real hardware
- Agents debug issues
- You confirm everything works

**Ready to start?** Just say which option you prefer (A, B, or C), and we'll begin!

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-26  
**Related Documents:**
- `docs/sprint-artifacts/sprint-0-checklist.md` (detailed task checklist)
- `docs/implementation-readiness-report-20251126.md` (readiness assessment)
- `docs/bmm-workflow-status.yaml` (project phase tracking)
