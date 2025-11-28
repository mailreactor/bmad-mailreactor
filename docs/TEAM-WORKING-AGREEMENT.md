# Team Working Agreement - Mail Reactor

**Last Updated:** 2025-11-28  
**Project:** Mail Reactor MVP  
**Sprint:** Sprint 1

---

## 🚨 CRITICAL CONSTRAINTS - READ FIRST

### Git Operations
- **NO GIT COMMITS** - HC handles ALL git operations
- **NO GIT REVERTS** - HC handles version control
- **NO DESTRUCTIVE OPS** - No force pushes, no deletions
- **READ OPERATIONS ONLY** - You can read code, but HC commits

### Why?
HC manages the git workflow to maintain clean history and proper commit messages.

---

## 📂 Directory Structure

### Project Root: `/home/hcvst/dev/bmad/bmad-mailreactor/`

```
bmad-mailreactor/
├── docs/                          # 📋 TEAM/PROCESS DOCUMENTATION
│   ├── sprint-artifacts/          # Sprint planning, stories, retros
│   ├── prd.md                     # Product requirements
│   ├── architecture.md            # System architecture  
│   ├── epics.md                   # Epic breakdown
│   ├── tdd-guide.md              # TDD practices
│   └── TEAM-WORKING-AGREEMENT.md  # ← You are here
│
└── mailreactor/                   # 🐍 PYTHON PACKAGE (PRODUCT CODE)
    ├── src/mailreactor/           # Source code (write here)
    ├── tests/                     # Test suites (write here)
    ├── .venv/                     # Python virtual environment (USE THIS)
    ├── pyproject.toml            # Package configuration
    ├── docs/                      # 📚 END-USER DOCUMENTATION
    │   └── (API guides, tutorials for Mail Reactor users)
    └── README.md                  # Product readme for users
```

### Three Documentation Layers

| Location | Purpose | Audience | Examples |
|----------|---------|----------|----------|
| `./docs/` | Team process, sprint planning | Internal team (us) | PRD, Architecture, Sprint status, TDD guide |
| `./mailreactor/` | Product code & tests | Developers (implementation) | Python code, pytest tests |
| `./mailreactor/docs/` | End-user documentation | Mail Reactor users | API docs, Installation guide, Tutorials |

---

## 🐍 Python Development

### Working Directory
```bash
cd /home/hcvst/dev/bmad/bmad-mailreactor/mailreactor
```

### Virtual Environment
**ALWAYS use the venv in mailreactor directory:**
```bash
source .venv/bin/activate
```

### Running Tests
```bash
cd /home/hcvst/dev/bmad/bmad-mailreactor/mailreactor
source .venv/bin/activate
pytest tests/
```

### Running the Application
```bash
cd /home/hcvst/dev/bmad/bmad-mailreactor/mailreactor
source .venv/bin/activate
python -m mailreactor dev
```

---

## 📝 Sprint Artifacts

### Location
All sprint artifacts live in: `./docs/sprint-artifacts/`

### Files
- **`sprint-status.yaml`** - Current sprint progress tracker
- **`{story-id}.md`** - Story drafts (e.g., `1-1-project-structure.md`)
- **`{story-id}-context.md`** - Story context for dev (e.g., `1-1-project-structure-context.md`)
- **Sprint 0 artifacts** - Setup checklists, spike reports

---

## 👥 Agent Roles & Responsibilities

### Scrum Master (Bob) - @sm
- Sprint planning & tracking
- Story drafting (in `./docs/sprint-artifacts/`)
- Code reviews
- Retrospectives
- **Does NOT write product code**

### Developer (Winston) - @dev
- Implementation (in `./mailreactor/src/`)
- TDD (tests first in `./mailreactor/tests/`)
- Story implementation
- Code in Python working directory
- **Does NOT commit to git**

### Test Engineer (Alice) - @tea
- Test architecture
- Test design & review
- CI/CD configuration
- Quality gates
- Works in `./mailreactor/tests/`

### Tech Writer (Sage) - @tech-writer
- END-USER documentation (in `./mailreactor/docs/`)
- API documentation
- Installation guides
- Tutorials for Mail Reactor users
- **Not team process docs** (that's in `./docs/`)

---

## 🔄 Workflow Pattern

### Story Lifecycle

1. **SM drafts story** → `./docs/sprint-artifacts/{story-id}.md`
2. **SM creates context** → `./docs/sprint-artifacts/{story-id}-context.md`
3. **Dev implements** → Code in `./mailreactor/src/`, tests in `./mailreactor/tests/`
4. **Dev signals review** → Updates story status to `review` in sprint-status.yaml
5. **SM reviews** → Code review workflow
6. **HC commits** → Git operations
7. **SM marks done** → Updates story status to `done`

### Sprint Status Updates

**File:** `./docs/sprint-artifacts/sprint-status.yaml`

**How to update:**
- Agents use Edit tool to change status values
- SM maintains the file
- Statuses: `backlog` → `drafted` → `ready-for-dev` → `in-progress` → `review` → `done`

---

## 🧪 Test-Driven Development (TDD)

### Sprint 0 Setup Complete ✅
- Test structure: `unit/`, `integration/`, `e2e/`, `performance/`, `security/`
- Mock SMTP/IMAP: Greenmail via Docker Compose
- Pre-commit hooks: Configured
- CI/CD: GitHub Actions ready

### TDD Workflow
1. **Write test first** (in `./mailreactor/tests/`)
2. **Run test** (it fails - red)
3. **Write minimal code** (in `./mailreactor/src/`)
4. **Run test** (it passes - green)
5. **Refactor** (improve code quality)
6. **Repeat**

### Test Guidelines
- See `./docs/tdd-guide.md` for complete practices
- Use fixtures from `./mailreactor/tests/conftest.py`
- Follow test templates in `./docs/testing/templates/`

---

## 🚀 Sprint 1 Status

### Current Sprint: Sprint 1
**Goal:** Complete Epic 1 - Foundation & Zero-Config Deployment

**Stories (8 total):**
1. ✅ Story 1.1: Project Structure and Build Configuration
2. ⏳ Story 1.2: FastAPI Application Initialization
3. ⏳ Story 1.3: Structured Logging
4. ⏳ Story 1.4: CLI Framework with Start Command
5. ⏳ Story 1.5: Health Check Endpoint
6. ⏳ Story 1.6: OpenAPI Documentation
7. ⏳ Story 1.7: Response Envelope & Error Handling
8. ⏳ Story 1.8: Development Mode

**Sprint Duration:** TBD (typically 1-2 weeks)

---

## 📚 Key Reference Documents

| Document | Location | Purpose |
|----------|----------|---------|
| PRD | `./docs/prd.md` | Product requirements |
| Architecture | `./docs/architecture.md` | System design decisions |
| Epics | `./docs/epics.md` | Story breakdown |
| TDD Guide | `./docs/tdd-guide.md` | Testing practices |
| Sprint Status | `./docs/sprint-artifacts/sprint-status.yaml` | Current progress |
| This Guide | `./docs/TEAM-WORKING-AGREEMENT.md` | Team constraints & workflow |

---

## ❓ Common Questions

**Q: Where do I write Python code?**  
A: `./mailreactor/src/mailreactor/`

**Q: Where do I write tests?**  
A: `./mailreactor/tests/`

**Q: Which venv do I use?**  
A: `./mailreactor/.venv`

**Q: Where do I write user documentation?**  
A: `./mailreactor/docs/` (for end users)

**Q: Where do I write sprint artifacts?**  
A: `./docs/sprint-artifacts/` (for team)

**Q: Can I commit to git?**  
A: **NO** - Only HC commits

**Q: Where is the PRD/Architecture?**  
A: `./docs/` (team documentation)

**Q: Where do I run pytest?**  
A: From `./mailreactor/` directory with `.venv` activated

---

## 🎯 Quick Start Checklist

When starting work as an agent:

1. ✅ Read this file first
2. ✅ Understand git constraints (NO COMMITS)
3. ✅ Know your working directory (`./mailreactor` for code, `./docs` for sprint)
4. ✅ Use the correct venv (`.venv` in mailreactor)
5. ✅ Check sprint status (`./docs/sprint-artifacts/sprint-status.yaml`)
6. ✅ Read relevant story context (in `./docs/sprint-artifacts/`)
7. ✅ Follow TDD practices (`./docs/tdd-guide.md`)

---

**Questions?** Ask HC or Bob (Scrum Master)

**Last Updated by:** Bob (Scrum Master)  
**Next Review:** After Sprint 1
