# Course Correction Report: Epic 2 - Email Account Connection

**Date:** 2025-12-06
**Triggered By:** Story 2.1.2 - CLI Account Management with Encrypted Storage
**PM:** John
**Status:** Approved - Architecture Update Pending

---

## Executive Summary

Epic 2 has been redesigned from a multi-account REST API model to a simpler `mailreactor init` wizard with project-local YAML configuration. This change resolves UX elegance concerns, reduces implementation complexity, and aligns with Mail Reactor's "zero-configuration" positioning.

**Key Decision:** Single account per Mail Reactor instance, config file as source of truth, master password encryption at rest.

**Next Action:** Architect (Winston) to update `architecture.md` to reflect simplified storage model.

---

## Section 1: Understand the Trigger and Context

### 1.1 Triggering Story
**Story ID:** Story 2.1.2 - CLI Account Management with Encrypted Storage
**Description:** Encrypted TOML config file at `~/.config/mailreactor/config.toml` with hot-reload polling mechanism
**Status:** ✅ Done

### 1.2 Core Problem Definition
**Issue Type:** Strategic UX/architecture pivot

**Problem Statement:**
The current Epic 2 design (global config file at `~/.config/mailreactor/config.toml` with account management REST API) conflicts with Mail Reactor's "zero-configuration" positioning. The approach adds complexity (encryption, hot-reload, account API, runtime state management) that doesn't serve the MVP use case: self-hosted, single-user managing multiple email accounts.

**Status:** ✅ Done

### 1.3 Supporting Evidence
- PRD positioning: "Zero-configuration deployment that works in seconds"
- Architecture constraint: "Stateless design" vs persistent config file contradiction
- User concerns: Config file management, master passwords, file corruption risks
- UX friction: Three ways to manage accounts (CLI flag, CLI commands, REST API) creates confusion
- Deployment reality: Localhost-first (NFR-S3) makes REST API less valuable for MVP
**Status:** ✅ Done

---

## Section 2: Epic Impact Assessment

### 2.1 Current Epic Completion Status
**Can Epic 2 be completed as planned?** No
**Modifications needed:** Complete redesign around `mailreactor init` workflow
**Status:** ✅ Done

### 2.2 Epic-Level Changes Required
**Action:** Completely redefine Epic 2 scope

**Old Model:**
- Global config at `~/.config/mailreactor/config.toml`
- Multi-account runtime management via REST API
- Hot-reload polling (5-second file watching)
- StateManager with namespaced storage

**New Model:**
- Project-local `mailreactor.yaml` (like `docker-compose.yaml`)
- Single account per instance
- `mailreactor init` wizard for setup
- Master password encryption (PBKDF2 + Fernet)
- No account management REST API

**Stories Removed:**
- Story 2.1.2: CLI Account Management with Encrypted Storage
- Story 2.4: StateManager with account storage
- Story 2.5: Account Listing and Retrieval API
- Story 2.8: Account Removal API

**Stories Added:**
- Story 2.4: `mailreactor init` wizard
- Story 2.5: YAML config file operations with `!encrypted` tag
- Story 2.6: `mailreactor start` with master password decryption

**Status:** ✅ Done

### 2.3 Future Epics Impact
- **Epic 3 (Email Sending):** No impact - operates on single account from config
- **Epic 4 (Email Retrieval):** No impact - operates on single account from config
- **Epic 6 (IMAP-as-database):** Simplified - single account storage model is cleaner
- **Epic 5 (Authentication):** Reduced scope - no account management API to protect
**Status:** ✅ Done

### 2.4 Obsolete/New Epics
**Obsolete:** None (multi-account orchestration deferred to Phase 2)
**New Needed:** None for MVP
**Status:** ✅ Done

### 2.5 Epic Priority Changes
No resequencing needed - Epic 2 remains prerequisite for Epic 3/4
**Status:** ✅ Done

---

## Section 3: Artifact Conflict and Impact Analysis

### 3.1 PRD Conflicts
**Conflicts:**
- FR-003: "Add account via REST API" - being removed
- FR-009: "Retrieve list of accounts via API" - being removed
- FR-010: "Retrieve specific account details via API" - being removed

**Resolution Required:**
- Update PRD to reflect project-local config model
- Add FR for `mailreactor init` wizard
- Update FR-004: Change from "memory-only storage" to "encrypted file storage"

**MVP Impact:** MVP scope reduced (simpler), timeline potentially improved
**Status:** ✅ Done

**Action Owner:** PM (John) to update PRD

### 3.2 Architecture Document Conflicts
**Impacted Sections:**
- Storage Backend abstraction (namespaced keys) - simplified to single-account
- Dual-mode architecture - library mode simplified (no multi-account orchestration)
- StateManager module - removed entirely
- Account API endpoints - removed

**Resolution Required:**
- Remove StateManager and account storage abstraction sections
- Update dual-mode architecture description (single account per instance)
- Update deployment patterns to reflect config file approach
- Remove account management REST API documentation

**Status:** ⚠️ Action Needed

**Action Owner:** Architect (Winston) - **THIS IS YOUR TASK**
**File:** `/home/hcvst/dev/bmad/bmad-mailreactor/docs/architecture.md`

**Specific Changes Needed:**
1. Remove all references to `StorageBackend` with namespaced keys (`account:*`, `webhook:*`, `email:*`)
2. Update "Dual-Mode Architecture" section:
   - Clarify single account per instance in API mode
   - Update library mode examples (no multi-account orchestration)
3. Remove StateManager component description
4. Remove account management REST API endpoints from API documentation
5. Add project-local config file (`mailreactor.yaml`) architecture
6. Add encryption architecture (PBKDF2 + Fernet, master password)
7. Update deployment patterns (Docker, systemd) to use config file + env var

**Reference:** Revised Epic 2 Tech Spec at `/home/hcvst/dev/bmad/bmad-mailreactor/docs/sprint-artifacts/tech-spec-epic-2-REVISED.md`

### 3.3 UI/UX Specifications
**Impact:** CLI UX significantly simplified
- `mailreactor init` wizard replaces account management commands
- No REST API for account CRUD

**Resolution:** Document new CLI flows in architecture/PRD (already captured in revised Epic 2 spec)
**Status:** ✅ Done

### 3.4 Other Artifacts
- **Testing strategies:** Simpler (no API endpoint tests, no state management tests)
- **Documentation:** Rewrite account setup guide around `mailreactor init` (future task)
- **Deployment:** Simplified (Docker/systemd just need `mailreactor.yaml` + env var)
**Status:** ✅ Done

---

## Section 4: Path Forward Evaluation

### 4.1 Option 1: Direct Adjustment
**Approach:** Modify Epic 2 stories to support both config file AND REST API
**Viability:** ❌ Not viable
**Reasoning:** Maintains complexity, doesn't resolve UX elegance concern
**Effort:** High (two systems to maintain)
**Risk:** High (confusion between config file vs API as source of truth)
**Status:** ❌ Rejected

### 4.2 Option 2: Potential Rollback
**Approach:** Revert Story 2.1.2 work (if already implemented)
**Viability:** ⚠️ Not applicable
**Reasoning:** Story 2.1.2 not yet fully implemented based on validation report dates
**Effort:** Low (no rollback needed)
**Risk:** Low
**Status:** N/A

### 4.3 Option 3: PRD MVP Review (SELECTED)
**Approach:** Redefine Epic 2 around `mailreactor init` model, update PRD FRs
**Viability:** ✅ Viable - **SELECTED**
**MVP Impact:** MVP still achievable, actually simplified
**Deferred to Post-MVP:** Multi-account orchestration, account management API
**Effort:** Medium (rewrite Epic 2 spec, update PRD, update architecture.md)
**Risk:** Low (clearer mental model, less code to maintain)
**Status:** ✅ Approved by HC (Scrum Master)

**Rationale:**
1. **UX elegance:** `mailreactor init` aligns with developer mental models (like `git init`, `npm init`)
2. **Reduced complexity:** Eliminates REST API, StateManager, hot-reload, global config
3. **Faster implementation:** Fewer stories (6 vs 8), simpler architecture
4. **Better MVP fit:** Serves self-hosted, single-user use case perfectly
5. **Future-proof:** Multi-account via multiple instances (different ports) is acceptable for MVP, orchestration can come later

---

## Section 5: Sprint Change Proposal

### 5.1 Issue Summary
Epic 2's current design (global config file with account management REST API) introduces unnecessary complexity that conflicts with Mail Reactor's "zero-configuration" positioning. The `mailreactor init` model (project-local YAML config, wizard-driven setup, single account per instance) better serves the MVP use case while maintaining simplicity and elegance.
**Status:** ✅ Done

### 5.2 Epic and Artifact Adjustments

**Epic 2 Changes:**
- ✅ Rewrite technical specification around `mailreactor init` workflow (COMPLETED)
- ✅ Remove: Account management REST API, StateManager, hot-reload, CLI account commands
- ✅ Add: Init wizard, YAML config schema, master password encryption, config-driven startup
- ✅ Story count: 8 → 6 (reduced scope, faster implementation)

**PRD Updates Required:**
- ⚠️ Remove FR-003, FR-009, FR-010 (account REST API requirements)
- ⚠️ Add FR for `mailreactor init` wizard and YAML config
- ⚠️ Update FR-004 (encrypted file storage vs memory-only)

**Architecture Updates Required:**
- ⚠️ Remove StateManager and account storage abstraction
- ⚠️ Simplify dual-mode architecture (single account per instance)
- ⚠️ Update deployment patterns to reflect config file approach

**Status:** Partially Complete - Pending PRD and Architecture updates

### 5.3 Recommended Path
**Option 3: PRD MVP Review** - Redefine Epic 2 around `mailreactor init`
**Status:** ✅ Approved by Scrum Master (HC)

### 5.4 MVP Impact and Action Plan

**MVP Status:** ✅ Still achievable, timeline potentially improved

**High-Level Actions:**
1. ✅ Rewrite Epic 2 Technical Specification (PM - John) - **COMPLETED**
2. ⚠️ Update PRD to remove account API FRs (PM - John) - **PENDING**
3. ⚠️ Update Architecture document for simplified storage model (Architect - Winston) - **PENDING**
4. ⚠️ Review with team for approval (Scrum Master - HC) - **PENDING**
5. ⏳ Proceed with Epic 2 implementation using new spec (Dev team) - **BLOCKED ON ARCHITECTURE UPDATE**

**Dependencies:**
- ✅ Epic 1 complete (foundation)
- ✅ Epic 2 spec rewrite (COMPLETED - see tech-spec-epic-2-REVISED.md)
- ⚠️ Architecture.md update (PENDING - Winston)
- ⚠️ PRD update (PENDING - John)
- Epic 3/4 specs unchanged (operate on single account from config)

### 5.5 Agent Handoff Plan

**PM (John - current agent):**
- ✅ Complete Epic 2 Technical Specification rewrite
- ⚠️ Update PRD FRs (remove account API, add init wizard) - **NEXT TASK**
- ⏳ Present to HC for final approval

**Architect (Winston):** **← YOU ARE HERE**
- ⚠️ Update `architecture.md` to reflect simplified storage model
- ⚠️ Remove StateManager and account storage abstraction sections
- ⚠️ Update dual-mode architecture description
- ⚠️ Review Epic 2 spec for technical soundness
- **File to Update:** `/home/hcvst/dev/bmad/bmad-mailreactor/docs/architecture.md`
- **Reference:** `/home/hcvst/dev/bmad/bmad-mailreactor/docs/sprint-artifacts/tech-spec-epic-2-REVISED.md`

**Scrum Master (HC):**
- ⏳ Approve revised Epic 2 specification (pending architecture update)
- ⏳ Update sprint planning with new story breakdown
- ⏳ Coordinate Architect review of architecture.md

**Dev Team:**
- ⏳ Implement Epic 2 using revised specification (blocked on architecture update)
- ✅ No work lost (Story 2.1.2 not fully implemented yet)

**Status:** ✅ Done

---

## Section 6: Final Review and Handoff

### 6.1 Checklist Completion
- ✅ All sections addressed
- ✅ Analysis comprehensive and actionable
**Status:** ✅ Done

### 6.2 Proposal Accuracy
- ✅ Recommendations supported by analysis
- ✅ Proposal is specific and actionable
**Status:** ✅ Done

### 6.3 User Approval
**HC Approval:** ✅ Approved (2025-12-06)
- Redefine Epic 2 around `mailreactor init` model
- Remove account management REST API
- Update PRD/Architecture to reflect simpler design
- Proceed with implementation using revised tech spec
**Status:** ✅ Done

### 6.4 Next Steps and Handoff Plan
**Status:** ✅ Done

**Completed Actions:**
1. ✅ **Winston (Architect):** Update `architecture.md` - **COMPLETE**
2. ✅ **John (PM):** Update PRD FRs - **COMPLETE**
3. ✅ **HC (Scrum Master):** Final approval - **APPROVED 2025-12-06**

**Next Step:** Dev team to proceed with Epic 2 implementation using revised tech spec (`tech-spec-epic-2-REVISED.md`).

---

## Artifacts Produced

### Completed
1. ✅ **Epic 2 Technical Specification (Revised)**
   - Location: `/home/hcvst/dev/bmad/bmad-mailreactor/docs/sprint-artifacts/tech-spec-epic-2-REVISED.md`
   - Date: 2025-12-06
   - Status: Complete - Ready for implementation pending architecture update

2. ✅ **Course Correction Report (This Document)**
   - Location: `/home/hcvst/dev/bmad/bmad-mailreactor/docs/sprint-artifacts/course-correction-epic-2-2025-12-06.md`
   - Date: 2025-12-06
   - Status: Complete

### Completed (Updated 2025-12-06)
3. ✅ **Architecture Document Update**
   - Owner: Winston (Architect)
   - Target File: `/home/hcvst/dev/bmad/bmad-mailreactor/docs/architecture.md`
   - Status: **COMPLETE** (Commit: "ARC course change 2 (init subcomand)")
   - Changes: Removed StateManager, added project-local config, updated deployment patterns, added encryption architecture

4. ✅ **PRD Update**
   - Owner: John (PM)
   - Target File: `/home/hcvst/dev/bmad/bmad-mailreactor/docs/prd.md`
   - Status: **COMPLETE** (2025-12-06)
   - Changes: Updated FR-002, FR-003, FR-004, FR-009, FR-010, FR-034 to reflect `mailreactor init` workflow and encrypted config file model

---

## For Winston (Architect) - Specific Action Items

**Your Task:** Update `architecture.md` to align with revised Epic 2 design.

**File:** `/home/hcvst/dev/bmad/bmad-mailreactor/docs/architecture.md`

**Reference Material:**
- Revised Epic 2 Spec: `/home/hcvst/dev/bmad/bmad-mailreactor/docs/sprint-artifacts/tech-spec-epic-2-REVISED.md`
- Course Correction Report: This document

**Specific Changes Required:**

1. **Remove StateManager Component**
   - Delete all references to runtime state management with namespaced keys
   - Delete `StorageBackend` abstraction description
   - Remove account storage examples with `account:*`, `webhook:*`, `email:*` namespaces

2. **Update Dual-Mode Architecture Section**
   - API Mode: Clarify single account per instance model
   - Library Mode: Update examples to show config loading (not multi-account orchestration)
   - Add project-local config file explanation

3. **Add Configuration Architecture**
   - Project-local `mailreactor.yaml` file structure
   - Master password encryption (PBKDF2 + Fernet)
   - Custom `!encrypted` YAML tag
   - Config lifecycle (init → start → decrypt)

4. **Remove Account Management API**
   - Delete REST endpoint documentation for `POST /accounts`, `GET /accounts`, `DELETE /accounts`
   - Remove CLI account commands (`mailreactor account add/list/remove`)

5. **Update Deployment Patterns**
   - Docker: Mount `mailreactor.yaml` as volume, set `MAILREACTOR_PASSWORD` env var
   - Systemd: Set working directory, provide env var
   - Multi-account: Document multiple instances pattern (different directories/ports)

6. **Update Component Diagram** (if exists)
   - Remove StateManager box
   - Add Config File component
   - Add Encryption module

**Questions for Winston:**
- Are there other architecture sections impacted that I haven't identified?
- Do you need additional context from the Epic 2 spec?
- Timeline: When can you complete the architecture update?

---

## Summary for Scrum Master (HC)

**Course Correction Status:** ✅ Approved and In Progress

**What's Complete:**
- ✅ Epic 2 redesigned around `mailreactor init` model
- ✅ Technical specification rewritten (tech-spec-epic-2-REVISED.md)
- ✅ Course correction documented and approved

**What's Complete:**
- ✅ Architecture.md update (Winston - DONE)
- ✅ PRD update (John - DONE)
- ✅ Sprint status updated

**What's Complete:**
- ✅ Final approval received from HC (Scrum Master) - 2025-12-06
- ✅ Epic 2 REVISED approved for implementation

**Next Meeting Prep:**
- Share this document with Winston before architecture meeting
- Winston to update architecture.md
- Review cycle: Winston → John (PRD update) → HC (final approval) → Dev Team (implementation)

**Timeline Impact:**
- Epic 2 complexity reduced (6 stories vs 8)
- Implementation likely faster with simpler design
- No work lost (Story 2.1.2 not fully implemented yet)

---

**End of Course Correction Report**
