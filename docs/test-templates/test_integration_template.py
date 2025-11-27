"""
Integration Test Template for Mail Reactor

Copy this file to tests/integration/api/test_<endpoint>.py and customize.

Integration Test Characteristics:
- Moderate speed (~100ms per test)
- Use FastAPI TestClient (httpx AsyncClient)
- Local IMAP/SMTP test servers (Greenmail on localhost)
- Test API contracts and error handling
- 35% of total test budget

Note: Greenmail is a REAL server (not mocking) - it implements actual IMAP/SMTP 
protocols but runs locally with in-memory storage for fast resets.
"""

import pytest
from httpx import AsyncClient
from mailreactor.main import app


# =====================================================
# Section 1: Basic API Endpoint Test
# =====================================================

@pytest.mark.asyncio
async def test_endpoint_returns_success():
    """
    Test POST /endpoint returns 201 with valid payload.
    
    Pattern: FastAPI TestClient with async/await.
    All Mail Reactor API tests use httpx.AsyncClient.
    """
    # ARRANGE
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "email": "test@example.com",
            "name": "Test User",
        }
        
        # ACT
        response = await client.post("/endpoint", json=payload)
        
        # ASSERT
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"


# =====================================================
# Section 2: Real Mail Reactor Example (Accounts API)
# =====================================================

@pytest.mark.asyncio
async def test_add_account_success():
    """
    Test POST /accounts creates account with valid credentials.
    
    This uses local IMAP/SMTP test server (Greenmail on localhost:3143/3025).
    Not mocking - real protocol, just localhost instead of imap.gmail.com.
    """
    # ARRANGE
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "email": "test@localhost",
            "password": "test-password",
            "provider": "custom",
            "imap_host": "localhost",
            "imap_port": 3143,  # Greenmail IMAP port
            "smtp_host": "localhost",
            "smtp_port": 3025,  # Greenmail SMTP port
        }
        
        # ACT
        response = await client.post("/accounts", json=payload)
        
        # ASSERT
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@localhost"
        assert "password" not in data  # Never expose password in response
        assert "id" in data  # Account should have generated ID


@pytest.mark.asyncio
async def test_get_account_by_id():
    """
    Test GET /accounts/{id} returns account details.
    
    Pattern: Create resource first, then retrieve it.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Step 1: Create account
        create_payload = {
            "email": "test@localhost",
            "password": "test",
            "imap_host": "localhost",
            "imap_port": 3143,
        }
        create_response = await client.post("/accounts", json=create_payload)
        account_id = create_response.json()["id"]
        
        # Step 2: Retrieve account
        get_response = await client.get(f"/accounts/{account_id}")
        
        # Assert
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == account_id
        assert data["email"] == "test@localhost"


# =====================================================
# Section 3: Error Response Testing
# =====================================================

@pytest.mark.asyncio
async def test_endpoint_validation_error():
    """
    Test endpoint returns 422 for invalid payload.
    
    Pattern: Test Pydantic validation errors.
    FastAPI returns 422 for validation failures.
    """
    # ARRANGE
    async with AsyncClient(app=app, base_url="http://test") as client:
        invalid_payload = {
            "email": "not-an-email",  # Invalid email format
        }
        
        # ACT
        response = await client.post("/accounts", json=invalid_payload)
        
        # ASSERT
        assert response.status_code == 422
        error_detail = response.json()["detail"]
        # Pydantic validation errors include field location and message
        assert isinstance(error_detail, list)


@pytest.mark.asyncio
async def test_account_not_found():
    """
    Test GET /accounts/{id} returns 404 for non-existent account.
    
    Pattern: Test error handling for missing resources.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # ACT - Request non-existent account
        response = await client.get("/accounts/99999")
        
        # ASSERT
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_invalid_credentials():
    """
    Test POST /accounts returns 401 for invalid IMAP credentials.
    
    Pattern: Test authentication failures.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "email": "test@localhost",
            "password": "wrong-password",
            "imap_host": "localhost",
            "imap_port": 3143,
        }
        
        # ACT
        response = await client.post("/accounts", json=payload)
        
        # ASSERT
        assert response.status_code == 401
        assert "authentication" in response.json()["detail"].lower()


# =====================================================
# Section 4: Parametrized API Tests
# =====================================================

@pytest.mark.asyncio
@pytest.mark.parametrize("email,status", [
    ("valid@example.com", 201),  # Valid email
    ("", 422),                    # Empty email
    ("invalid-email", 422),       # Invalid format
    ("test@", 422),               # Incomplete email
])
async def test_email_validation(email, status):
    """
    Test email validation for various inputs.
    
    Pattern: Combine parametrize with async tests.
    Each tuple becomes one async test run.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "email": email,
            "password": "test",
            "imap_host": "localhost",
            "imap_port": 3143,
        }
        
        response = await client.post("/accounts", json=payload)
        assert response.status_code == status


# =====================================================
# Section 5: Using Test Server Fixtures (from conftest.py)
# =====================================================

@pytest.mark.asyncio
async def test_with_mock_imap_server(mock_imap):
    """
    Test using IMAP test server fixture.
    
    Pattern: Fixtures from tests/conftest.py provide pre-configured test servers.
    Note: 'mock_imap' is a fixture that returns a connected IMAPClient to localhost:3143.
    """
    # ARRANGE - Fixture provides connected IMAP client
    # mock_imap is already connected to Greenmail on localhost:3143
    
    # ACT
    folders = mock_imap.list_folders()
    
    # ASSERT
    assert isinstance(folders, list)
    # Greenmail auto-creates INBOX on login
    # assert any("INBOX" in str(folder) for folder in folders)


@pytest.mark.asyncio
async def test_send_email_integration(api_client):
    """
    Test email sending with local SMTP test server.
    
    Pattern: Use api_client fixture (FastAPI TestClient).
    """
    # ARRANGE
    # api_client fixture provides AsyncClient with app
    
    # First create account
    # account_response = await api_client.post("/accounts", json={...})
    # account_id = account_response.json()["id"]
    
    # ACT - Send email
    # send_response = await api_client.post(f"/accounts/{account_id}/send", json={
    #     "to": ["recipient@localhost"],
    #     "subject": "Test Email",
    #     "body": "Integration test email body",
    # })
    
    # ASSERT
    # assert send_response.status_code == 200
    
    # Placeholder
    assert True


# =====================================================
# Section 6: Testing Response Schemas
# =====================================================

@pytest.mark.asyncio
async def test_response_schema_validation():
    """
    Test API response matches expected schema.
    
    Pattern: Verify response structure and types.
    FastAPI + Pydantic ensure this, but good to test explicitly.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create account
        response = await client.post("/accounts", json={
            "email": "test@localhost",
            "password": "test",
            "imap_host": "localhost",
            "imap_port": 3143,
        })
        
        # Assert schema
        assert response.status_code == 201
        data = response.json()
        
        # Verify required fields
        assert "id" in data
        assert "email" in data
        assert "created_at" in data
        
        # Verify types
        assert isinstance(data["id"], (int, str))
        assert isinstance(data["email"], str)
        
        # Verify sensitive fields excluded
        assert "password" not in data


# =====================================================
# Section 7: Testing Async Operations
# =====================================================

@pytest.mark.asyncio
async def test_async_email_retrieval():
    """
    Test async email retrieval endpoint.
    
    Pattern: All Mail Reactor I/O is async.
    Integration tests must use @pytest.mark.asyncio.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Assume account exists (created in previous test or fixture)
        # account_id = 1
        
        # ACT - Retrieve messages (async IMAP operation)
        # response = await client.get(f"/accounts/{account_id}/messages")
        
        # ASSERT
        # assert response.status_code == 200
        # messages = response.json()
        # assert isinstance(messages, list)
        
        # Placeholder
        assert True


# =====================================================
# Section 8: Integration Test Tips
# =====================================================

"""
Integration Test Best Practices:

1. Start test servers before running tests
   cd tests && docker-compose -f docker-compose.test.yml up -d

2. Use localhost test servers (Greenmail)
   - IMAP: localhost:3143
   - SMTP: localhost:3025
   - Auto-creates accounts on first login

3. Always use @pytest.mark.asyncio for async tests
   - Mail Reactor is async-first
   - FastAPI endpoints are async
   - IMAP/SMTP operations use async executor pattern

4. Test API contracts, not implementation
   - Verify request/response schemas
   - Test error status codes
   - Check response headers

5. Keep tests isolated
   - Each test should work independently
   - Use transactions or cleanup fixtures
   - Don't rely on test execution order

6. Speed: ~100ms per test
   - Faster than E2E (no real Gmail/Outlook)
   - Slower than unit (real protocol, localhost connection)

7. Use fixtures for common setup
   - api_client (FastAPI TestClient)
   - mock_imap (IMAP client to localhost:3143)
   - mock_smtp (SMTP client to localhost:3025)
"""


# =====================================================
# Usage Instructions
# =====================================================

"""
How to use this template:

1. Start test servers
   cd tests
   docker-compose -f docker-compose.test.yml up -d

2. Copy template to tests/integration/api/test_<endpoint>.py
   Example: tests/integration/api/test_accounts.py

3. Replace examples with your endpoint tests
   - Import your FastAPI app
   - Define test payloads
   - Assert on response status and data

4. Run integration tests
   pytest tests/integration/api/test_accounts.py -v

5. Run with coverage
   pytest tests/integration/ --cov=src/mailreactor

6. Filter by marker
   pytest -m "not e2e"  # Run integration but not E2E

7. Stop test servers when done
   cd tests
   docker-compose -f docker-compose.test.yml down -v
"""
