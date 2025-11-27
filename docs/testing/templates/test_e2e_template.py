"""
E2E Test Template for Mail Reactor

Copy this file to tests/e2e/test_<journey>.py and customize.

E2E Test Characteristics:
- Slow (~5s per test)
- Use real IMAP/SMTP servers (Greenmail or test accounts)
- Test critical user journeys end-to-end
- Happy paths and highest-risk scenarios only
- 15% of total test budget

Custom markers used:
- @pytest.mark.e2e - E2E test (can filter with: pytest -m e2e)
- @pytest.mark.slow - Test takes >5 seconds (skip in CI: pytest -m "not slow")
"""

import pytest
from httpx import AsyncClient
from mailreactor.main import app


# =====================================================
# Section 1: Complete User Journey
# =====================================================

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_complete_email_workflow():
    """
    E2E: Add account → send email → retrieve email.
    
    This tests the complete happy path from account setup to email retrieval.
    Tests multiple epics working together:
    - Epic 2: Account connection
    - Epic 3: Email sending
    - Epic 4: Email retrieval
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # ==========================================
        # Step 1: Add Account (Epic 2)
        # ==========================================
        add_account_response = await client.post("/accounts", json={
            "email": "test@localhost",
            "password": "test",
            "imap_host": "localhost",
            "imap_port": 3143,
            "smtp_host": "localhost",
            "smtp_port": 3025,
        })
        
        assert add_account_response.status_code == 201
        account_id = add_account_response.json()["id"]
        
        # ==========================================
        # Step 2: Send Email (Epic 3)
        # ==========================================
        send_response = await client.post(f"/accounts/{account_id}/send", json={
            "to": ["recipient@localhost"],
            "subject": "E2E Test Email",
            "body": "This is an end-to-end test email.",
            "from": "test@localhost",
        })
        
        assert send_response.status_code == 200
        
        # ==========================================
        # Step 3: Retrieve Emails (Epic 4)
        # ==========================================
        # Note: Email delivery might take a moment (async)
        # In production E2E tests, might need retry logic
        
        messages_response = await client.get(f"/accounts/{account_id}/messages")
        
        assert messages_response.status_code == 200
        messages = messages_response.json()
        
        # Verify email appears in list
        assert len(messages) > 0
        # In real test, would verify specific email by subject/sender
        # assert any(msg["subject"] == "E2E Test Email" for msg in messages)


# =====================================================
# Section 2: Critical Path - Gmail Account Setup
# =====================================================

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_gmail_account_auto_detection():
    """
    E2E: Add Gmail account with auto-detection.
    
    Critical path: Provider auto-detection (Story 2.1) + Connection validation (Story 2.4).
    High risk if this fails - most common use case.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # ARRANGE - Gmail email triggers auto-detection
        payload = {
            "email": "test@gmail.com",
            "password": "app-specific-password",
            # No imap_host/smtp_host - should auto-detect
        }
        
        # ACT
        response = await client.post("/accounts", json=payload)
        
        # ASSERT
        # In real E2E, this would connect to actual Gmail with test account
        # For template, expect failure (no real credentials)
        # assert response.status_code == 201
        # account = response.json()
        # assert account["provider"] == "gmail"
        # assert account["imap_host"] == "imap.gmail.com"


# =====================================================
# Section 3: Slow Test (Large Data Volume)
# =====================================================

@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.asyncio
async def test_sync_large_mailbox():
    """
    E2E: Sync account with 1000+ emails.
    
    This test validates performance under realistic load.
    Marked 'slow' to skip in fast CI runs.
    
    Run with: pytest -m "e2e and slow"
    Skip with: pytest -m "e2e and not slow"
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create account with pre-populated mailbox
        # (In real test, would use test account with known email count)
        
        # account_response = await client.post("/accounts", json={...})
        # account_id = account_response.json()["id"]
        
        # Retrieve all messages (should handle 1000+ efficiently)
        # messages_response = await client.get(
        #     f"/accounts/{account_id}/messages",
        #     params={"limit": 1000}
        # )
        
        # Assert performance
        # assert messages_response.status_code == 200
        # assert messages_response.elapsed.total_seconds() < 10  # Within NFR-P2
        
        # Placeholder
        assert True


# =====================================================
# Section 4: Error Recovery Path
# =====================================================

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_connection_retry_on_temporary_failure():
    """
    E2E: Verify connection retry logic for temporary failures.
    
    High-risk scenario: IMAP server temporarily unavailable.
    System should retry gracefully, not crash.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Simulate temporary failure by using invalid port
        # (In real test, might use network simulation tools)
        
        payload = {
            "email": "test@localhost",
            "password": "test",
            "imap_host": "localhost",
            "imap_port": 9999,  # No server listening
        }
        
        response = await client.post("/accounts", json=payload)
        
        # Should return clear error, not crash
        assert response.status_code in [401, 503]  # Auth failure or service unavailable
        assert "connection" in response.json()["detail"].lower()


# =====================================================
# Section 5: Multi-Account Scenario
# =====================================================

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_multiple_accounts_isolation():
    """
    E2E: Add multiple accounts and verify isolation.
    
    Critical: Each account's emails should be isolated.
    Emails from account A should not appear in account B.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create Account A
        account_a_response = await client.post("/accounts", json={
            "email": "accounta@localhost",
            "password": "test",
            "imap_host": "localhost",
            "imap_port": 3143,
        })
        account_a_id = account_a_response.json()["id"]
        
        # Create Account B
        account_b_response = await client.post("/accounts", json={
            "email": "accountb@localhost",
            "password": "test",
            "imap_host": "localhost",
            "imap_port": 3143,
        })
        account_b_id = account_b_response.json()["id"]
        
        # Send email from Account A
        await client.post(f"/accounts/{account_a_id}/send", json={
            "to": ["accounta@localhost"],
            "subject": "Account A Email",
            "body": "This belongs to Account A",
        })
        
        # Retrieve emails for Account B
        account_b_messages = await client.get(f"/accounts/{account_b_id}/messages")
        
        # Assert Account B does NOT see Account A's emails
        messages = account_b_messages.json()
        # assert not any(msg["subject"] == "Account A Email" for msg in messages)


# =====================================================
# Section 6: Cleanup Pattern
# =====================================================

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_with_automatic_cleanup():
    """
    E2E: Test with cleanup to avoid polluting test environment.
    
    Pattern: Use try/finally to ensure cleanup even if test fails.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        account_id = None
        
        try:
            # Create test account
            response = await client.post("/accounts", json={
                "email": "cleanup-test@localhost",
                "password": "test",
                "imap_host": "localhost",
                "imap_port": 3143,
            })
            account_id = response.json()["id"]
            
            # Run test operations
            messages_response = await client.get(f"/accounts/{account_id}/messages")
            assert messages_response.status_code == 200
            
        finally:
            # Cleanup: Remove test account
            if account_id:
                await client.delete(f"/accounts/{account_id}")


# =====================================================
# Section 7: Security E2E Test
# =====================================================

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_credentials_never_logged():
    """
    E2E: Verify credentials never appear in logs (NFR-S1).
    
    Critical security test: Passwords should never be logged or exposed.
    """
    import logging
    from io import StringIO
    
    # Capture logs
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    logging.root.addHandler(handler)
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create account with known password
        test_password = "super-secret-password-123"
        
        response = await client.post("/accounts", json={
            "email": "security-test@localhost",
            "password": test_password,
            "imap_host": "localhost",
            "imap_port": 3143,
        })
        
        # Check logs for password leak
        logs = log_stream.getvalue()
        
        # Assert password never appears in logs
        assert test_password not in logs
        assert "super-secret" not in logs
        
        # Password should not be in response either
        assert "password" not in response.json()


# =====================================================
# Section 8: Performance E2E Test (NFR Validation)
# =====================================================

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_startup_time_under_3_seconds():
    """
    E2E: Verify cold start time meets NFR-P1 (<3 seconds).
    
    Non-functional requirement validation.
    """
    import time
    
    # Measure cold start time
    start = time.perf_counter()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Health check endpoint should respond quickly
        response = await client.get("/health")
        
        elapsed = time.perf_counter() - start
        
        # Assert NFR-P1: Cold start <3 seconds
        assert elapsed < 3.0, f"Startup took {elapsed:.2f}s (NFR-P1 requires <3s)"
        assert response.status_code == 200


# =====================================================
# E2E Test Best Practices
# =====================================================

"""
E2E Testing Guidelines:

1. Test critical happy paths only
   - Most common user journeys
   - Highest-risk scenarios
   - Don't test every edge case (that's for unit/integration)

2. Use custom markers
   @pytest.mark.e2e - Filter with: pytest -m e2e
   @pytest.mark.slow - Skip slow tests: pytest -m "not slow"

3. Keep E2E tests independent
   - Each test should create its own test data
   - Clean up after test completes
   - Don't depend on test execution order

4. Accept slower runtime
   - E2E tests are naturally slower (~5s each)
   - That's OK - they test the whole system
   - Run less frequently than unit/integration tests

5. Use real servers when possible
   - Greenmail for localhost testing
   - Test Gmail/Outlook accounts for production validation
   - Avoid mocking in E2E (defeats the purpose)

6. Monitor for flakiness
   - E2E tests can be flaky (network, timing)
   - Use retries for known-async operations
   - Investigate and fix flaky tests immediately

7. Validate NFRs
   - Performance (startup time, API latency)
   - Security (credential handling)
   - Reliability (error recovery)
"""


# =====================================================
# Usage Instructions
# =====================================================

"""
How to use this template:

1. Start test servers
   cd tests
   docker-compose -f docker-compose.test.yml up -d

2. Copy template to tests/e2e/test_<journey>.py
   Example: tests/e2e/test_email_workflows.py

3. Define critical user journeys
   - Add account → send email → retrieve email
   - Multi-account scenarios
   - Error recovery paths

4. Run E2E tests
   pytest tests/e2e/ -v

5. Run only fast E2E tests
   pytest -m "e2e and not slow"

6. Run all E2E including slow tests
   pytest -m e2e

7. Run with verbose output
   pytest tests/e2e/test_email_workflows.py -v -s

8. Stop test servers
   cd tests
   docker-compose -f docker-compose.test.yml down -v

9. Schedule E2E tests appropriately
   - Fast E2E: Every commit (CI)
   - Slow E2E: Nightly builds or pre-release
"""
