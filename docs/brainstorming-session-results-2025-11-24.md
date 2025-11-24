# Brainstorming Session Results

**Session Date:** 2025-11-24
**Facilitator:** AI Brainstorming Facilitator
**Participant:** HC

## Session Start

**Session Plan:**
- Focus Area: Core features and functionality for Mail Reactor
- Approach: Progressive Technique Flow
- Techniques Selected: 
  1. First Principles Thinking (15 min)
  2. What If Scenarios (15 min)
  3. SCAMPER Method (20 min)
  4. Resource Constraints (10 min)

## Executive Summary

**Topic:** Core features and functionality for Mail Reactor

**Session Goals:** Explore and define the core feature set that will make Mail Reactor valuable and differentiated

**Techniques Used:** {{techniques_list}}

**Total Ideas Generated:** {{total_ideas}}

### Key Themes Identified:

{{key_themes}}

## Technique Sessions

### Technique 1: First Principles Thinking

**Fundamental Truths Discovered:**

1. **Email is a solved technical problem with abstraction gaps:**
   - Consumer email clients (Outlook, etc.) have usability issues
   - Code-level email (IMAP/SMTP) is too low-level
   - Commercial abstractions (Mailgun, Sendgrid) exist but are cloud-based and closed-source

2. **Core developer use cases:**
   - **Outbound:** Registration emails, OTP login, password reset, notifications
   - **Inbound:** Support request ingestion, workflow triggers, data processing

3. **The fundamental problem:**
   - Low-level protocols (IMAP/SMTP) distract developers from business logic
   - Existing high-level abstractions are cloud-based and proprietary
   - **Gap:** No open-source, self-hostable, high-level email abstraction

4. **Core value proposition emerging:**
   - Developers want to focus on business problems, not email infrastructure
   - Need for vendor independence and control (self-hosted)
   - Desire for open-source transparency and customization

5. **Essential abstraction layer:**
   - **Developer's first thought:** Messages (send/receive individual messages)
   - **Deeper reality:** Conversations (email threads, context, relationships)
   - **Tension identified:** Simple message APIs vs rich conversational context
   - **Design implication:** Start with message-level simplicity but support conversation-aware features

6. **Core concept crystallized - "Headless Email Client":**
   - **Not just:** An email sending/receiving API
   - **But rather:** A programmable email client without a UI
   - **Key capabilities emerging:**
     - Automatic thread grouping (like Outlook, but accessible via API)
     - Send new messages (initiate conversations)
     - Reply to messages (participate in conversations)
     - Receive notifications (reactive, event-driven)
   - **Mental model shift:** From "email infrastructure" to "email client you control via code"

---

### Party Mode Session - Competitive Analysis & Product Strategy

**Team Discussion with 9 agents produced:**

**Competitive Landscape:**
- **EmailEngine.app**: Commercial self-hosted email API (NOT open-source), yearly license model, unified REST API for IMAP/SMTP/Gmail/MS Graph, webhooks included, no explicit thread intelligence
- **Sendgrid/Mailgun**: Cloud SaaS, expensive at scale, vendor lock-in, strong deliverability but compliance concerns
- **Gap for Mail Reactor**: MIT core + commercial plugins vs EmailEngine's fully commercial model

**Commercial Model Decisions:**

**MIT Core (Free):**
- Send/receive emails with IMAP/SMTP
- Basic webhooks (no retry/signatures)
- Single account
- Simple templates (string interpolation)
- Basic message operations
- Plugin runtime system
- Simple logging

**Production Pack (Commercial Plugin):**
- Retry logic with delivery guarantees
- Webhook reliability (retry, signatures, health monitoring)
- Bounce/complaint handling & suppression lists
- Rate limiting & throttling
- Health monitoring & alerts
- Audit logs & request tracing

**Scale Pack (Commercial Plugin):**
- Multi-tenancy with isolation & quotas
- Advanced template engine (versioning, multi-language, A/B testing)
- Deliverability optimization (SPF/DKIM/DMARC automation, reputation monitoring)
- Search & filtering (full-text, advanced queries)
- Attachment handling (streaming, S3 storage, compression)
- Backup & recovery tools

**Conversation Pack (Commercial Plugin):**
- Thread detection & automatic grouping
- Reply-in-context with proper headers
- Conversation state tracking
- Thread history & context
- Conversation-aware search

**Architecture Decisions:**
- Static linking for all plugins (core and commercial)
- Separate repos: core (public/MIT) vs packs (private/commercial)
- Plugin API proven by core features using same plugin system
- License validation at startup for commercial plugins

**Open Source Governance (Pinned for later):**
- Core feature set frozen - clear boundaries
- Separate repos from day one
- CONTRIBUTING.md and GOVERNANCE.md with transparent commercial model
- CLA for commercial pack contributions
- Public roadmap showing core vs pack features

---

### Technique 2: What If Scenarios - Exploring Radical Possibilities

**Prompt: What if Mail Reactor had unlimited resources and could integrate with ANY system?**

**Multi-Channel Communication Hub:**
- **Beyond email:** WhatsApp, Telegram, Slack integration
- **Unified inbox:** All channels in one conversation view
- **Channel-agnostic API:** Send message to user via their preferred channel
- **Cross-channel threading:** Email thread continues on Slack, tracks context

**AI-Powered Intelligence:**
- **Message classification:** Automatic categorization (support, sales, urgent, spam)
- **Spam detection:** Learning system that adapts to user patterns
- **Smart routing:** Route messages based on content/sentiment
- **Auto-responses:** AI generates contextual replies for review/approval
- **Learning system:** Gets smarter over time based on user actions

**Implications:**
- Transforms from "email tool" to "communication platform"
- AI features could be premium plugins (AI Classification Pack, AI Assistant Pack)
- Multi-channel = much broader use cases (customer support platforms, unified comms)

**Prompt: What if Mail Reactor had NO interface - what becomes important?**

**Headless Core with Optional Interfaces:**
- **Core = Pure API** - No UI dependency, runs as daemon/service
- **Web UI = Optional plugin** - For SaaS offering and visual management
- **TUI (Terminal UI) = Developer-focused interface** - Like k9s for Kubernetes
  - Live monitoring of email queues
  - Real-time webhook delivery status
  - Thread visualization in terminal
  - Interactive debugging and inspection
  - Keyboard-driven workflow (vim-style navigation)
  - Perfect for SSH sessions and server management

**Why this is brilliant:**
- **Separation of concerns:** API core never coupled to UI decisions
- **Multiple interface options:** Web for business users, TUI for developers
- **Deploy anywhere:** Headless on servers, UI optional
- **Developer love:** Technical users LOVE great TUIs (k9s, lazygit, htop)
- **Marketing differentiation:** "The only email API with a badass TUI"

**TUI as killer feature:**
- Watch emails flowing in real-time
- Debug webhook deliveries interactively
- Inspect thread grouping visually
- Tail logs with filtering
- Quick config changes without editing files

**Prompt: What if Mail Reactor needed to process 10 million emails per second?**

**Scalable Architecture from Day One:**

**Deployment Modes:**
1. **Standalone mode** - Single process, all-in-one (dev/small deployments)
   - Install via Python package (`pip install mailreactor`)
   - Single command to start: `mailreactor start`
   - Perfect for side projects and testing

2. **Distributed mode** - Coordinator + Worker nodes
   - **Coordinator:** API server, job scheduling, state management
   - **Workers:** Email processing, IMAP connections, webhook delivery
   - Horizontal scaling: Add workers as load increases
   - docker-compose for local multi-node testing

3. **Kubernetes mode** - Production-grade orchestration
   - Helm chart for easy deployment
   - Auto-scaling workers based on queue depth
   - StatefulSets for coordinators, Deployments for workers
   - Service mesh ready

**Parallel Processing Design:**
- **Work queue architecture:** Redis/RabbitMQ for job distribution
- **Per-account worker assignment:** One IMAP connection per worker per account
- **Webhook parallelization:** Separate worker pool for webhook delivery
- **Shared state:** Distributed cache for thread detection, rate limiting

**Configuration flexibility:**
```yaml
mode: standalone|distributed|kubernetes
coordinator:
  replicas: 3
workers:
  min: 2
  max: 50
  scale_on: queue_depth
```

**Why this matters:**
- **Start simple:** `pip install && mailreactor start` - runs locally
- **Scale gradually:** Add docker-compose when ready
- **Scale massive:** Helm chart for production
- **Same codebase:** All modes use same core, just different orchestration

**Architecture benefits:**
- Parallel processing = handle millions of emails
- Horizontal scaling = pay-as-you-grow infrastructure
- Zero-downtime deployments
- Failure isolation (worker crashes don't kill coordinator)

**Prompt: What if plugins could be written in ANY programming language?**

**Language-Agnostic Plugin System:**

**Communication Models:**
1. **Unix pipes (stdin/stdout)** - Classic, simple, universal
   - Plugin receives JSON on stdin
   - Plugin outputs JSON on stdout
   - Works with ANY language
   - Lightweight, no dependencies

2. **Protocol Buffers** - Efficient binary protocol
   - Faster serialization than JSON
   - Strong typing across languages
   - Version compatibility built-in

3. **gRPC** - Service-based plugins
   - Plugin runs as separate service
   - Core calls plugin via RPC
   - Can run on different machines
   - More overhead but maximum flexibility

**State Model - Erlang-inspired:**
- **Core state object** with known attributes:
  ```json
  {
    "message": {...},
    "thread": {...},
    "account": {...},
    "metadata": {...}
  }
  ```
- **Extension fields** - Plugins can add custom data:
  ```json
  {
    ...core fields...,
    "extensions": {
      "spam_classifier": {"score": 0.12, "category": "ham"},
      "sentiment_analyzer": {"sentiment": "positive", "confidence": 0.89}
    }
  }
  ```
- **Pipeline model:** State flows through plugin chain
- **Immutability option:** Plugins return new state (functional, safe)
- **Side effects tracked:** Plugins declare what they modify

**Why Erlang model is brilliant:**
- **Process isolation:** Plugin crashes don't kill core
- **Hot code reloading:** Swap plugins without restart
- **Message passing:** Clean boundaries, no shared memory
- **Supervision trees:** Automatic plugin restart on failure
- **Actor model:** Each account could be an actor/process

**Language support benefits:**
- Go plugins for performance (thread detection, parsing)
- Python plugins for AI/ML (classification, learning)
- Rust plugins for security-critical features
- JavaScript plugins for easy community contributions
- Any language with JSON I/O works

**Trade-offs:**
- stdin/stdout = simplest, but highest overhead per call
- protobuf = fast, but requires compilation step
- gRPC = most flexible, but complex for simple plugins

**Hybrid approach:**
- Core plugins: Native (Python/Go) for performance
- External plugins: stdin/stdout or gRPC for flexibility
- Let plugin author choose based on needs

**Prompt: What if Mail Reactor needed to work completely offline with intermittent connectivity?**

**Resilience via Battle-Tested Components:**

**Queue & Persistence Requirements:**
- Must work in standalone mode (embedded)
- Must work in distributed mode (networked)
- Must handle offline queueing
- Must persist across restarts
- Should be industry-proven, not custom-built

**Candidate Technologies:**

**Redis:**
- ✅ Embedded mode: Redis can run alongside core
- ✅ Distributed: Redis cluster for multi-node
- ✅ Persistence: AOF (append-only file) + RDB snapshots
- ✅ Queues: Lists, Streams for job queues
- ✅ Proven: EmailEngine uses it
- ⚠️ Requires separate process even in standalone

**SQLite + Job Queue:**
- ✅ Embedded: Single file, zero setup
- ✅ Persistence: Native SQL durability
- ✅ ACID guarantees
- ✅ Works everywhere Python works
- ⚠️ Distributed mode needs different solution (switch to Postgres?)

**Hybrid approach (Best of both):**
- **Standalone mode:** SQLite for state + in-process queue
- **Distributed mode:** Redis/PostgreSQL for shared state + RabbitMQ/Redis Streams for queues
- **Same API:** Abstract queue interface, swap backends

**NATS with JetStream:**
- ✅ Embedded mode: NATS server can embed
- ✅ Distributed: Built for clustering
- ✅ Persistence: JetStream adds durable streams
- ✅ Lightweight: Go binary, minimal resources
- ✅ Resilience: Designed for intermittent connectivity
- 🤔 Less common than Redis (community familiarity)

**Design principle:**
- **Don't build persistence layer from scratch**
- **Abstract behind interface:** `QueueBackend`, `StateStore`
- **Swap implementations:** SQLite → Redis → PostgreSQL based on mode
- **Research decision:** Evaluate Redis vs NATS vs hybrid approach

**Offline resilience features:**
- Queue outgoing emails when SMTP unreachable
- Queue webhook deliveries when endpoint down
- Persist IMAP sync state to resume after disconnect
- Exponential backoff with jitter on reconnection
- Health checks before attempting operations

**Action item:** Research and decide on queue/persistence stack that works across all deployment modes

---

### Technique 3: SCAMPER Method - Systematic Feature Innovation

**Base concept: "Headless Email Client"**

**S - SUBSTITUTE: Alternative Protocols and Integrations**

**Protocol Substitutions:**
- **IMAP/SMTP → Multi-protocol support:**
  - JMAP (modern email protocol, JSON-based, better than IMAP)
  - Matrix protocol (federated messaging)
  - ActivityPub (Mastodon, federated social)
  - Telegram Bot API
  - Slack API
  - WhatsApp Business API

**MCP (Model Context Protocol) Integration - LLM Compatibility:**
- **What is MCP?** Protocol for connecting LLMs to data sources and tools
- **Mail Reactor as MCP Server:**
  - Expose email operations as MCP tools
  - LLMs can read emails, send replies, search threads
  - "Claude, draft a reply to the support ticket in thread #123"
  - "ChatGPT, summarize all emails from customer X this week"
  
- **Use Cases:**
  - AI assistants that can actually interact with your email
  - Natural language email management
  - AI-powered email agents that take actions
  - Voice-to-email workflows
  
- **Architecture:**
  - Mail Reactor exposes MCP endpoints
  - LLMs connect via MCP client
  - Safe: LLM can only do what MCP permissions allow
  - Plugin: MCP Server Plugin (could be commercial or community)

**Why this is powerful:**
- Makes Mail Reactor **LLM-native**
- Enables AI automation without building AI
- Differentiator: "The email API that speaks to LLMs"
- Future-proof: MCP is gaining adoption (Anthropic, others)

**Multi-protocol vision:**
- Core: Email (IMAP/SMTP)
- Plugins: Telegram, Slack, WhatsApp, Matrix, JMAP
- MCP Plugin: LLM integration layer
- Unified API: Send/receive regardless of protocol
- Thread intelligence works across ALL protocols

**C - COMBINE: Powerful Feature Combinations**

**Webhooks + MCP = AI Agents that React and Act:**
- Email arrives → Webhook fires → LLM receives notification via MCP
- LLM analyzes email context, thread history, sender
- LLM decides action: reply, forward, categorize, escalate
- LLM executes via MCP tools (send reply, update thread state)
- **Result:** Autonomous AI email agent loop

**Example flow:**
```
1. Support email arrives
2. Webhook → MCP notification to Claude
3. Claude reads thread history via MCP
4. Claude drafts reply based on knowledge base
5. Claude sends reply via MCP (or queues for human approval)
6. Human reviews AI actions via TUI/Web UI
```

**Why this is killer:**
- Not just "AI can read email"
- Not just "AI can write email"
- **AI can be autonomous email agent with human oversight**

**Focus Decision: Headless Email Client**
- **In scope:** Email (IMAP/SMTP), threads, webhooks, MCP integration
- **Out of scope:** Calendar, contacts, scheduling (let AI/other tools handle)
- **Philosophy:** Do ONE thing perfectly - be the best headless email client
- **Integration strategy:** Email is the interface, other services orchestrate via API/MCP

**Let AI orchestrate across domains, Mail Reactor owns email domain**

**A - ADAPT: Patterns from Other Successful Tools**

**Stripe's Webhook Excellence → Mail Reactor Webhook DX:**

Stripe has gold-standard webhook implementation. Adapt these patterns:

**Developer Experience Features:**
1. **Event Inspector Dashboard (TUI/Web)**
   - Real-time view of every webhook delivery attempt
   - Full request/response details (payload, headers, status codes)
   - Timeline view with retry attempts
   - Filter by account, event type, success/failure

2. **Manual Replay/Retry**
   - One-click resend any past webhook event
   - Bulk replay (e.g., "replay all failed events from yesterday")
   - Perfect for recovering from downtime or debugging

3. **Local Development Mode**
   - CLI command: `mailreactor webhooks listen --forward localhost:3000`
   - Routes webhook events to local dev environment
   - No ngrok or tunnel needed
   - See events in real-time during development

4. **Webhook Testing Tools**
   - Send synthetic test events manually
   - Test different scenarios (new email, bounced, spam detected)
   - Validate endpoint before going live

5. **Webhook Health Monitoring**
   - Success/failure rates per endpoint
   - Automatic endpoint disabling after repeated failures
   - Alert when webhook endpoint degraded
   - Response time tracking

6. **Signature Verification** (Production Pack)
   - Cryptographic signing of webhook payloads
   - Verification libraries for common languages
   - Prevents spoofing and replay attacks

**Where these fit:**
- **Core:** Basic webhook POST (no retry, no signatures)
- **Production Pack:** Retry logic, signatures, health monitoring, event log, replay
- **TUI/Web UI:** Event inspector, testing tools, manual replay

**Developer love:** "Mail Reactor has the best webhook debugging experience I've ever used"

**M - MODIFY: Magnify, Minimize, Change Attributes**

**MINIMIZE: Zero-Config Philosophy**

**Goal: Awesome GitHub README with one-liner quickstart**

```bash
# That's it. No config files, no setup, just run:
pipx run mailreactor --account hc@gmail.com --webhook http://localhost:8081
```

**What this requires:**
- Intelligent defaults for everything
- OAuth flow in browser for authentication (if needed)
- Automatic IMAP/SMTP server detection from email domain
- SQLite for storage (auto-creates db file)
- No Redis/Postgres required for standalone
- Sensible default port (maybe 8080 for API)
- Auto-start TUI or provide web link

**Progressive configuration:**
- **Zero config:** Works immediately for 80% of users
- **CLI flags:** Quick tweaks without config file
- **Config file:** Advanced users can create `mailreactor.yml` for full control
- **Environment variables:** 12-factor app compatibility

**Example progression:**
```bash
# Instant start
pipx run mailreactor --account me@gmail.com

# Add webhook
pipx run mailreactor --account me@gmail.com --webhook http://myapp/hook

# Multiple accounts
pipx run mailreactor --config mailreactor.yml

# Production deployment
docker-compose up  # or kubectl apply -f mailreactor.yaml
```

**MODIFY: Immutable Event Sourcing + Erlang Model**

**Architecture: Events as Source of Truth**

**Core principle:** 
- Input (email, command) is never mutated
- System produces new state from input + current state
- Pure functional transformation
- All state changes are events in event log

**Email as immutable event stream:**
```
Event 1: EmailReceived(id=123, from=user@example.com, ...)
Event 2: ThreadDetected(email_id=123, thread_id=456)
Event 3: WebhookDelivered(email_id=123, endpoint=http://..., status=200)
Event 4: EmailMarkedRead(email_id=123, read_at=timestamp)
```

**Benefits:**
- **Audit trail:** Every state change is logged
- **Time travel:** Replay events to reconstruct any past state
- **Debugging:** See exactly what happened and when
- **Testing:** Replay production events in dev
- **Reprocessing:** Changed thread detection algorithm? Replay all events

**Erlang-style state transformation:**
```python
# Pure function: old_state + event → new_state
def handle_email_received(state, event):
    # Never mutate state
    # Return new state with event incorporated
    return State(
        emails=state.emails + [event.email],
        threads=detect_thread(state, event.email),
        metadata=state.metadata
    )
```

**Storage model:**
- **Event log:** Append-only (SQLite, PostgreSQL, or specialized event store)
- **Projections:** Current state materialized from events (for fast queries)
- **Snapshots:** Periodic state snapshots to avoid replaying millions of events

**Where this fits:**
- Core uses event sourcing internally
- Plugins receive immutable state, return transformations
- All state changes go through event log
- TUI can show event stream in real-time

**Developer appeal:** "Mail Reactor: The email API that does event sourcing right"

**P - PUT TO OTHER USES: Unexpected Use Cases**

**Email as Database (Community Plugin Opportunity):**
- Store structured data in email metadata/body
- Query emails like a database via API
- Use email as append-only log (event sourcing meets email)
- **Plugin:** `mailreactor-db` - turns email into queryable data store
- **Market dynamic:** Community plugin adds value, doesn't compete with commercial packs
  - Commercial packs: Reliability, scale, conversation intelligence
  - Community plugins: Creative use cases, niche features
  - **Ecosystem growth:** More plugins = more reasons to use Mail Reactor

**Email Testing Service (MCP + LLM Integration):**
- **Use case:** QA teams testing email workflows in their apps
- **Traditional approach:** Manual testing, checking mailboxes, painful
- **Mail Reactor approach:**
  ```
  QA Engineer: "Hey Claude, test the password reset flow"
  Claude via MCP:
    1. Triggers password reset in test app
    2. Monitors Mail Reactor for reset email
    3. Extracts reset link from email
    4. Validates link format, expiry, security
    5. Reports back: "✅ Reset email received in 2.3s, link valid"
  ```

**LLM-Powered Testing Features:**
- Autonomous email flow testing
- AI validates email content against requirements
- Checks deliverability, timing, formatting
- Regression testing: "Does this still work like it did last month?"
- Load testing: "Send 1000 registration emails, verify all delivered"

**Testing Plugin/Pack Potential:**
- **Community plugin:** Basic email testing utilities
- **Commercial pack:** Advanced testing features (AI validation, load testing, reporting)

**Other Unexpected Uses:**
- **Email forensics:** Legal/compliance investigations with full audit trail
- **Migration tool:** Move emails between providers with thread preservation
- **IoT notifications hub:** Devices send status via email, AI triages
- **Collaborative inbox:** Multiple AI agents + humans managing shared inbox

**Community vs Commercial Balance:**
- **Strategy:** Welcome community plugins - they grow the ecosystem
- **Differentiation:** Commercial packs focus on production/scale/reliability
- **Examples:**
  - Community: Email-as-database, custom integrations, experimental features
  - Commercial: Thread intelligence, production reliability, enterprise scale
- **Risk mitigation:** Clear value prop for commercial packs (things businesses NEED)

**E - ELIMINATE: Remove Storage Requirement**

**RADICAL IDEA: Email Account IS the Event Source**

**Core Philosophy:**
- Email server already stores all emails (IMAP)
- Why duplicate storage locally?
- **Stateless by default, persistent storage optional**

**Architecture Models:**

**1. Stateless Mode (Core - Default):**
- No local database required
- State reconstructed from IMAP on startup
- Email account = source of truth
- In-memory cache for performance
- Restart = rebuild state from email server

**How it works:**
```bash
pipx run mailreactor --account me@gmail.com
# On startup:
# 1. Connect to IMAP
# 2. Fetch recent emails (with filters)
# 3. Rebuild state in memory
# 4. Start processing new emails
# 5. Shutdown = state discarded, no persistence needed
```

**Smart filtering to avoid ingesting everything:**
```bash
# Only emails from last 7 days
--filter "since:7d"

# Only from specific sender
--filter "from:customer@company.com"

# Only in specific folder
--filter "folder:INBOX"

# Combination
--filter "since:30d from:support@"
```

**State storage in email itself (genius!):**
- Store Mail Reactor state as special emails in a folder
- Example: `[MailReactor]/state/thread-mappings`
- Structured data in email body (JSON)
- Email headers as metadata
- IMAP = distributed, durable state store (for free!)

**2. Persistent Storage Mode (Production Pack):**
- Local database (SQLite/Postgres) for performance
- Full event log with audit trail
- Fast queries without IMAP round-trips
- Historical data beyond email retention
- Survives email account deletion/changes

**Benefits of Stateless Default:**
- ✅ **Zero setup:** No database to install/configure
- ✅ **Zero maintenance:** No backup, no migrations
- ✅ **Portable:** Works anywhere with IMAP access
- ✅ **Self-healing:** Restart = fresh state from source of truth
- ✅ **Simple README:** Just run the command

**When you need Production Pack (Persistent Storage):**
- High-volume (rebuilding from IMAP too slow)
- Complex queries (need indexed database)
- Historical analysis (beyond email retention)
- Compliance/audit (immutable event log)
- Multi-node coordination (shared state)

**R - REVERSE: Design for Distributed, Deploy as Standalone**

**REVERSE TYPICAL ARCHITECTURE APPROACH:**

**Traditional:** Start simple (monolith) → scale later (refactor to distributed) → pain

**Mail Reactor:** Design distributed first → deploy as standalone → scale naturally

**Architecture:**
- **Core abstraction:** Assume distributed from day one
- **Coordinator/Worker pattern:** Built into design
- **Standalone mode:** Just run coordinator + worker in same process
- **Scale mode:** Separate coordinator/worker processes
- **Same code, different topology**

**Benefits:**
- No architectural rewrite when scaling
- Standalone gets battle-tested distributed code
- Worker isolation = better fault tolerance even in standalone
- Easy to reason about (same patterns everywhere)

**Deployment configurations:**
```python
# Standalone (default)
mailreactor start
# → Runs: coordinator + worker in one process

# Distributed
mailreactor coordinator &
mailreactor worker --coordinator http://localhost:5000
mailreactor worker --coordinator http://localhost:5000
# → Separate processes, horizontal scaling

# Kubernetes
# → Coordinator as StatefulSet, Workers as Deployment
```

**Design principle:** "Build for distributed, optimize for standalone"

**The GitHub README becomes:**
```markdown
# Mail Reactor 🚀
Headless email client. Zero config. Scales from laptop to cluster.

## Quickstart (Stateless)
pipx run mailreactor --account you@gmail.com

No database. No setup. Email is your state store.

## Production (Persistent)
Add Production Pack for local storage, audit logs, and scale.
```

---

### Technique 4: Resource Constraints - MVP Definition

**Constraint: Only 3 features for MVP, ship in 2 weeks**

**Essential Features Identified:**

**1. REST API: Add Mail Account**
```
POST /accounts
{
  "email": "user@gmail.com",
  "imap_host": "imap.gmail.com",  // Optional, auto-detect if not provided
  "smtp_host": "smtp.gmail.com",  // Optional, auto-detect if not provided
  "password": "app-password"
}

Response: 201 Created
{
  "account_id": "acc_123",
  "status": "connected"
}
```

**2. REST API: Send Messages**
```
POST /accounts/{account_id}/messages
{
  "to": "recipient@example.com",
  "subject": "Hello",
  "body": "Message text",
  "html": "<p>Message HTML</p>",  // Optional
  "attachments": [...]  // Optional
}

Response: 200 OK
{
  "message_id": "msg_456",
  "status": "sent"
}
```

**3. REST API: Retrieve Messages with Server-Side Filtering**

**IMAP Search Capabilities (RFC 3501):**
IMAP natively supports server-side search - use this from day one:

```
GET /accounts/{account_id}/messages?filter=<imap_search>

IMAP search criteria supported:
- ALL - all messages
- UNSEEN - unread messages
- SEEN - read messages
- FROM "sender@example.com" - from specific sender
- TO "recipient@example.com" - to specific recipient
- SUBJECT "keyword" - subject contains keyword
- SINCE "date" - messages since date
- BEFORE "date" - messages before date
- BODY "text" - body contains text
- OR (criteria1) (criteria2) - logical OR
- NOT (criteria) - logical NOT

Examples:
GET /messages?filter=UNSEEN
GET /messages?filter=FROM "support@company.com"
GET /messages?filter=SINCE "01-Jan-2025"
GET /messages?filter=OR UNSEEN (FROM "urgent@company.com")
```

**Why IMAP search is perfect:**
- ✅ Server-side filtering (fast, no local processing)
- ✅ Standardized (RFC 3501, works across providers)
- ✅ Powerful (date ranges, boolean logic, text search)
- ✅ Efficient (only matching messages transferred)

**Response:**
```json
{
  "messages": [
    {
      "id": "msg_789",
      "from": "sender@example.com",
      "to": "user@gmail.com",
      "subject": "Hello",
      "date": "2025-11-24T10:30:00Z",
      "body_preview": "First 200 chars...",
      "unread": true
    }
  ],
  "total": 42,
  "next_page": "cursor_abc"
}
```

**MVP = These 3 endpoints. Nothing else.**

No webhooks, no threads, no TUI, no persistence, no plugins.

Just: Connect account → Send email → Query emails with IMAP search

**This is genuinely useful:**
- Developers can build transactional email (password resets)
- Developers can poll for incoming emails (support tickets)
- All the complex IMAP/SMTP is abstracted away
- Server-side filtering means efficient queries

**Everything else is v2+:**
- v2: Webhooks (reactive instead of polling)
- v3: Thread detection (conversation intelligence)
- v4: Commercial packs (reliability, scale, AI)
- v5: TUI, MCP, multi-protocol

**The README for MVP:**
```markdown
# Mail Reactor MVP

## Install
pipx install mailreactor

## Run
mailreactor start

## Use
curl -X POST http://localhost:8080/accounts \
  -d '{"email":"me@gmail.com","password":"app-pw"}'

curl -X POST http://localhost:8080/accounts/acc_123/messages \
  -d '{"to":"you@example.com","subject":"Hi","body":"Hello"}'

curl http://localhost:8080/accounts/acc_123/messages?filter=UNSEEN
```

**Ships in 2 weeks. Solves real problem. Room to grow.**

---

## Idea Categorization

### Immediate Opportunities

_Ideas ready to implement now - MVP and Phase 2_

**MVP (Phase 1 - 2 weeks):**
- 3-endpoint REST API (add account, send messages, retrieve with IMAP search)
- Zero-config deployment: `pipx run mailreactor --account me@gmail.com`
- Stateless mode (email-as-storage, no local DB)
- Server-side IMAP filtering (use native IMAP search capabilities)
- Basic in-memory architecture

**Phase 2 (Early addition - high impact):**
- **Basic webhooks** - Simple HTTP POST on email received (no retry yet)
  - Why early: Enables reactive patterns, much better DX than polling
  - MVP: Fire-and-forget webhook
  - Production Pack later: Retry, signatures, monitoring
  
- **MCP (Model Context Protocol) integration** - LLM-native email API
  - Why early: **Massive hype potential** - "First email API LLMs can control"
  - Research needed: How complex is MCP implementation?
  - If quick to build (< 1 week): Add to Phase 2 for differentiation
  - Enables: "Hey Claude, check my emails and draft responses"
  - Marketing gold: Demo videos of AI controlling email

**Action item:** Research MCP implementation complexity - if simple, prioritize high for Phase 2

### Future Innovations

_Promising concepts requiring development - Phase 3+_

**Architecture & Scaling:**
- Event sourcing architecture (immutable events, Erlang-style state)
- Distributed-first design (coordinator/worker pattern)
- Persistent storage mode (Production Pack - SQLite/Postgres)
- Plugin system (language-agnostic via stdin/stdout or gRPC)
- Kubernetes deployment (Helm charts, auto-scaling)

**Core Features:**
- Thread detection and conversation intelligence (Conversation Pack)
- TUI (Terminal UI like k9s for developers)
- Web UI for visual management
- Commercial pack architecture (Production, Scale, Conversation)

**Developer Experience:**
- Stripe-quality webhook debugging (event inspector, replay, local dev mode)
- Advanced IMAP features beyond basic search
- Multi-account management
- Template system

### Moonshots

_Ambitious, transformative concepts - Long-term vision_

**AI & Automation:**
- Webhooks + MCP closed-loop AI agents (autonomous email handling)
- AI classification and spam detection with learning
- Auto-response generation with human approval
- Sentiment analysis and priority routing

**Multi-Channel:**
- Protocol plugins: Telegram, Slack, WhatsApp, Matrix, JMAP
- Unified conversation API across all channels
- Cross-channel thread intelligence

**Ecosystem:**
- Community plugin marketplace
- Email-as-database plugin (community-built)
- Email testing service (QA automation via MCP + LLM)
- Email forensics and compliance tools

**Advanced Architecture:**
- Zero-knowledge encryption mode
- P2P email protocols
- Blockchain-based email verification (if it makes sense)

---

**Revised Roadmap Priority:**

## Phase Structure

### MVP (Weeks 1-2): Validate the Concept
**Goal:** Ship minimal viable product to validate demand

**Features:**
- 3 REST endpoints only:
  1. POST /accounts (add email account)
  2. POST /accounts/{id}/messages (send email)
  3. GET /accounts/{id}/messages?filter=... (retrieve with IMAP search)
- Stateless mode (email-as-storage, no local DB required)
- Zero-config deployment: `pipx run mailreactor --account me@gmail.com`
- In-memory state only

**Success metric:** Do developers want this? Get initial feedback.

---

### Core (Months 1-2): Build Stable Foundation
**Goal:** Feature-complete MIT-licensed core with proven plugin architecture

**Features:**
- **Plugin system architecture** - Language-agnostic (stdin/stdout or gRPC)
  - Core features implemented as plugins to prove the system works
  - Clean plugin API and boundaries established
- **Basic webhooks** (in Core, simple fire-and-forget)
  - HTTP POST on email received
  - No retry, no signatures (those are Production Pack)
  - Enables reactive patterns vs polling
- **Event sourcing foundation** - Immutable events, Erlang-style state
- **Stateless architecture** - Email account as event source
- **Smart IMAP filtering** - Server-side search to avoid ingesting everything
- **Distributed-ready design** - Coordinator/worker pattern from day one
  - Runs as single process in standalone mode
  - Can separate into multiple processes later
- **Zero-config remains** - Works out of the box

**Success metric:** Core is stable, useful, and plugin architecture proven.

---

### Community Plugins (Parallel with Core development)
**Goal:** Prove plugin extensibility, generate hype

**MCP Plugin (High Priority - Build Early!):**
- **What:** Model Context Protocol server plugin
- **Why:** LLM-native email API - massive differentiator
- **Enables:** 
  - "Hey Claude, check my emails and draft responses"
  - AI agents can read/send/search emails
  - Marketing gold: First self-hosted email API with MCP
- **Action:** Research MCP complexity - if simple, build during Core phase
- **Release:** Community plugin (MIT licensed, separate repo)
- **Hype factor:** Demo videos of Claude controlling email = HackerNews front page

**Other Community Plugins (Later):**
- Email-as-database plugin
- Custom protocol integrations
- Niche use cases

**Repository structure:**
- `mailreactor/core` (MIT, public)
- `mailreactor/mcp-plugin` (MIT, public, community)
- Commercial packs in private repos (built later)

---

### Production Pack (Month 3+): First Commercial Offering
**Goal:** Monetize users who need production reliability

**Features:**
- **Retry logic with delivery guarantees:**
  - SMTP retry with exponential backoff
  - Email send confirmation tracking
  - Queue management for failed sends
  - Dead letter queue for permanently failed
- **Webhook reliability:**
  - Retry with exponential backoff
  - Cryptographic signature verification
  - Webhook health monitoring
  - Automatic endpoint disabling on repeated failures
  - Event log with manual replay capability
  - Stripe-quality debugging experience
- **Persistent storage:**
  - Local database (SQLite/PostgreSQL)
  - Full event log with audit trail
  - Fast queries without IMAP round-trips
  - Historical data beyond email retention
- **Bounce and complaint handling:**
  - Automatic bounce detection
  - Suppression list management
  - ISP feedback loop processing
- **Rate limiting and throttling:**
  - Per-provider limits
  - Smart queuing
  - Burst protection
- **Health monitoring and alerts:**
  - Connection health per account
  - Quota tracking
  - Auth expiry alerts
  - Proactive notifications
- **Audit logs and request tracing:**
  - Structured logging
  - Full request/response tracing
  - Webhook delivery logs

**Pricing:** $500-1000/year (TBD based on market research)

**Success metric:** Converting free users to paying customers.

---

### Scale Pack (TBD - If Market Demands)
**Goal:** Support enterprise scale and multi-tenant deployments

**Features:**
- Multi-tenancy with isolation and per-tenant quotas
- Advanced template engine (versioning, multi-language, A/B testing)
- Deliverability optimization (SPF/DKIM/DMARC automation, reputation monitoring)
- Advanced search and filtering (full-text, complex queries)
- Attachment handling (streaming, S3 storage, compression)
- Backup and recovery tools
- Kubernetes optimization (Helm charts, auto-scaling)

**Build only if:** Users are hitting limits and requesting these features.

---

### Conversation Pack (TBD - Maybe Never)
**Goal:** Thread intelligence for conversational email applications

**Features:**
- Thread detection and automatic grouping
- Reply-in-context with proper headers
- Conversation state tracking
- Thread history and context
- Conversation-aware search

**Build only if:** Market segment (CRMs, helpdesks) shows strong demand.

---

### Other Potential Packs (Speculative)
- **Analytics Pack:** Reporting, dashboards, insights
- **AI Pack:** Classification, spam detection, auto-responses
- **Multi-Channel Pack:** Telegram, Slack, WhatsApp integrations

**Build based on:** Customer demand, not speculation.

---

## Governance & Repository Setup (Immediate)

**Before building commercial packs:**
1. Set up separate repositories:
   - `mailreactor/core` (MIT, public)
   - `mailreactor/mcp-plugin` (MIT, public)
   - `mailreactor/production-pack` (Commercial, private)
   - Additional packs as needed
2. Write CONTRIBUTING.md with clear boundaries
3. Write GOVERNANCE.md explaining commercial model
4. Define CLA for pack contributions (if accepting)
5. Create public roadmap showing core vs pack features
6. Be transparent: "We need revenue to sustain development"

---

## Key Decisions Summary

**What's in MIT Core:**
- Basic email send/receive via REST API
- Server-side IMAP filtering
- Basic webhooks (fire-and-forget)
- Plugin runtime
- Stateless mode
- Event sourcing foundation
- Simple templates (string interpolation)

**What's Commercial (Production Pack):**
- Retry logic (SMTP + webhooks)
- Persistent storage and audit logs
- Bounce/complaint handling
- Rate limiting and throttling
- Health monitoring and alerts
- Webhook reliability features

**What's Community:**
- MCP plugin (high priority)
- Creative/niche plugins
- Experimental features

**Timeline:**
- **Now - Week 2:** MVP (validate)
- **Month 1-2:** Core + MCP plugin (foundation + hype)
- **Month 3+:** Production Pack (monetize)
- **Later:** Scale Pack, Conversation Pack (if demanded)

{{technique_sessions}}

## Action Planning

### Top 3 Priority Ideas

#### #1 Priority: Build MVP (3 REST Endpoints)

**Rationale:** 
- Validates the entire concept - do developers actually want this?
- Gets something tangible running quickly
- Proves IMAP/SMTP abstraction works
- Foundation for everything else
- Can test, demo, and gather feedback immediately

**Next steps:**
1. **Set up project structure**
   - Create GitHub repo: `mailreactor/core`
   - Initialize Python project (or chosen language)
   - Set up basic REST framework (FastAPI, Flask, or similar)
   - Add basic tests and CI

2. **Implement IMAP/SMTP abstraction layer**
   - Research Python libraries: `imaplib`, `smtplib` (built-in) or higher-level like `imapclient`
   - Build connection management (connect, authenticate, handle errors)
   - Implement server auto-detection from email domain
   - Handle OAuth2 for Gmail/Outlook (or defer to app passwords for MVP)

3. **Build 3 core endpoints**
   - `POST /accounts` - Add email account with credentials
   - `POST /accounts/{id}/messages` - Send email via SMTP
   - `GET /accounts/{id}/messages?filter=...` - Retrieve emails with IMAP search
   
4. **Add stateless in-memory state**
   - Store connected accounts in memory
   - Cache recent emails for quick access
   - No database yet - truly stateless

5. **Zero-config CLI**
   - Entry point: `mailreactor start`
   - Optional flags: `--account`, `--port`
   - Auto-start API server on localhost:8080

6. **Write README with quickstart**
   - One-liner install: `pipx install mailreactor`
   - One-liner run: `mailreactor start`
   - Simple curl examples for all 3 endpoints

**Resources needed:**
- Python development environment
- Test email accounts (Gmail, Outlook, self-hosted)
- IMAP/SMTP testing tools
- 2-4 days focused coding time

**Timeline:**
- Week 1: Project setup, IMAP/SMTP abstraction, first endpoint
- Week 2: Complete all 3 endpoints, CLI, basic tests, README
- **Target: Working MVP in 2 weeks**

#### #2 Priority: Research & Validate MCP Integration

**Rationale:**
- You're keen to try this soon
- Massive differentiator if simple to implement
- Generate hype: "First self-hosted email API with MCP support"
- Validates plugin architecture early
- Marketing gold for launch

**Next steps:**
1. **Understand MCP protocol**
   - Read Anthropic's MCP documentation
   - Review MCP specification and examples
   - Understand: Is it just wrapping REST APIs in MCP format?
   - Check existing Python MCP server libraries

2. **Assess implementation complexity**
   - Estimate: Days? Weeks? Months?
   - Identify: What's the minimal viable MCP implementation?
   - Determine: Can basic MCP be added to Core phase (Month 1-2)?

3. **Design MCP tool mapping**
   - Map email operations to MCP tools:
     - `send_email` tool
     - `search_emails` tool
     - `read_email` tool
     - `get_threads` tool (if thread detection exists)
   - Define parameters and responses

4. **Prototype if simple**
   - If research shows <1 week effort: Build basic MCP plugin
   - Test with Claude Desktop or other MCP client
   - Demo: "Claude, check my emails"

5. **Decide on timeline**
   - If simple: Include in Core phase (Month 1-2)
   - If complex: Defer to community plugin later
   - If very complex: Reconsider priority

**Resources needed:**
- Time to read MCP docs thoroughly
- MCP client for testing (Claude Desktop, or build simple client)
- Test LLM API access (Claude, GPT-4)
- 1-2 days research time

**Timeline:**
- **Immediate (this week):** Research MCP documentation and complexity
- **Decision point:** Include in Core phase or defer?
- **If simple:** Build during Core development (Month 1-2)

#### #3 Priority: Define Plugin Architecture

**Rationale:**
- Core phase depends on clean plugin system
- Proves extensibility model works
- Enables MCP plugin to be built separately
- Allows community contributions
- Critical for commercial packs later

**Next steps:**
1. **Choose plugin communication model**
   - Research options: stdin/stdout (simplest), gRPC (flexible), native Python (performant)
   - Decision: Start with stdin/stdout for language-agnostic support
   - Can add gRPC later if needed

2. **Design state model (Erlang-inspired)**
   - Define core state object structure (message, thread, account, metadata)
   - Define extension fields mechanism
   - Specify immutable state transformation pattern
   - Document how plugins add custom data

3. **Define plugin lifecycle**
   - How plugins register themselves
   - How core discovers and loads plugins
   - Plugin initialization, execution, shutdown
   - Error handling and plugin crash isolation

4. **Implement plugin runtime**
   - Plugin registry/loader
   - State pipeline (pass state through plugin chain)
   - JSON serialization for stdin/stdout
   - Example "hello world" plugin

5. **Prove it works**
   - Implement one core feature as a plugin (e.g., basic webhook)
   - Dogfooding: If core features work as plugins, API is good
   - Document plugin development guide

6. **Set up plugin repository structure**
   - `mailreactor/core` - contains plugin runtime
   - `mailreactor/mcp-plugin` - first community plugin
   - Plugin manifest/registry concept

**Resources needed:**
- Time to design and prototype plugin system
- Understanding of process isolation, IPC
- JSON schema design for state objects
- 3-5 days design and implementation

**Timeline:**
- **Month 1:** Design plugin architecture (parallel with MVP completion)
- **Month 2:** Implement plugin runtime, prove with core features as plugins
- **Outcome:** Core phase complete with working plugin system

---

## Execution Strategy

**Sequential priorities with learning feedback:**

1. **Start with #1 (MVP)** - Build the foundation
   - Weeks 1-2: Working 3-endpoint REST API
   - Validates concept, proves IMAP/SMTP abstraction works

2. **Then #2 (MCP Research)** - Understand the target
   - Week 2-3: Research MCP protocol complexity
   - Understand how MCP plugin should integrate with core
   - Informs plugin architecture design

3. **Use #2 to inform #3 (Plugin Architecture)** - Design with real use case
   - Week 3-4: Design plugin system with MCP as primary example
   - MCP plugin becomes the proving ground for plugin architecture
   - Build MCP plugin to validate plugin API design
   - If plugin API works well for MCP, it'll work for other plugins

**Why this sequence works:**
- MVP gives you working foundation to extend
- MCP research provides concrete requirements for plugin system
- Building MCP plugin validates/refines plugin architecture
- Real-world plugin (MCP) is better teacher than theoretical design
- By Month 2: Core + working plugin system + MCP plugin = massive launch momentum

**Key insight:** Don't design plugin architecture in abstract - design it to make MCP plugin work beautifully, then generalize.

## Reflection and Follow-up

### What Worked Well

**Technique Effectiveness:**
- **First Principles Thinking:** Crystallized "Headless Email Client" concept - clear mental model that differentiates from competitors
- **Party Mode:** Multi-agent discussion provided crucial commercial model clarity (Core vs Packs structure)
- **What If Scenarios:** Unlocked ambitious ideas (MCP integration, stateless architecture, event sourcing)
- **SCAMPER:** Systematic exploration produced concrete features (Stripe-quality webhooks, zero-config)
- **Resource Constraints:** Forced clarity on MVP (just 3 endpoints) - prevents over-engineering

**Session Flow:**
- Progressive technique flow worked well - each technique built on previous insights
- Switching between divergent (What If) and convergent (Resource Constraints) thinking was productive
- Party Mode at the right moment brought architectural and business validation

### Areas for Further Exploration

**Technical Research Needed:**
1. **MCP Protocol Complexity** - How much effort is minimal viable MCP integration?
2. **Queue/Persistence Stack** - Redis vs NATS vs SQLite/Postgres hybrid for different deployment modes
3. **IMAP Libraries** - Best Python library for robust IMAP handling (imapclient, aioimaplib, others)
4. **Plugin IPC** - Performance comparison of stdin/stdout vs gRPC for plugin communication
5. **OAuth2 Flow** - Smoothest way to handle Gmail/Outlook OAuth in CLI context

**Business Validation Needed:**
1. **Pricing Research** - What would users actually pay for Production Pack? ($500? $1000? $2000?)
2. **Competitive Pricing** - Detailed analysis of EmailEngine pricing tiers
3. **Target Customer** - Who's the beachhead customer for MVP? (Indie devs? Small SaaS? Agencies?)
4. **Community Plugin Strategy** - How to bootstrap plugin ecosystem without cannibalizing commercial packs?

**Product Questions:**
1. **Thread Detection Algorithm** - What's the balance between accuracy and performance?
2. **Multi-Account Priority** - Should Core support multiple accounts or is single account enough for MVP?
3. **TUI vs Web UI Priority** - Which interface to build first after Core?

### Recommended Follow-up Techniques

**For next brainstorming sessions:**

1. **User Story Mapping** - Map out specific developer workflows to validate feature priorities
2. **Competitive Feature Matrix** - Detailed comparison: Mail Reactor vs EmailEngine vs Sendgrid
3. **Assumption Testing** - List and prioritize assumptions to validate (e.g., "developers want self-hosted email API")
4. **Pricing Strategy Workshop** - Explore different pricing models and positioning

**For technical planning:**
1. **Architecture Decision Records (ADRs)** - Document key decisions (plugin model, event sourcing, etc.)
2. **Threat Modeling** - Security analysis for handling email credentials, OAuth tokens
3. **Performance Benchmarking** - Define performance targets (emails/sec, latency, etc.)

### Questions That Emerged

**Strategic Questions:**
1. Is MCP truly simple enough to build in Core phase, or should it be deferred?
2. Should we validate demand (build MVP first) before investing in plugin architecture?
3. What's the minimum time between MVP and Production Pack to build revenue? (3 months? 6 months?)
4. Do we build TUI before or after commercial packs?

**Technical Questions:**
1. How to handle email credentials securely in stateless mode?
2. Can we truly avoid local storage, or will we hit performance walls?
3. What's the right balance between dogfooding (core features as plugins) and pragmatism (native code for performance)?
4. How to handle IMAP IDLE for real-time email notifications without webhooks?

**Business Questions:**
1. What's the conversion rate we need from free users to paid to be sustainable?
2. Should we offer SaaS hosting from day one, or focus on self-hosted first?
3. How to prevent someone from forking Core and adding "Production Pack" features themselves?
4. What's the right balance between features in Core vs Production Pack?

### Next Session Planning

**Suggested topics:**

1. **Technical Architecture Deep Dive** - Design plugin system, state model, event sourcing implementation
2. **Go-to-Market Strategy** - Launch plan, positioning, messaging, initial users
3. **Competitive Analysis** - Detailed EmailEngine teardown, feature comparison
4. **Product Requirements** - Write detailed specs for MVP endpoints
5. **Commercial Model Refinement** - Pricing, packaging, trial strategy

**Recommended timeframe:**

- **After MVP is built** (Week 3-4) - Review what worked/didn't work, adjust Core phase plan
- **Before Production Pack development** (Month 2-3) - Define Production Pack features based on user feedback
- **Before launch** (Month 2) - Finalize positioning, messaging, go-to-market strategy

**Preparation needed:**

- Build MVP to inform next discussions with real data
- Research MCP protocol thoroughly
- Analyze EmailEngine pricing and features in detail
- Talk to potential users (developers who might use Mail Reactor)
- Document technical architecture decisions made during MVP

---

## Session Summary

**Total Ideas Generated:** 50+ concrete features and architectural decisions

**Key Themes Identified:**
1. **Headless Email Client** - Clear mental model differentiates from "email API"
2. **MIT Core + Commercial Packs** - Sustainable open-source business model
3. **Stateless by default** - Email account as event source eliminates setup friction
4. **Plugin-first architecture** - Extensibility core to product strategy
5. **MCP integration** - LLM-native capability as launch differentiator
6. **Developer experience focus** - Zero-config, Stripe-quality tooling, beautiful TUI
7. **Distributed from day one** - Design for scale, deploy as standalone

**Techniques Used:**
- First Principles Thinking (15 min)
- Party Mode with 9 agents (45 min)
- What If Scenarios (20 min)
- SCAMPER Method (25 min)
- Resource Constraints (10 min)

**Session Duration:** ~2 hours

**Outcome:** Clear product vision, defined MVP, execution roadmap, and prioritized action plan

---

_Session facilitated using the BMAD CIS brainstorming framework_
