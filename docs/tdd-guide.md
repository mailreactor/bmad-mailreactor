# Mail Reactor TDD Guide

**Date:** 2025-11-27  
**Author:** Murat (TEA - Test Architect)  
**Status:** Team Standard - MANDATORY for All Development  
**Project:** Mail Reactor MVP

---

## Overview

This guide defines the **Test-Driven Development (TDD) workflow** for Mail Reactor. TDD is **MANDATORY** for all production code - no exceptions for MVP.

**Why TDD is non-negotiable:**

- ✅ **Design feedback:** Tests reveal API awkwardness before implementation locks it in
- ✅ **Regression prevention:** Every feature has tests from Day 1
- ✅ **Living documentation:** Tests show how code actually works
- ✅ **Faster debugging:** Failing tests pinpoint issues immediately
- ✅ **Confidence:** Refactor without fear of breaking features

---

## The Red-Green-Refactor Cycle

Every feature follows this strict 3-step **micro-cycle**:

```
RED → Write smallest failing test
  ↓
GREEN → Minimal code to pass (hardcode if needed)
  ↓
RED → Add next failing test
  ↓
GREEN → Generalize to pass both tests
  ↓
RED → Add another test
  ↓
GREEN → Extend logic
  ↓
[Continue micro-cycles until feature complete]
  ↓
REFACTOR → Improve code quality (all tests stay green)
```

**Critical:** Each RED → GREEN cycle should take **seconds to minutes**, not hours. If you're writing code for >10 minutes without running tests, you've skipped RED.

---

## TDD Micro-Cycles: The Baby Steps Philosophy

**The smaller your RED → GREEN cycles, the faster you move.**

### Why Micro-Cycles Matter

**Traditional (Wrong) Approach:**
```
RED: Write complete test suite (15 minutes)
  ↓
GREEN: Implement full feature (60 minutes)
  ↓
Debug: Why did I break 3 tests? (30 minutes)
```
**Total:** 105 minutes, high cognitive load, risky

**Micro-Cycle (Correct) Approach:**
```
RED: Import fails (write 3 lines) → GREEN: Create file (write 2 lines) [20 seconds]
RED: Class missing (write 5 lines) → GREEN: Add class (write 2 lines) [20 seconds]
RED: Method missing (write 6 lines) → GREEN: Add stub (write 3 lines) [30 seconds]
RED: First assertion (write 8 lines) → GREEN: Hardcode return (write 4 lines) [40 seconds]
RED: Second assertion (write 8 lines) → GREEN: Add if/elif (write 6 lines) [50 seconds]
[Repeat 10-20 more cycles...]
```
**Total:** 60 minutes, low cognitive load, safe

### The "No Test Should Force You to Write >10 Lines" Rule

If making a test pass requires writing >10 lines of production code, **the test is too big**. Break it down.

**❌ Too Big:**
```python
def test_provider_detection():
    """Test complete provider detection."""
    # This test forces you to implement:
    # - ProviderSettings class (5 fields)
    # - ProviderDetector class
    # - detect() method
    # - Gmail logic
    # - Outlook logic
    # - Error handling
    # = 50+ lines of code before test passes!
```

**✅ Right Size:**
```python
def test_provider_settings_has_imap_host():
    """ProviderSettings should store imap_host."""
    settings = ProviderSettings(imap_host="imap.gmail.com")
    assert settings.imap_host == "imap.gmail.com"
    # Forces you to write: class + __init__ + one field = 4 lines
```

### Micro-Cycle Example: Real TDD Session

Here's what a **real 15-minute TDD session** looks like:

### Step 1: RED - Write Smallest Possible Failing Test

**Before writing ANY production code**, write the **smallest test** that will fail.

#### Micro-Cycle 1: Import Fails

```python
# tests/unit/core/test_provider_detector.py
import pytest
from mailreactor.core.provider_detector import ProviderDetector


def test_provider_detector_exists():
    """ProviderDetector class should exist."""
    detector = ProviderDetector()
    assert detector is not None
```

**Run test:**
```bash
pytest tests/unit/core/test_provider_detector.py::test_provider_detector_exists -v
```

**Expected result:** ❌ **FAILS** 
```
ImportError: cannot import name 'ProviderDetector' from 'mailreactor.core.provider_detector' 
(module not found)
```

---

### Step 2: GREEN - Write Minimal Code to Fix Import

**Now** create the **minimum code** to fix this specific failure.

```python
# src/mailreactor/core/provider_detector.py
class ProviderDetector:
    """Detect email provider settings from email address."""
    pass
```

**Run test again:**
```bash
pytest tests/unit/core/test_provider_detector.py::test_provider_detector_exists -v
```

**Result:** ✅ **PASSES**

---

### Micro-Cycle 2: Add detect() Method Test

Now add **one new assertion** that will fail:

```python
# tests/unit/core/test_provider_detector.py
import pytest
from mailreactor.core.provider_detector import ProviderDetector


def test_provider_detector_exists():
    """ProviderDetector class should exist."""
    detector = ProviderDetector()
    assert detector is not None


def test_detect_method_exists():
    """ProviderDetector should have detect() method."""
    detector = ProviderDetector()
    email = "user@gmail.com"
    
    # This will fail - no detect() method yet
    result = detector.detect(email)
    assert result is not None
```

**Run test:**
```bash
pytest tests/unit/core/test_provider_detector.py::test_detect_method_exists -v
```

**Result:** ❌ **FAILS**
```
AttributeError: 'ProviderDetector' object has no attribute 'detect'
```

**GREEN - Add Empty Method:**

```python
# src/mailreactor/core/provider_detector.py
class ProviderDetector:
    """Detect email provider settings from email address."""
    
    def detect(self, email: str):
        """Auto-detect provider settings from email domain."""
        return None  # Minimal - just make test pass
```

**Run test:**
```bash
pytest tests/unit/core/test_provider_detector.py::test_detect_method_exists -v
```

**Result:** ✅ **PASSES** (returns None, which is not None... wait, this test is wrong)

**Fix test to be more specific:**

```python
def test_detect_method_exists():
    """ProviderDetector should have detect() method that returns settings."""
    detector = ProviderDetector()
    email = "user@gmail.com"
    
    result = detector.detect(email)
    assert result is not None
    assert hasattr(result, 'imap_host')  # Now it will fail!
```

**Result:** ❌ **FAILS** (None has no attribute 'imap_host')

---

### Micro-Cycle 3: Return ProviderSettings Object

**RED - Add Gmail Detection Test:**

```python
# tests/unit/core/test_provider_detector.py
import pytest
from mailreactor.core.provider_detector import ProviderDetector


def test_gmail_imap_host():
    """Gmail detection should return correct IMAP host."""
    detector = ProviderDetector()
    email = "user@gmail.com"
    
    settings = detector.detect(email)
    
    # Test ONE thing at a time
    assert settings.imap_host == "imap.gmail.com"
```

**Run test:**
```bash
pytest tests/unit/core/test_provider_detector.py::test_gmail_imap_host -v
```

**Result:** ❌ **FAILS** (ProviderSettings doesn't exist, or returns None)

**GREEN - Hardcode Gmail Settings:**

```python
# src/mailreactor/core/provider_detector.py
class ProviderSettings:
    """IMAP/SMTP settings for email provider."""
    
    def __init__(self, imap_host: str):
        self.imap_host = imap_host


class ProviderDetector:
    """Detect email provider settings from email address."""
    
    def detect(self, email: str) -> ProviderSettings:
        """Auto-detect provider settings from email domain."""
        # Hardcode to pass test - we'll generalize later
        return ProviderSettings(imap_host="imap.gmail.com")
```

**Run test:**
```bash
pytest tests/unit/core/test_provider_detector.py::test_gmail_imap_host -v
```

**Result:** ✅ **PASSES**

---

### Micro-Cycle 4: Add IMAP Port Test

**RED - Test IMAP Port:**

```python
def test_gmail_imap_port():
    """Gmail detection should return correct IMAP port."""
    detector = ProviderDetector()
    email = "user@gmail.com"
    
    settings = detector.detect(email)
    
    assert settings.imap_port == 993
```

**Result:** ❌ **FAILS** (AttributeError: 'ProviderSettings' object has no attribute 'imap_port')

**GREEN - Add imap_port:**

```python
# src/mailreactor/core/provider_detector.py
class ProviderSettings:
    """IMAP/SMTP settings for email provider."""
    
    def __init__(self, imap_host: str, imap_port: int):
        self.imap_host = imap_host
        self.imap_port = imap_port


class ProviderDetector:
    """Detect email provider settings from email address."""
    
    def detect(self, email: str) -> ProviderSettings:
        """Auto-detect provider settings from email domain."""
        return ProviderSettings(imap_host="imap.gmail.com", imap_port=993)
```

**Result:** ✅ **PASSES**

---

### Micro-Cycle 5: Add Outlook Test (Forces Generalization)

**RED - Test Outlook Detection:**

```python
def test_outlook_imap_host():
    """Outlook detection should return correct IMAP host."""
    detector = ProviderDetector()
    email = "user@outlook.com"
    
    settings = detector.detect(email)
    
    assert settings.imap_host == "outlook.office365.com"
```

**Result:** ❌ **FAILS** (Returns "imap.gmail.com" for Outlook!)

**GREEN - Add Domain Logic:**

```python
# src/mailreactor/core/provider_detector.py
class ProviderSettings:
    """IMAP/SMTP settings for email provider."""
    
    def __init__(self, imap_host: str, imap_port: int):
        self.imap_host = imap_host
        self.imap_port = imap_port


class ProviderDetector:
    """Detect email provider settings from email address."""
    
    def detect(self, email: str) -> ProviderSettings:
        """Auto-detect provider settings from email domain."""
        # NOW we need to check the domain
        if "@gmail.com" in email:
            return ProviderSettings(imap_host="imap.gmail.com", imap_port=993)
        elif "@outlook.com" in email:
            return ProviderSettings(imap_host="outlook.office365.com", imap_port=993)
        else:
            # Don't handle unknown yet - no test for it
            return ProviderSettings(imap_host="unknown", imap_port=0)
```

**Result:** ✅ **PASSES**

---

### Key Insight: Tiny Steps

Notice the difference:

**❌ My Original (Wrong):** 
- RED: Write 3 complete tests (Gmail, Outlook, unknown)
- GREEN: Implement full solution
- Result: RED → GREEN (big jump)

**✅ Your Approach (Correct):**
- RED: Import fails → GREEN: Create file
- RED: Class missing → GREEN: Add class
- RED: Method missing → GREEN: Add method stub
- RED: Gmail imap_host → GREEN: Hardcode "imap.gmail.com"
- RED: Gmail imap_port → GREEN: Add port field
- RED: Outlook imap_host → GREEN: Add if/elif logic
- Result: RED → GREEN → RED → GREEN → RED → GREEN (micro-cycles)

**Each cycle is seconds long, not minutes.**

---

### Step 3: REFACTOR - Improve Code Quality (After Multiple Micro-Cycles)

**After several RED → GREEN cycles**, you'll have:
- ✅ All required fields in ProviderSettings (imap_host, imap_port, imap_ssl, smtp_host, smtp_port, smtp_starttls)
- ✅ Detection logic for Gmail, Outlook, Yahoo
- ✅ Error handling for unknown providers

**Now** refactor while keeping tests green. Use Pydantic, extract logic, add type hints.

```python
# src/mailreactor/core/provider_detector.py (refactored)
from pydantic import BaseModel
from typing import Dict
import yaml
from pathlib import Path


class ProviderSettings(BaseModel):
    """IMAP/SMTP settings for email provider."""
    
    imap_host: str
    imap_port: int
    imap_ssl: bool
    smtp_host: str
    smtp_port: int
    smtp_starttls: bool


class ProviderDetector:
    """Detect email provider settings from email address."""
    
    def __init__(self, providers_file: Path | None = None):
        """Initialize with provider configurations."""
        if providers_file is None:
            # Default to packaged providers.yaml
            providers_file = Path(__file__).parent.parent / "utils" / "providers.yaml"
        
        self.providers = self._load_providers(providers_file)
    
    def _load_providers(self, path: Path) -> Dict[str, ProviderSettings]:
        """Load provider configurations from YAML."""
        with open(path) as f:
            data = yaml.safe_load(f)
        
        return {
            domain: ProviderSettings(**settings)
            for domain, settings in data.items()
        }
    
    def detect(self, email: str) -> ProviderSettings:
        """Auto-detect provider settings from email domain."""
        # Extract domain from email
        if "@" not in email:
            raise ValueError(f"Invalid email address: {email}")
        
        domain = email.split("@")[1].lower()
        
        # Check if we have settings for this domain
        if domain in self.providers:
            return self.providers[domain]
        
        # Unknown provider
        raise ValueError(
            f"Unknown provider for email: {email}. "
            f"Use manual configuration or add to providers.yaml"
        )
```

**Run tests again:**
```bash
pytest tests/unit/core/test_provider_detector.py -v
```

**Result:** ✅ **Still PASSES** (refactoring didn't break anything!)

---

## Test Organization

Mail Reactor uses a **3-tier testing strategy** based on test design document recommendations:

### Directory Structure

```
tests/
├── __init__.py
├── conftest.py                  # Shared pytest fixtures
├── templates/                   # Test templates (from Task #2.2)
│   ├── test_unit_template.py
│   ├── test_integration_template.py
│   └── test_e2e_template.py
├── unit/                        # 50% of test budget
│   ├── __init__.py
│   ├── core/
│   │   ├── test_provider_detector.py
│   │   ├── test_message_parser.py
│   │   └── test_state_manager.py
│   └── models/
│       ├── test_account_models.py
│       └── test_message_models.py
├── integration/                 # 35% of test budget
│   ├── __init__.py
│   ├── api/
│   │   ├── test_accounts_api.py
│   │   ├── test_messages_api.py
│   │   └── test_send_api.py
│   └── core/
│       ├── test_imap_client.py   # With mock IMAP server
│       └── test_smtp_client.py   # With mock SMTP server
├── e2e/                         # 15% of test budget
│   ├── __init__.py
│   └── test_critical_paths.py   # Happy path scenarios only
├── performance/                 # NFR validation
│   ├── __init__.py
│   └── test_startup_time.py
└── security/                    # NFR validation
    ├── __init__.py
    └── test_credential_leaks.py
```

### Test Distribution (from Test Design)

- **Unit Tests (50%):** Pure Python logic, no network/I/O, <1ms per test
- **Integration Tests (35%):** API endpoints with mock IMAP/SMTP, ~100ms per test
- **E2E Tests (15%):** Critical paths with real servers, ~5s per test

---

## Unit Tests (50% of test budget)

**Purpose:** Test business logic in isolation, no network calls.

**Characteristics:**
- ✅ Fast (<1ms per test)
- ✅ No external dependencies
- ✅ Mock all I/O (IMAP, SMTP, file system)
- ✅ Test one function/class per file

### Unit Test Template

```python
# tests/unit/core/test_example.py
import pytest
from mailreactor.core.example import YourClass


class TestYourClass:
    """Test suite for YourClass."""

    def test_basic_functionality(self):
        """Test basic functionality works as expected."""
        # ARRANGE
        instance = YourClass()
        input_data = "example"
        
        # ACT
        result = instance.process(input_data)
        
        # ASSERT
        assert result == "expected_output"


    @pytest.mark.parametrize("input_val,expected", [
        ("input1", "output1"),
        ("input2", "output2"),
        ("edge_case", "special_output"),
    ])
    def test_parametrized(self, input_val, expected):
        """Test multiple scenarios with parametrization."""
        # ARRANGE
        instance = YourClass()
        
        # ACT
        result = instance.process(input_val)
        
        # ASSERT
        assert result == expected


    def test_error_handling(self):
        """Test error handling for invalid input."""
        # ARRANGE
        instance = YourClass()
        invalid_input = None
        
        # ACT & ASSERT
        with pytest.raises(ValueError) as exc_info:
            instance.process(invalid_input)
        
        assert "cannot be None" in str(exc_info.value)
```

### Example: Unit Test with Mocking

```python
# tests/unit/core/test_imap_client.py
import pytest
from unittest.mock import Mock, patch
from mailreactor.core.imap_client import AsyncIMAPClient


class TestAsyncIMAPClient:
    """Test AsyncIMAPClient with mocked IMAPClient."""

    @pytest.mark.asyncio
    async def test_list_folders_with_mock(self):
        """Test list_folders without real IMAP connection."""
        # ARRANGE
        mock_imap = Mock()
        mock_imap.list_folders.return_value = [
            (b'\\HasNoChildren', b'/', 'INBOX'),
            (b'\\HasNoChildren', b'/', 'Sent'),
        ]
        
        with patch('mailreactor.core.imap_client.IMAPClient', return_value=mock_imap):
            client = AsyncIMAPClient(host="localhost", port=143)
            await client.connect()
        
        # ACT
        folders = await client.list_folders()
        
        # ASSERT
        assert len(folders) == 2
        assert "INBOX" in folders
        assert "Sent" in folders
```

---

## Integration Tests (35% of test budget)

**Purpose:** Test API endpoints with mock IMAP/SMTP servers.

**Characteristics:**
- ✅ Moderate speed (~100ms per test)
- ✅ Use FastAPI TestClient (httpx)
- ✅ Mock IMAP/SMTP with Greenmail or fake servers
- ✅ Test API contracts and error handling

### Integration Test Template

```python
# tests/integration/api/test_accounts_api.py
import pytest
from httpx import AsyncClient
from mailreactor.main import app


@pytest.mark.asyncio
async def test_add_account_success(mock_imap_server):
    """Test POST /accounts creates account with valid credentials."""
    # ARRANGE
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "email": "test@example.com",
            "password": "secure-password",
            "provider": "custom",
            "imap_host": "localhost",
            "imap_port": 3143,
            "smtp_host": "localhost",
            "smtp_port": 3025,
        }
        
        # ACT
        response = await client.post("/accounts", json=payload)
        
        # ASSERT
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "password" not in data  # Never expose password in response


@pytest.mark.asyncio
async def test_add_account_invalid_credentials(mock_imap_server):
    """Test POST /accounts returns 401 for invalid credentials."""
    # ARRANGE
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "email": "test@example.com",
            "password": "wrong-password",
            "imap_host": "localhost",
            "imap_port": 3143,
        }
        
        # ACT
        response = await client.post("/accounts", json=payload)
        
        # ASSERT
        assert response.status_code == 401
        assert "authentication failed" in response.json()["detail"].lower()
```

### Using Mock Server Fixtures

```python
# tests/conftest.py
import pytest
from imapclient import IMAPClient
import smtplib


@pytest.fixture(scope="session")
def mock_imap_host():
    """Mock IMAP server host and port."""
    return "localhost", 3143


@pytest.fixture(scope="session")
def mock_smtp_host():
    """Mock SMTP server host and port."""
    return "localhost", 3025


@pytest.fixture
def mock_imap(mock_imap_host):
    """IMAP client connected to mock server."""
    host, port = mock_imap_host
    client = IMAPClient(host, port, ssl=False)
    client.login("test@localhost", "test")
    yield client
    client.logout()


@pytest.fixture
def mock_smtp(mock_smtp_host):
    """SMTP connection to mock server."""
    host, port = mock_smtp_host
    smtp = smtplib.SMTP(host, port)
    yield smtp
    smtp.quit()


@pytest.fixture
async def api_client():
    """FastAPI test client."""
    from httpx import AsyncClient
    from mailreactor.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

---

## E2E Tests (15% of test budget)

**Purpose:** Test critical user journeys end-to-end.

**Characteristics:**
- ✅ Slow (~5s per test)
- ✅ Use real IMAP/SMTP servers (Greenmail)
- ✅ Happy paths only (not exhaustive)
- ✅ Test highest-risk scenarios

### E2E Test Template

```python
# tests/e2e/test_critical_paths.py
import pytest
from httpx import AsyncClient
from mailreactor.main import app


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_full_email_workflow():
    """
    E2E: Add Gmail account → send email → retrieve email.
    
    This tests the complete happy path from account setup to email retrieval.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Step 1: Add account
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
        
        # Step 2: Send email
        send_response = await client.post(f"/accounts/{account_id}/send", json={
            "to": ["recipient@localhost"],
            "subject": "Test Email",
            "body": "This is a test email body.",
        })
        assert send_response.status_code == 200
        
        # Step 3: Retrieve emails
        messages_response = await client.get(f"/accounts/{account_id}/messages")
        assert messages_response.status_code == 200
        messages = messages_response.json()
        
        # Step 4: Verify email appears in list
        assert len(messages) > 0
        # Note: In real E2E test, might need to wait/retry for email to appear
```

---

## Async Testing with pytest-asyncio

Mail Reactor is async-first (FastAPI + asyncio). Use `pytest-asyncio` for async tests.

### Configuration

```python
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"  # Automatically detect async tests
```

### Async Test Pattern

```python
import pytest


@pytest.mark.asyncio
async def test_async_function():
    """Test async functions with pytest-asyncio."""
    # ARRANGE
    from mailreactor.core.imap_client import AsyncIMAPClient
    client = AsyncIMAPClient(host="localhost", port=3143)
    
    # ACT
    await client.connect()
    folders = await client.list_folders()
    
    # ASSERT
    assert "INBOX" in folders
    
    # CLEANUP
    await client.disconnect()
```

### Async Fixtures

```python
@pytest.fixture
async def imap_client():
    """Async fixture for IMAP client."""
    from mailreactor.core.imap_client import AsyncIMAPClient
    client = AsyncIMAPClient(host="localhost", port=3143)
    await client.connect()
    
    yield client
    
    await client.disconnect()
```

---

## Mocking Strategies for IMAP/SMTP

### Strategy 1: Mock Library (Unit Tests)

Use `unittest.mock` to mock IMAPClient/aiosmtplib:

```python
from unittest.mock import Mock, patch


def test_with_mocked_imap():
    """Mock IMAPClient for unit tests."""
    mock_imap = Mock()
    mock_imap.search.return_value = [1, 2, 3]
    
    with patch('mailreactor.core.imap_client.IMAPClient', return_value=mock_imap):
        # Your test code here
        pass
```

### Strategy 2: Mock Server (Integration Tests)

Use Greenmail or fake-imap-server for integration tests:

```bash
# Start Greenmail in Docker (from Sprint 0 Task #3)
cd tests
docker-compose -f docker-compose.test.yml up -d
```

### Strategy 3: Real Server (E2E Tests)

Use Greenmail or self-hosted Dovecot for E2E tests:

```python
@pytest.fixture(scope="session")
def real_imap_server():
    """Real IMAP server for E2E tests."""
    # Greenmail auto-creates accounts on first login
    return {
        "host": "localhost",
        "port": 3143,
        "email": "test@localhost",
        "password": "test",
    }
```

---

## Coverage Requirements

**Minimum coverage:** 80% (enforced by pre-commit hook)  
**Target coverage:** 85%+

### Running Coverage Locally

```bash
# Run tests with coverage report
pytest --cov=src/mailreactor --cov-report=html --cov-report=term

# Open HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Coverage Enforcement

Pre-commit hook fails if coverage <80%:

```yaml
# .pre-commit-config.yaml (from Task #2.3)
- repo: local
  hooks:
    - id: pytest-coverage
      name: pytest with coverage
      entry: pytest
      args: [--cov=src/mailreactor, --cov-fail-under=80]
      language: system
      pass_filenames: false
      always_run: true
```

---

## Best Practices

### 1. Arrange-Act-Assert Pattern

Always structure tests with clear sections:

```python
def test_example():
    # ARRANGE - Set up test data
    input_data = "test"
    
    # ACT - Execute the code under test
    result = function_under_test(input_data)
    
    # ASSERT - Verify the outcome
    assert result == "expected"
```

### 2. Test One Thing Per Test

```python
# ❌ BAD: Test does too much
def test_provider_detector():
    assert detector.detect("user@gmail.com").imap_host == "imap.gmail.com"
    assert detector.detect("user@outlook.com").imap_host == "outlook.office365.com"
    assert detector.detect("user@yahoo.com").imap_host == "imap.mail.yahoo.com"

# ✅ GOOD: Separate tests for each provider
def test_gmail_detection():
    assert detector.detect("user@gmail.com").imap_host == "imap.gmail.com"

def test_outlook_detection():
    assert detector.detect("user@outlook.com").imap_host == "outlook.office365.com"

def test_yahoo_detection():
    assert detector.detect("user@yahoo.com").imap_host == "imap.mail.yahoo.com"
```

### 3. Use Descriptive Test Names

```python
# ❌ BAD: Vague name
def test_detector():
    pass

# ✅ GOOD: Clear intent
def test_gmail_detection_from_email():
    """Given Gmail email address, auto-detect IMAP/SMTP settings."""
    pass
```

### 4. Parametrize Similar Tests

```python
@pytest.mark.parametrize("email,expected_host", [
    ("user@gmail.com", "imap.gmail.com"),
    ("user@outlook.com", "outlook.office365.com"),
    ("user@yahoo.com", "imap.mail.yahoo.com"),
])
def test_provider_detection(email, expected_host):
    """Test provider detection for common providers."""
    settings = detector.detect(email)
    assert settings.imap_host == expected_host
```

### 5. Never Commit Secrets in Tests

```python
# ❌ BAD: Real credentials
def test_gmail_connection():
    client = IMAPClient("imap.gmail.com")
    client.login("myrealemail@gmail.com", "my-real-password")  # NEVER!

# ✅ GOOD: Mock server or test credentials
def test_gmail_connection(mock_imap):
    client = mock_imap  # Uses localhost:3143 with "test@localhost"
    folders = client.list_folders()
    assert "INBOX" in folders
```

### 6. Clean Up Resources

```python
@pytest.fixture
def imap_client():
    """IMAP client fixture with auto-cleanup."""
    client = IMAPClient("localhost", 3143)
    client.login("test@localhost", "test")
    
    yield client  # Test runs here
    
    # Cleanup happens automatically
    client.logout()
```

---

## TDD Workflow Summary

### Daily Development Loop

1. **Pull latest code**
   ```bash
   git pull origin main
   ```

2. **Create feature branch**
   ```bash
   git checkout -b feature/story-2.1-provider-detection
   ```

3. **RED: Write failing test**
   ```bash
   # Create tests/unit/core/test_provider_detector.py
   pytest tests/unit/core/test_provider_detector.py  # Should FAIL
   ```

4. **GREEN: Make test pass**
   ```bash
   # Create src/mailreactor/core/provider_detector.py
   pytest tests/unit/core/test_provider_detector.py  # Should PASS
   ```

5. **REFACTOR: Improve code**
   ```bash
   # Refactor implementation (Pydantic, extract logic, etc.)
   pytest tests/unit/core/test_provider_detector.py  # Still PASS
   ```

6. **Run all tests**
   ```bash
   pytest  # All tests should pass
   ```

7. **Check coverage**
   ```bash
   pytest --cov=src/mailreactor --cov-fail-under=80
   ```

8. **Commit** (pre-commit hooks run automatically)
   ```bash
   git add .
   git commit -m "feat: implement provider auto-detection (Story 2.1)"
   ```

9. **Push and create PR**
   ```bash
   git push origin feature/story-2.1-provider-detection
   # Create pull request on GitHub
   ```

---

## Common Pitfalls

### ❌ Writing Tests After Implementation

```python
# WRONG ORDER:
# 1. Write src/mailreactor/core/provider_detector.py
# 2. Write tests/unit/core/test_provider_detector.py

# This defeats TDD's design feedback!
```

**Correct:** Test FIRST, implementation SECOND.

---

### ❌ Big Jumps Instead of Micro-Cycles

```python
# WRONG: Write 5 tests, then implement everything
def test_gmail(): ...
def test_outlook(): ...
def test_yahoo(): ...
def test_unknown(): ...
def test_custom(): ...

# Then write all implementation at once
# Result: RED → GREEN (30 minutes of coding)
```

**Correct:** One test, minimal code, run test. Repeat.

```python
# RIGHT: Tiny cycles
# Cycle 1: RED (import fails) → GREEN (create file) [10 seconds]
# Cycle 2: RED (class missing) → GREEN (add class) [10 seconds]
# Cycle 3: RED (method missing) → GREEN (add stub) [20 seconds]
# Cycle 4: RED (gmail test) → GREEN (hardcode gmail) [30 seconds]
# Cycle 5: RED (outlook test) → GREEN (add if/elif) [40 seconds]
# Result: 5 cycles in 2 minutes vs 1 cycle in 30 minutes
```

---

### ❌ Skipping Refactor Step

```python
# After test passes, you might be tempted to move on.
# DON'T! Refactor for quality while tests are green.
```

**Correct:** Always refactor after GREEN (Pydantic models, extract functions, etc.)

---

### ❌ Testing Implementation Details

```python
# ❌ BAD: Test internal methods
def test_internal_parsing():
    assert provider._parse_domain("user@gmail.com") == "gmail.com"

# ✅ GOOD: Test public API
def test_gmail_detection():
    settings = provider.detect("user@gmail.com")
    assert settings.imap_host == "imap.gmail.com"
```

---

### ❌ Slow Tests in Unit Suite

```python
# ❌ BAD: Network calls in unit tests
def test_gmail_connection():
    client = IMAPClient("imap.gmail.com", 993)  # Real connection!
    client.login("test@gmail.com", "password")

# ✅ GOOD: Mock or move to integration tests
def test_gmail_connection(mock_imap):
    folders = mock_imap.list_folders()
    assert "INBOX" in folders
```

---

## Resources

### Documentation
- **pytest:** https://pytest.org/
- **pytest-asyncio:** https://pytest-asyncio.readthedocs.io/
- **FastAPI Testing:** https://fastapi.tiangolo.com/tutorial/testing/
- **Pydantic:** https://docs.pydantic.dev/

### Project-Specific
- **Test Design:** `docs/test-design-system.md`
- **Architecture:** `docs/architecture.md`
- **Development Practices:** `docs/development-practices.md`
- **Sprint 0 Checklist:** `docs/sprint-artifacts/sprint-0-checklist.md`

### Running Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/unit/core/test_provider_detector.py

# Specific test
pytest tests/unit/core/test_provider_detector.py::test_gmail_detection

# With coverage
pytest --cov=src/mailreactor --cov-report=html

# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run only E2E tests
pytest -m e2e

# Run everything except E2E
pytest -m "not e2e"
```

---

## Next Steps

After reading this guide:

1. ✅ **Complete Sprint 0 Task #2.2:** Create test templates
2. ✅ **Complete Sprint 0 Task #2.3:** Set up pre-commit hooks
3. ✅ **Complete Sprint 0 Task #3:** Set up mock IMAP/SMTP servers
4. ✅ **Start Epic 1 with TDD:** Write test first for Story 1.1 (Project Structure)

---

**Remember:** Test-first is non-negotiable. RED → GREEN → REFACTOR. Every feature. Every time.

---

**Generated:** 2025-11-27  
**Author:** Murat (TEA - Test Architect)  
**For:** Mail Reactor MVP - Sprint 0 Task #2.1
