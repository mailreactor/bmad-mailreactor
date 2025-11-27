# TDD Anti-Patterns - What NOT to Do

This document lists common TDD mistakes and how to avoid them in Mail Reactor.

---

## Anti-Pattern 1: Writing Tests After Implementation

### ❌ WRONG: Implementation First

```python
# Step 1: Write production code
# src/mailreactor/core/provider_detector.py
class ProviderDetector:
    def detect(self, email):
        # 100 lines of code...
        pass

# Step 2: Write tests after
# tests/unit/core/test_provider_detector.py
def test_provider_detector():
    detector = ProviderDetector()
    assert detector.detect("user@gmail.com") is not None
```

**Why it's bad:**
- Defeats TDD's design feedback
- Tests become "quality theater" (just for coverage)
- You write tests that pass (confirmation bias)
- Harder to refactor (tests coupled to implementation)

### ✅ CORRECT: Test First (RED → GREEN)

```python
# Step 1: Write failing test first
# tests/unit/core/test_provider_detector.py
def test_gmail_detection():
    """RED: This test fails - ProviderDetector doesn't exist."""
    detector = ProviderDetector()
    settings = detector.detect("user@gmail.com")
    assert settings.imap_host == "imap.gmail.com"

# Step 2: Run test (FAILS - ImportError)
# pytest tests/unit/core/test_provider_detector.py

# Step 3: Write minimal code to pass
# src/mailreactor/core/provider_detector.py
class ProviderDetector:
    def detect(self, email):
        return ProviderSettings(imap_host="imap.gmail.com")
```

---

## Anti-Pattern 2: Big Jumps Instead of Micro-Cycles

### ❌ WRONG: Write 5 Tests, Then Implement Everything

```python
# RED: Write complete test suite (15 minutes)
def test_gmail(): ...
def test_outlook(): ...
def test_yahoo(): ...
def test_unknown(): ...
def test_validation(): ...

# GREEN: Implement full feature (60 minutes of coding)
class ProviderDetector:
    # 100+ lines of code before running tests again
    pass

# Result: RED → GREEN (75 minutes between test runs)
```

**Why it's bad:**
- Long feedback loop (find bugs 60 minutes later)
- High cognitive load (tracking multiple requirements)
- Risky (what if implementation is completely wrong?)
- Not actually TDD (just test-after with red step)

### ✅ CORRECT: Micro-Cycles (Every 30 Seconds)

```python
# Cycle 1: RED (import fails) → GREEN (create file) [20 seconds]
def test_import():
    from mailreactor.core.provider_detector import ProviderDetector

# Cycle 2: RED (class missing) → GREEN (add class) [20 seconds]
def test_class_exists():
    detector = ProviderDetector()

# Cycle 3: RED (method missing) → GREEN (add stub) [30 seconds]
def test_detect_exists():
    detector = ProviderDetector()
    result = detector.detect("user@gmail.com")

# Cycle 4: RED (Gmail assertion) → GREEN (hardcode Gmail) [40 seconds]
def test_gmail_host():
    settings = ProviderDetector().detect("user@gmail.com")
    assert settings.imap_host == "imap.gmail.com"

# Result: 4 cycles in 2 minutes vs 1 cycle in 75 minutes
```

---

## Anti-Pattern 3: Testing Implementation Details

### ❌ WRONG: Test Private Methods

```python
class ProviderDetector:
    def detect(self, email):
        domain = self._extract_domain(email)  # Private method
        return self._lookup_provider(domain)  # Private method
    
    def _extract_domain(self, email):
        """Private helper."""
        return email.split("@")[1]
    
    def _lookup_provider(self, domain):
        """Private helper."""
        return PROVIDERS.get(domain)


# ❌ BAD: Testing private methods
def test_extract_domain():
    """This test will break if we refactor internal logic!"""
    detector = ProviderDetector()
    assert detector._extract_domain("user@gmail.com") == "gmail.com"

def test_lookup_provider():
    """Also testing private method - fragile!"""
    detector = ProviderDetector()
    assert detector._lookup_provider("gmail.com") is not None
```

**Why it's bad:**
- Tests become **change detectors**, not behavior validators
- Can't refactor without breaking tests
- Couples tests to implementation (defeats TDD purpose)

### ✅ CORRECT: Test Public API

```python
# ✅ GOOD: Test observable behavior
def test_gmail_detection():
    """Test what users interact with - the public API."""
    detector = ProviderDetector()
    settings = detector.detect("user@gmail.com")
    assert settings.imap_host == "imap.gmail.com"

# Internal implementation can change freely:
# - Could use regex instead of split()
# - Could use database instead of dict
# - Could cache results
# Test still passes as long as behavior is correct!
```

---

## Anti-Pattern 4: Network Calls in Unit Tests

### ❌ WRONG: Real IMAP Connection in Unit Test

```python
def test_list_folders():
    """This is NOT a unit test - it makes real network calls!"""
    client = IMAPClient("imap.gmail.com", 993)  # Real connection!
    client.login("test@gmail.com", "password")  # Real authentication!
    folders = client.list_folders()  # Real IMAP protocol!
    assert "INBOX" in folders
```

**Why it's bad:**
- Slow (network latency)
- Flaky (network issues, Gmail downtime)
- Requires credentials (can't run in CI without secrets)
- Not testing **your code**, testing Gmail's IMAP server

### ✅ CORRECT: Mock External Dependencies

```python
from unittest.mock import Mock

def test_list_folders():
    """Unit test: Mock IMAP client, test wrapper logic."""
    # ARRANGE - Mock the external dependency
    mock_client = Mock()
    mock_client.list_folders.return_value = [
        (b'\\HasNoChildren', b'/', 'INBOX'),
        (b'\\HasNoChildren', b'/', 'Sent'),
    ]
    
    # ACT - Test YOUR code (wrapper logic)
    with patch('mailreactor.core.imap_client.IMAPClient', return_value=mock_client):
        wrapper = AsyncIMAPClient(host="imap.gmail.com")
        folders = wrapper.parse_folders()  # Your logic
    
    # ASSERT - Verify wrapper behavior, not Gmail behavior
    assert "INBOX" in folders
    assert len(folders) == 2
```

**Use integration tests for real connections:**
```python
# tests/integration/test_imap_real.py
@pytest.mark.integration
def test_imap_with_greenmail():
    """Integration test: Real IMAP protocol, localhost test server."""
    client = IMAPClient("localhost", 3143)  # Greenmail, not Gmail
    client.login("test@localhost", "test")
    folders = client.list_folders()
    assert "INBOX" in str(folders)
```

---

## Anti-Pattern 5: Multiple Assertions Testing Unrelated Things

### ❌ WRONG: One Test, Many Concerns

```python
def test_provider_detector():
    """This test does too much!"""
    detector = ProviderDetector()
    
    # Testing Gmail
    gmail = detector.detect("user@gmail.com")
    assert gmail.imap_host == "imap.gmail.com"
    assert gmail.imap_port == 993
    
    # Testing Outlook
    outlook = detector.detect("user@outlook.com")
    assert outlook.imap_host == "outlook.office365.com"
    
    # Testing error handling
    with pytest.raises(ValueError):
        detector.detect("invalid-email")
    
    # Testing validation
    with pytest.raises(ValueError):
        detector.detect("")
```

**Why it's bad:**
- Test failure doesn't pinpoint issue (which assertion failed?)
- Can't run tests independently
- Violates Single Responsibility Principle
- Hard to understand test purpose

### ✅ CORRECT: One Test, One Concept

```python
def test_gmail_detection():
    """Test Gmail provider detection."""
    detector = ProviderDetector()
    settings = detector.detect("user@gmail.com")
    assert settings.imap_host == "imap.gmail.com"
    assert settings.imap_port == 993  # OK - same concept (Gmail settings)

def test_outlook_detection():
    """Test Outlook provider detection."""
    detector = ProviderDetector()
    settings = detector.detect("user@outlook.com")
    assert settings.imap_host == "outlook.office365.com"

def test_invalid_email_raises_error():
    """Test invalid email raises ValueError."""
    detector = ProviderDetector()
    with pytest.raises(ValueError):
        detector.detect("invalid-email")

def test_empty_email_raises_error():
    """Test empty email raises ValueError."""
    detector = ProviderDetector()
    with pytest.raises(ValueError):
        detector.detect("")
```

**Exception:** Multiple assertions OK if testing same object:
```python
def test_provider_settings_creation():
    """Multiple assertions OK - all test 'settings object created correctly'."""
    settings = ProviderSettings(
        imap_host="imap.gmail.com",
        imap_port=993,
        imap_ssl=True,
    )
    assert settings.imap_host == "imap.gmail.com"  # Same concept
    assert settings.imap_port == 993                # Same concept
    assert settings.imap_ssl is True                # Same concept
```

---

## Anti-Pattern 6: Vague Test Names

### ❌ WRONG: Unclear Names

```python
def test_detector():
    """What does this test?"""
    pass

def test_detect():
    """What scenario? What's expected?"""
    pass

def test_provider():
    """Provider what? Detection? Validation? Creation?"""
    pass

def test_1():
    """Meaningless!"""
    pass
```

### ✅ CORRECT: Descriptive Names

```python
def test_gmail_detection_from_email():
    """Clear: Given Gmail email, auto-detect IMAP/SMTP settings."""
    pass

def test_unknown_provider_raises_value_error():
    """Clear: Unknown provider should raise ValueError."""
    pass

def test_provider_settings_stores_imap_host():
    """Clear: ProviderSettings should store imap_host field."""
    pass
```

**Naming pattern:** `test_<what>_<condition>_<expected>`
- `test_gmail_detection_from_email`
- `test_invalid_credentials_return_401`
- `test_empty_password_raises_validation_error`

---

## Anti-Pattern 7: No Arrange-Act-Assert Structure

### ❌ WRONG: Jumbled Test

```python
def test_detection():
    detector = ProviderDetector()
    assert detector.detect("user@gmail.com").imap_host == "imap.gmail.com"
    email = "user@outlook.com"
    result = detector.detect(email)
    assert result.imap_port == 993
```

**Why it's bad:**
- Hard to read (what's setup vs execution vs verification?)
- Difficult to debug
- Unclear test intent

### ✅ CORRECT: Clear AAA Pattern

```python
def test_gmail_detection():
    """Test Gmail provider auto-detection."""
    # ARRANGE - Set up test data
    detector = ProviderDetector()
    email = "user@gmail.com"
    
    # ACT - Execute code under test
    settings = detector.detect(email)
    
    # ASSERT - Verify outcome
    assert settings.imap_host == "imap.gmail.com"
    assert settings.imap_port == 993
```

---

## Anti-Pattern 8: Committing Secrets in Tests

### ❌ WRONG: Real Credentials

```python
def test_gmail_connection():
    """NEVER commit real credentials!"""
    client = IMAPClient("imap.gmail.com", 993)
    client.login("myrealemail@gmail.com", "my-actual-password")  # SECURITY RISK!
    folders = client.list_folders()
```

**Why it's bad:**
- Credentials exposed in version control (forever!)
- Security breach if repo is public
- Violates NFR-S1 (credential handling)

### ✅ CORRECT: Mock or Test Servers

```python
# Unit test: Mock
def test_gmail_connection():
    """Mock for unit tests - no real credentials."""
    mock_client = Mock()
    mock_client.list_folders.return_value = ["INBOX"]
    # Test wrapper logic, not Gmail


# Integration test: Local test server
@pytest.mark.integration
def test_imap_connection():
    """Greenmail auto-creates accounts - no real credentials needed."""
    client = IMAPClient("localhost", 3143)
    client.login("test@localhost", "test")  # Greenmail accepts any password
    folders = client.list_folders()


# E2E test: Environment variables
@pytest.mark.e2e
def test_gmail_e2e():
    """Real credentials from environment - never hardcoded."""
    email = os.getenv("TEST_GMAIL_EMAIL")  # From CI secrets
    password = os.getenv("TEST_GMAIL_PASSWORD")  # From CI secrets
    
    if not email or not password:
        pytest.skip("E2E credentials not configured")
    
    # Use credentials from environment
```

---

## Anti-Pattern 9: Skipping Refactor Step

### ❌ WRONG: RED → GREEN → Next Feature

```python
# RED: Write test
def test_gmail_detection():
    settings = detector.detect("user@gmail.com")
    assert settings.imap_host == "imap.gmail.com"

# GREEN: Hardcode to pass
class ProviderDetector:
    def detect(self, email):
        return ProviderSettings(imap_host="imap.gmail.com")  # Hardcoded!

# ❌ STOP HERE - Move to next feature
# Result: Messy code accumulates!
```

### ✅ CORRECT: RED → GREEN → REFACTOR

```python
# RED: Write test
def test_gmail_detection():
    settings = detector.detect("user@gmail.com")
    assert settings.imap_host == "imap.gmail.com"

# GREEN: Hardcode to pass
class ProviderDetector:
    def detect(self, email):
        return ProviderSettings(imap_host="imap.gmail.com")

# REFACTOR: Improve while tests stay green
class ProviderDetector:
    def __init__(self):
        self.providers = self._load_providers()  # Extract to method
    
    def _load_providers(self):
        return {
            "gmail.com": ProviderSettings(imap_host="imap.gmail.com"),
        }
    
    def detect(self, email):
        domain = email.split("@")[1]
        return self.providers.get(domain)

# Tests still pass after refactor!
```

---

## Anti-Pattern 10: Mocking What You Don't Own

### ❌ WRONG: Mock Third-Party Library Internals

```python
def test_imap_list_folders():
    """Mocking IMAPClient internals - fragile!"""
    with patch('imapclient.IMAPClient._command') as mock_cmd:
        mock_cmd.return_value = b'OK LIST completed'
        # Testing IMAPClient's internal implementation!
```

**Why it's bad:**
- Breaks when library updates (even patch versions)
- Tests implementation, not behavior
- You're testing the library, not your code

### ✅ CORRECT: Wrap and Mock Your Wrapper

```python
# Your wrapper
class AsyncIMAPClient:
    """Wrapper around IMAPClient with async support."""
    
    def __init__(self, host, port):
        self.client = IMAPClient(host, port)  # Third-party
    
    def list_folders(self):
        """Your logic wrapping library."""
        raw_folders = self.client.list_folders()
        return [folder[2] for folder in raw_folders]  # Parse response


# Test YOUR wrapper
def test_list_folders_parsing():
    """Mock the third-party client at YOUR boundary."""
    mock_client = Mock()
    mock_client.list_folders.return_value = [
        (b'\\HasNoChildren', b'/', 'INBOX'),
        (b'\\HasNoChildren', b'/', 'Sent'),
    ]
    
    with patch('mailreactor.core.imap_client.IMAPClient', return_value=mock_client):
        wrapper = AsyncIMAPClient(host="localhost", port=143)
        folders = wrapper.list_folders()
    
    # Test YOUR parsing logic
    assert folders == ['INBOX', 'Sent']
```

---

## Summary: TDD Golden Rules

1. **Test FIRST, code SECOND** (RED → GREEN)
2. **Micro-cycles** (every 30 seconds, not 30 minutes)
3. **Test public API**, not implementation details
4. **Mock external dependencies** in unit tests
5. **One test, one concept** (single responsibility)
6. **Descriptive names** (`test_gmail_detection_from_email`)
7. **Arrange-Act-Assert** structure
8. **Never commit secrets** (use mocks or environment variables)
9. **Always refactor** (RED → GREEN → REFACTOR)
10. **Mock YOUR wrappers**, not third-party internals

---

**Follow these rules to write maintainable, fast, reliable tests for Mail Reactor.**

---

**Generated:** 2025-11-27  
**Author:** Murat (TEA - Test Architect)  
**For:** Mail Reactor MVP - Sprint 0 Task #2.2
