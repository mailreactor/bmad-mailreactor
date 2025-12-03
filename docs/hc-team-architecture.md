# Team Working Agreement - Mail Reactor

## 🚨 CRITICAL CONSTRAINTS - READ FIRST AND ALWAYS ACKNOWLEDGE UNDERSTANDING WITH 🧠🧠🧠

### Project Root: `/home/hcvst/dev/bmad/bmad-mailreactor/`
The project root houses the project docs and tasks.

### Python Project Root: `/home/hcvst/dev/bmad/bmad-mailreactor/mailreactor`
The Python projec`t root contains our deliverable that we ship. Code, contributer docs and end-user docs.

### Python Tests: `/home/hcvst/dev/bmad/bmad-mailreactor/mailreactor/tests`

### Two Documentation Layers
As a consequence of the above we have two doc locations:

| Location | Purpose | Audience | Examples |
|----------|---------|----------|----------|
| `./docs/` | Team process, sprint planning | Internal team (us) | PRD, Architecture, Sprint status, TDD guide |
| `./mailreactor/docs/` | End-user documentation | Mail Reactor users | API docs, Installation guide, Tutorials |


### How to run commands
`cd mailreactor && .venv/bin/python`
`cd mailreactor && .venv/bin/pytest`

If a command does not work ASK for help. Do not try and explore alternatives.

### 3rd party library
Consult the docs of all 3rd party libraries to ensure code is minimal and focused. Do not reinvent the wheel
and use libraries canonically.

### Focused sharp code
Keep code and comments focused and sharp, easy to understand and minimal.

### Testing Principle:

• ✅ ONLY test functionality WE have added
• ❌ DO NOT test Python machinery
• ❌ DO NOT test 3rd party library functionality
• ❌ DO NOT test framework behavior

Examples:

• ✅ Test: Our business logic, our domain rules, our API endpoints
• ❌ Don't test: FastAPI routing works, Pydantic validates, logging library logs
• ✅ Test: Our email parsing logic
• ❌ Don't test: That email.parser.Parser actually parses emails

Keep tests focused and minimal - only verify the value we're adding to the codebase, not that Python or our dependencies work correctly.

### Git Operations
- **NO GIT COMMITS** - HC handles ALL git operations
- **NO GIT REVERTS** - HC handles version control
- **NO DESTRUCTIVE OPS** - No force pushes, no deletions
- **READ OPERATIONS ONLY** - You can read code, but HC commits

### 📂 Directory Structure


```
bmad-mailreactor/
├── docs/                          # 📋 TEAM/PROCESS DOCUMENTATION
│   ├── sprint-artifacts/          # Sprint planning, stories, retros
│   ├── prd.md                     # Product requirements
│   ├── architecture.md            # System architecture  
│   ├── epics.md                   # Epic breakdown
│   ├── tdd-guide.md              # TDD practices
│   └── ...
│
└── mailreactor/                   # 🐍 PYTHON PACKAGE (PRODUCT CODE)
    ├── src/mailreactor/           # Source code (write here)
    ├── tests/                     # Test suites (write here)
    ├── .venv/                     # Python virtual environment (USE THIS)
    ├── pyproject.toml            # Package configuration
    ├── docs/                      # 📚 END-USER DOCUMENTATION
    │   └── (API guides, tutorials for Mail Reactor users)
    └── ...
```

ACKNOWLEDGE WITH THREE BRAINS 🧠🧠🧠
