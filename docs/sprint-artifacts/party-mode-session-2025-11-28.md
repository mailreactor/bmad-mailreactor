# Party Mode Planning Session - Sprint 0 to Sprint 1 Transition

**Date:** 2025-11-28  
**Participants:** All BMAD agents (9 agents)  
**Facilitator:** Bob (Scrum Master)  
**Topic:** Dual-mode architecture planning and Sprint 1 preparation

---

## Session Overview

HC initiated party mode discussion to validate architectural decisions before Sprint 1 kickoff. Three main topics discussed:

1. **Library vs API usage modes** - Can Mail Reactor be used as both?
2. **Webhooks and callbacks** - How do real-time email events work in each mode?
3. **Async executor pattern** - Does GPL avoidance strategy conflict with library mode?

---

## Key Decisions

### 1. Dual-Mode Architecture Approved

**Decision:** Mail Reactor will support TWO usage modes from Sprint 1:

- **API Mode:** FastAPI HTTP server (original design)
- **Library Mode:** Direct Python import for embedded use cases (new)

**Rationale:**
- Architecture already supports clean separation (core/ vs api/)
- Expands addressable market: embedded apps, batch processing, prototyping
- Competitive advantage vs EmailEngine (API only) and IMAPClient (library only)
- Minimal implementation cost - architecture already designed correctly

**Installation patterns:**
```bash
# Library mode
pip install mailreactor
# → Core only, no FastAPI dependency

# API mode  
pip install mailreactor[api]
# → Includes FastAPI, Uvicorn
```

---

### 2. Event-Driven Architecture for Real-Time Notifications

**Decision:** Implement transport-agnostic event emitter in core layer.

**Pattern:**
```python
# Core event system (no HTTP knowledge)
class EventEmitter:
    async def emit(event: EmailEvent)
    def subscribe(handler: Callable)

# Library mode - register callbacks
@client.on_message_received
async def my_handler(event):
    print(event.message.subject)

# API mode - webhooks are just HTTP POST handlers
@emitter.subscribe
async def webhook_forwarder(event):
    await http_client.post(webhook_url, json=event.dict())
```

**Benefits:**
- Library users get clean async callback API
- API users get webhooks (HTTP POST to registered URLs)
- Same event pipeline, different transports
- Testable, decoupled design

**Terminology:**
- **Library mode:** "Event handlers" or "callbacks"
- **API mode:** "Webhooks"
- Both deliver real-time email notifications, different mechanisms

---

### 3. Asyncio Executor Pattern Validated

**Decision:** IMAPClient (BSD-3, sync) + `asyncio.run_in_executor()` pattern is correct and works in both modes.

**Key insight:** The executor pattern depends on **asyncio (stdlib)**, NOT FastAPI. Library mode users provide their own event loop:

```python
# Library mode - user's event loop
import asyncio
from mailreactor.core import AsyncIMAPClient

async def main():
    client = AsyncIMAPClient(...)  # Uses executor internally
    await client.start_monitoring()

asyncio.run(main())  # User's event loop, not FastAPI's
```

**License compliance preserved:**
- ✅ IMAPClient: BSD-3 (MIT-compatible)
- ✅ asyncio: Python stdlib
- ❌ aioimaplib: GPL-3.0 (avoided)

**Performance trade-off accepted:**
- Executor overhead: ~50-100ms per operation
- Network latency: 200-2000ms (IMAP/SMTP)
- Overhead negligible compared to I/O

---

## Requirements Updates

### New Functional Requirements

**FR-099: Direct Python Library Import Support**
> System supports direct Python import of core modules without FastAPI dependency, enabling embedded usage in user applications.

**FR-100: Event Handler Registration (Library Mode)**
> Users can register async callback functions for real-time email notifications using decorator pattern when using mailreactor as a library.

**FR-101: Webhook HTTP POST Delivery (API Mode)**
> Users can register webhook URLs via REST API to receive HTTP POST notifications when new emails arrive matching configured filters.

**FR-102: Transport-Agnostic Event Emitter**
> System implements core event emitter that dispatches email events to registered handlers without knowledge of transport mechanism (callbacks vs webhooks).

---

## Action Items

### SPIKE-001: Core/API Separation Validation

**Owner:** Winston (Architect)  
**Time-box:** 6 hours  
**Status:** Ready for execution

**Scope:**
- Validate core imports work without FastAPI
- Prototype event emitter with callback registration
- Test executor pattern with user event loop
- Measure thread pool usage baseline
- Document async patterns for library users

**Deliverables:**
- Go/No-Go decision on dual-mode architecture
- Event emitter prototype code
- Example code for documentation
- Dependency validation report

---

### Documentation Planning

**Owner:** Paige (Technical Writer)  
**Status:** Blocked on SPIKE-001 (needs example code)

**Structure:**
```
docs/
├── usage-modes.md (API vs Library comparison)
├── guides/
│   ├── library-mode-quickstart.md
│   ├── api-mode-quickstart.md
│   ├── real-time-events.md (webhooks + callbacks)
│   └── async-patterns.md (event loops, monitors)
```

---

### PRD Updates

**Owner:** Mary (Business Analyst) + John (Product Manager)  
**Status:** In progress

**Changes:**
- Add FR-099 through FR-102
- Update product scope section to explicitly mention dual-mode support
- Add library mode installation instructions
- Update competitive positioning with dual-mode advantage

---

### Architecture Decision Record

**Owner:** Winston (Architect)  
**Status:** Queued (after SPIKE-001)

**ADR-007: Event-Driven Architecture for Real-Time Notifications**
- Decision: Transport-agnostic event emitter
- Rationale: Support both library callbacks and API webhooks
- Consequences: Unified event pipeline, different consumers
- Alternatives considered: Separate implementations per mode

---

## Team Consensus Points

### From Winston (Architect):
- Architecture already enforces clean separation (core/ has no FastAPI imports)
- Dependency flow: api/ → core/, never reverse
- Event emitter pattern is industry standard (observer pattern)
- Executor pattern works identically in both modes

### From Amelia (Developer):
- `pyproject.toml` structure enforces separation via optional dependencies
- Core modules importable standalone: `from mailreactor.core import AsyncIMAPClient`
- Zero coupling detected in current architecture

### From Murat (Test Architect):
- Event-driven design improves testability (mock handlers, verify emissions)
- Need circuit breaker for handler errors (prevent crash loops)
- Thread pool usage needs baseline metrics
- Async-only handlers for MVP (sync via executor in Phase 2)

### From John (Product Manager):
- Three user segments: embedded apps, batch processing, prototyping
- Library mode lowers adoption friction (no deployment needed)
- Dual-mode positioning: "Easiest email API AND best Python email library"

### From Mary (Business Analyst):
- Competitive gap: EmailEngine is API-only, IMAPClient is library-only
- Mail Reactor uniquely serves both use cases
- PRD needs explicit dual-mode documentation

### From Paige (Technical Writer):
- Two clear entry points in documentation
- Code example parity across modes (show both ways)
- Terminology clarity: webhooks (API) vs callbacks (library)

### From Sally (UX Designer):
- Two distinct developer journeys both feel natural
- API mode: language-agnostic, containerizable
- Library mode: no HTTP overhead, pure Python

### From Bob (Scrum Master):
- Spike needed to validate assumptions before Sprint 1
- Dual-mode scope adds ~3 story points to Sprint 1
- PRD updates required before planning

---

## Risks Identified

### Technical Risks

**Risk:** Event handlers crash and break monitor loop  
**Mitigation:** Circuit breaker pattern, error handling, handler timeouts

**Risk:** Thread pool exhaustion with multiple accounts  
**Mitigation:** Configurable executor, document best practices

**Risk:** User confusion about event loop management  
**Mitigation:** Documentation with clear examples, auto-start with warnings

### Scope Risks

**Risk:** Dual-mode increases testing surface  
**Mitigation:** Test both modes, but core logic shared (DRY principle)

**Risk:** Documentation effort doubles  
**Mitigation:** Unified concepts, mode-specific examples side-by-side

### Market Risks

**Risk:** Users don't discover both modes exist  
**Mitigation:** PyPI description, README hero section, clear positioning

---

## Sprint 1 Readiness Checklist

- [ ] SPIKE-001 executed and Go decision reached
- [ ] PRD updated with FR-099 through FR-102
- [ ] Event emitter prototype reviewed and approved
- [ ] Documentation structure planned
- [ ] Package dependency structure validated
- [ ] Sprint 1 stories estimated with dual-mode scope

**Blocked on:** SPIKE-001 completion

---

## Next Steps

1. **Winston:** Execute SPIKE-001 (6 hours)
2. **Mary + John:** Update PRD with new FRs
3. **Paige:** Draft documentation structure (parallel with spike)
4. **Bob:** Sprint 1 planning session once spike completes
5. **Team:** Review spike findings and adjust plan if needed

---

## Session Outcome

✅ **Consensus reached:** Dual-mode architecture is desirable and architecturally sound  
✅ **Event system designed:** Transport-agnostic emitter with callbacks + webhooks  
✅ **License compliance confirmed:** Executor pattern doesn't require FastAPI  
✅ **Sprint 1 prep:** SPIKE-001 defined and ready for execution

**Team alignment:** 9/9 agents approve dual-mode approach

**HC decision:** Finalize and commit planning artifacts

---

**Session Duration:** ~45 minutes  
**Status:** Complete  
**Artifacts Created:** SPIKE-001.md, session notes, PRD update requirements
