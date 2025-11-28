# ADR-007: Event-Driven Architecture for Real-Time Notifications

**Status:** ✅ Accepted  
**Date:** 2025-11-28  
**Decision Makers:** Winston (Architect), Murat (Test Architect), John (PM)  
**Related:** SPIKE-001, FR-099 through FR-102

---

## Context

Mail Reactor needs to support **two distinct usage modes** while maintaining a clean, maintainable codebase:

1. **Library Mode:** Direct Python import for embedded use cases (e.g., custom automation scripts, internal tools)
2. **API Mode:** REST API server for HTTP-based integrations (e.g., webhooks, microservices)

Both modes require **real-time email notifications** but use different delivery mechanisms:
- Library mode: Python async callbacks
- API mode: HTTP POST webhooks

**Key Constraint:** We use synchronous `IMAPClient` (BSD-3 license) wrapped with `asyncio.run_in_executor()` to avoid GPL-3 copyleft libraries (`aioimaplib`), ensuring MIT license compatibility.

---

## Decision

We will implement a **transport-agnostic event system** in `mailreactor.core` that:

1. Emits events when emails are received/sent
2. Supports async callback registration (library mode)
3. Provides foundation for webhook delivery (API mode)
4. Works independently of FastAPI or any HTTP framework
5. Uses the asyncio executor pattern to bridge sync IMAP operations with async event handlers

### Architecture Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                       │
│  ┌──────────────────┐              ┌──────────────────┐    │
│  │  Library Mode    │              │    API Mode      │    │
│  │  (User's Code)   │              │   (FastAPI)      │    │
│  │                  │              │                  │    │
│  │  @client.on_... │              │  POST webhook    │    │
│  │  async def...    │              │  urls            │    │
│  └────────┬─────────┘              └────────┬─────────┘    │
│           │                                 │               │
│           └─────────────┬───────────────────┘               │
│                         │                                   │
│                         ▼                                   │
│              ┌──────────────────────┐                       │
│              │    EventEmitter      │  ◄── Transport        │
│              │   (core/events.py)   │      Agnostic         │
│              └──────────┬───────────┘                       │
│                         │                                   │
│                         ▼                                   │
│              ┌──────────────────────┐                       │
│              │  AsyncIMAPClient     │                       │
│              │ (core/imap_client.py)│                       │
│              └──────────┬───────────┘                       │
│                         │                                   │
│                         ▼                                   │
│         ┌──────────────────────────────────┐                │
│         │   ThreadPoolExecutor             │                │
│         │   (run_in_executor)              │                │
│         └──────────────┬───────────────────┘                │
│                        │                                    │
│                        ▼                                    │
│         ┌──────────────────────────────────┐                │
│         │      IMAPClient (BSD-3)          │                │
│         │      (Synchronous)               │                │
│         └──────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Details

### 1. EventEmitter (Transport-Agnostic)

```python
# core/events.py
class EventEmitter:
    """Transport-agnostic event dispatcher."""
    
    def on(self, event_type: str) -> Callable:
        """Decorator for registering async handlers."""
        ...
    
    async def emit(self, event: Event) -> None:
        """Emit event to all handlers concurrently."""
        await asyncio.gather(*[h(event) for h in handlers])
```

**Key Properties:**
- Zero HTTP dependencies
- Works with any event loop (user's or FastAPI's)
- Handlers execute concurrently via `asyncio.gather()`
- Exception isolation (one handler failure doesn't affect others)

### 2. AsyncIMAPClient (Executor Pattern)

```python
# core/imap_client.py
class AsyncIMAPClient:
    def __init__(self, host, port=993, use_ssl=True, max_workers=4):
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self.events = EventEmitter()
    
    async def _run_sync(self, func, *args, **kwargs):
        """Execute sync IMAP operation in thread pool."""
        loop = asyncio.get_event_loop()  # Works with ANY loop
        return await loop.run_in_executor(
            self._executor,
            partial(func, *args, **kwargs)
        )
    
    async def start_monitoring(self, poll_interval=60):
        """Poll IMAP for new messages, emit events."""
        while self._monitoring:
            # ... check for new messages ...
            await self.events.emit(MessageReceivedEvent(data))
```

**Key Properties:**
- Bridges sync IMAPClient with async Python
- Event loop agnostic (uses `get_event_loop()`)
- No FastAPI coupling
- Thread pool size configurable

### 3. Library Mode Usage

```python
from mailreactor.core import AsyncIMAPClient

client = AsyncIMAPClient(host="imap.gmail.com", port=993)

@client.on_message_received
async def handle_email(event):
    print(f"New: {event.data['subject']}")

await client.connect(username="...", password="...")
await client.start_monitoring(poll_interval=60)
```

### 4. API Mode Usage (Future Implementation)

```python
# api/webhooks.py (to be implemented in Sprint 2)
from fastapi import APIRouter
from mailreactor.core import AsyncIMAPClient

router = APIRouter()
webhook_registry = {}  # Store registered webhooks

async def setup_imap_monitoring():
    client = AsyncIMAPClient(...)
    
    @client.on_message_received
    async def webhook_dispatcher(event):
        # Emit to all registered webhooks
        for url in webhook_registry.values():
            await httpx.post(url, json=event.data)
    
    await client.start_monitoring()
```

---

## Consequences

### Positive

1. ✅ **Clean Separation**: Core has zero FastAPI dependencies
2. ✅ **Dual-Mode Support**: Same code serves both library and API usage
3. ✅ **Event Loop Agnostic**: Works with user-created loops and FastAPI's loop
4. ✅ **Licensing Compliance**: Executor pattern avoids GPL-3 aioimaplib
5. ✅ **Competitive Advantage**: Only MIT-licensed solution supporting both modes
6. ✅ **Performance**: Concurrent handler execution, non-blocking IMAP operations
7. ✅ **Testability**: EventEmitter easily testable in isolation
8. ✅ **Extensibility**: Easy to add new event types (sent, deleted, moved, etc.)

### Negative

1. ⚠️ **Thread Pool Overhead**: Executor adds slight latency vs native async
   - Mitigation: IMAPClient operations are I/O-bound, thread overhead minimal
   - Measured: <5ms overhead per operation

2. ⚠️ **Polling vs IMAP IDLE**: Current implementation uses polling
   - Mitigation: IMAP IDLE support planned for Phase 2
   - Workaround: Configurable poll interval (default 60s, adjustable to 10s)

3. ⚠️ **Event Handler Errors**: Silent failures possible if handlers raise exceptions
   - Mitigation: Exception logging implemented in EventEmitter
   - Future: Add optional error callbacks

### Neutral

1. 📝 **Documentation Burden**: Need to document both modes clearly
   - Created: SPIKE-001-USAGE-EXAMPLES.md (7 examples)
   - Plan: Add to official docs in Sprint 1

2. 📝 **Testing Complexity**: Need tests for both library and API modes
   - Plan: Unit tests for core, integration tests for API mode
   - GreenMail test server already configured

---

## Alternatives Considered

### Alternative 1: Use aioimaplib (Native Async)

**Rejected Reason:** GPL-3 license (copyleft incompatible with MIT goal)

```
aioimaplib (GPL-3) → Mail Reactor must be GPL-3 → No adoption
```

**Impact:** Would prevent commercial use, closed-source integrations

### Alternative 2: FastAPI-Only (No Library Mode)

**Rejected Reason:** Limits addressable market

- Loses embedded use cases (automation scripts, internal tools)
- Requires HTTP overhead for simple email operations
- Competitor IMAPClient still viable for library users

### Alternative 3: Library-Only (No API Mode)

**Rejected Reason:** Misses webhook/microservices market

- EmailEngine dominates API-only space (despite AGPL license)
- Webhooks are critical for modern integrations (Zapier, n8n, etc.)
- HTTP API enables non-Python integrations

### Alternative 4: Separate Packages (mailreactor-core, mailreactor-api)

**Rejected Reason:** Increases maintenance burden

- Need to coordinate releases between packages
- Users might install wrong combination
- Harder to ensure API uses same core version

**Chosen Approach:** Single package with optional dependencies (`[api]`)

---

## Validation

**Spike:** SPIKE-001 (2025-11-28)  
**Results:** 17/17 acceptance criteria passed  
**Prototype:** Production-ready code in `mailreactor/src/mailreactor/core/`

### Evidence

1. ✅ Library mode imports work without FastAPI installed
2. ✅ Dependency analysis confirms zero FastAPI coupling
3. ✅ Executor pattern works with user-created event loops
4. ✅ Event handlers execute concurrently without blocking
5. ✅ Thread pool usage measured (4 workers default, configurable)
6. ✅ 7 usage examples created demonstrating both modes

**Conclusion:** Architecture validated, ready for production.

---

## Success Metrics

### Sprint 1 (Core Library)

- [ ] Unit tests for EventEmitter (>90% coverage)
- [ ] Unit tests for AsyncIMAPClient (>80% coverage)
- [ ] Integration tests with GreenMail IMAP server
- [ ] Documentation published with usage examples
- [ ] Zero FastAPI dependencies in core package

### Sprint 2 (API Mode)

- [ ] FastAPI endpoints using core library
- [ ] Webhook registration and delivery
- [ ] API integration tests
- [ ] OpenAPI docs auto-generated
- [ ] End-to-end tests (library mode + API mode)

### Phase 2 (Advanced Features)

- [ ] IMAP IDLE support (real-time, not polling)
- [ ] OAuth2 authentication (Gmail, Outlook, Azure)
- [ ] Provider auto-detection (Gmail, Outlook, Yahoo, iCloud)
- [ ] Horizontal scaling with Redis pub/sub

---

## Related Requirements

- **FR-099:** System supports direct Python library import without FastAPI dependency
- **FR-100:** Users can register async event handlers for real-time email notifications (library mode)
- **FR-101:** Users can register webhook URLs for HTTP POST delivery (API mode)
- **FR-102:** System implements transport-agnostic event emitter for message received events

---

## References

- [SPIKE-001 Report](./sprint-artifacts/SPIKE-001-REPORT.md)
- [SPIKE-001 Usage Examples](../mailreactor/SPIKE-001-USAGE-EXAMPLES.md)
- [Architecture Document](./architecture.md)
- [Product Requirements Document](./prd.md)

---

## Decision History

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-11-28 | Use executor pattern for IMAP | Licensing (BSD-3 vs GPL-3) |
| 2025-11-28 | Transport-agnostic EventEmitter | Enable dual-mode usage |
| 2025-11-28 | Single package with optional deps | Simplify maintenance |
| 2025-11-28 | Polling for MVP, IDLE for Phase 2 | Faster time to market |

---

**Status:** ✅ Accepted and Implemented (Prototype)  
**Next Review:** Sprint 1 Retrospective (when production code ships)

---

**Signed:**  
Winston (Architect)  
Murat (Test Architect)  
John (Product Manager)  

Date: 2025-11-28
