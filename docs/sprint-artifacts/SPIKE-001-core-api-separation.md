# SPIKE-001: Validate Core/API Separation for Dual-Mode Usage

**Type:** Spike  
**Sprint:** Sprint 1 Prep  
**Priority:** High (Blocks Sprint 1 implementation)  
**Created:** 2025-11-28  
**Owner:** Winston (Architect)  
**Time-box:** 6 hours

---

## Goal

Prove that `mailreactor.core` can be used as both a standalone Python library AND as the foundation for FastAPI endpoints, validating architectural assumptions before Sprint 1 implementation.

---

## Context

During Sprint 0 planning discussion, the team identified that Mail Reactor should support two usage modes:

1. **API Mode:** FastAPI server exposing HTTP endpoints (original design)
2. **Library Mode:** Direct Python import for embedded use cases (new requirement)

This spike validates that the existing architecture (core/ separate from api/) truly supports both modes without coupling to FastAPI.

**Key architectural constraint:** We use IMAPClient (BSD-3, synchronous) wrapped with `asyncio.run_in_executor()` because native async IMAP libraries are GPL-3.0 (copyleft incompatible with MIT license goal). This spike must confirm the executor pattern works in library mode without FastAPI.

---

## Acceptance Criteria

### Core Separation Validation

- [ ] **AC-1:** Create prototype that imports `AsyncIMAPClient` and `AsyncSMTPClient` from `mailreactor.core` without importing any FastAPI code
- [ ] **AC-2:** Send test email using core library directly (no HTTP server running)
- [ ] **AC-3:** Retrieve emails using core library directly with IMAP search
- [ ] **AC-4:** Run dependency analyzer (`pipdeptree` or `import-linter`) - confirm `core/` module has zero FastAPI dependencies
- [ ] **AC-5:** Verify asyncio executor pattern works with user-provided event loop (not FastAPI's event loop)

### Event System Prototype

- [ ] **AC-6:** Implement basic `EventEmitter` class with async handler registration
- [ ] **AC-7:** Prototype callback registration API: `@client.on_message_received` decorator pattern
- [ ] **AC-8:** Verify async handler execution doesn't block IMAP polling loop
- [ ] **AC-9:** Test event emission from executor thread to async handlers
- [ ] **AC-10:** Measure thread pool usage under concurrent IMAP operations (establish baseline metrics)

### Documentation Inputs

- [ ] **AC-11:** Document import patterns for library mode usage with code examples
- [ ] **AC-12:** Document async monitoring loop patterns (`asyncio.create_task`, `asyncio.gather`)
- [ ] **AC-13:** Capture example code demonstrating both library mode AND API mode using same core
- [ ] **AC-14:** Identify any coupling issues requiring architectural adjustments

### Package Structure Validation

- [ ] **AC-15:** Draft `pyproject.toml` with core dependencies separate from `[api]` optional dependencies
- [ ] **AC-16:** Confirm installation pattern: `pip install mailreactor` → library mode (no FastAPI installed)
- [ ] **AC-17:** Confirm installation pattern: `pip install mailreactor[api]` → full API mode (includes FastAPI)

---

## Output Deliverables

1. **Go/No-Go Decision:** Can we proceed with dual-mode architecture for Sprint 1?
2. **Event Emitter Prototype Code:** Working implementation for team review
3. **Architectural Adjustments List:** Any issues discovered that need fixes (if any)
4. **Example Code Snippets:** For documentation team (Paige)
5. **Dependency Validation Report:** Proof that core has no FastAPI coupling

---

## Definition of Done

- [ ] Architect (Winston) approves separation is production-ready
- [ ] Test Architect (Murat) approves async execution model and thread pool behavior
- [ ] Technical Writer (Paige) has sufficient example code for documentation
- [ ] Product Manager (John) confirms both usage modes are viable for target users
- [ ] All acceptance criteria passing OR concrete action items identified to fix issues

---

## Technical Notes

### Asyncio Executor Pattern

```python
# Expected pattern in core/imap_client.py
from imapclient import IMAPClient  # BSD-3, sync
import asyncio  # stdlib
from functools import partial  # stdlib

class AsyncIMAPClient:
    async def _run_sync(self, func, *args, **kwargs):
        """Execute sync IMAPClient method in thread pool executor"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            partial(func, *args, **kwargs)
        )
```

### Event Emitter Design

```python
# Expected pattern in core/events.py
from typing import Callable, Awaitable

class EventEmitter:
    """Transport-agnostic event dispatch"""
    def __init__(self):
        self._handlers = []
    
    def subscribe(self, handler: Callable[[Event], Awaitable]):
        self._handlers.append(handler)
    
    async def emit(self, event: Event):
        await asyncio.gather(*[h(event) for h in self._handlers])
```

### Library Mode Usage Example

```python
# User's code - no FastAPI
import asyncio
from mailreactor.core import AsyncIMAPClient

async def main():
    client = AsyncIMAPClient(
        host="imap.gmail.com",
        port=993,
        use_ssl=True
    )
    
    @client.on_message_received
    async def handle_email(event):
        print(f"New email: {event.message.subject}")
    
    await client.start_monitoring(poll_interval=60)

asyncio.run(main())
```

### API Mode Usage Example

```python
# api/messages.py - FastAPI endpoint
from fastapi import APIRouter
from ..core.imap_client import AsyncIMAPClient

router = APIRouter()

@router.get("/messages")
async def list_messages():
    client = AsyncIMAPClient(...)  # Same core code
    messages = await client.list_messages()
    return {"messages": messages}
```

---

## Success Metrics

**Primary:** All 17 acceptance criteria pass without architectural changes needed.

**Secondary:** Event emitter prototype is clean enough to use directly in Sprint 1 implementation.

**Risk Indicator:** If more than 2 ACs fail, we may need to reconsider dual-mode architecture or adjust timeline.

---

## Related Requirements

- **FR-099:** System supports direct Python library import without FastAPI dependency
- **FR-100:** Users can register async event handlers for real-time email notifications (library mode)
- **FR-101:** Users can register webhook URLs for HTTP POST delivery (API mode)
- **FR-102:** System implements transport-agnostic event emitter for message received events

---

## Follow-up Actions (If Spike Succeeds)

1. Update PRD with FR-099 through FR-102
2. Create ADR-007: Event-Driven Architecture for Real-Time Notifications
3. Create documentation structure for dual-mode usage
4. Plan Sprint 1 stories for core library + event system implementation

---

## Notes from Party Mode Discussion (2025-11-28)

**Team consensus:**
- Winston: Architecture already supports separation, executor pattern is FastAPI-agnostic
- Amelia: Dependency tree enforces clean separation, zero coupling detected
- Murat: Event-driven design testable, async handler execution needs validation
- John: Dual-mode expands addressable market (embedded use + API service)
- Mary: Competitive advantage vs EmailEngine (API only) and IMAPClient (library only)
- Paige: Documentation structure clear, needs example code from spike
- Sally: Two distinct user journeys both feel natural

**Key decision:** Event emitter is transport-agnostic. Webhooks (HTTP POST) and callbacks (Python async functions) are different consumers of same event pipeline.

---

**Status:** Ready for execution  
**Next:** Winston to execute spike and report findings
