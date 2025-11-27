"""
Unit Test Template for Mail Reactor

Copy this file to tests/unit/<module>/test_<feature>.py and customize.

Unit Test Characteristics:
- Fast (<1ms per test)
- No network/file I/O
- Mock all external dependencies
- Test business logic in isolation
- 50% of total test budget

Follow TDD micro-cycles: RED → GREEN → RED → GREEN (each cycle: seconds)
"""

import pytest
from unittest.mock import Mock, patch


# =====================================================
# Section 1: Basic Test Structure
# =====================================================

class TestBasicExample:
    """Example: Simple unit test with Arrange-Act-Assert pattern."""

    def test_function_returns_expected_value(self):
        """
        Test basic functionality.
        
        Pattern: Arrange-Act-Assert (AAA)
        """
        # ARRANGE - Set up test data and dependencies
        input_data = "example"
        expected_output = "EXAMPLE"
        
        # ACT - Execute the code under test
        result = input_data.upper()  # Replace with your function
        
        # ASSERT - Verify the outcome
        assert result == expected_output


# =====================================================
# Section 2: Parametrized Tests (DRY Principle)
# =====================================================

class TestParametrizedExample:
    """Example: Test multiple scenarios with pytest.mark.parametrize."""

    @pytest.mark.parametrize("input_val,expected", [
        # Each tuple becomes one test run
        ("gmail.com", "imap.gmail.com"),
        ("outlook.com", "outlook.office365.com"),
        ("yahoo.com", "imap.mail.yahoo.com"),
    ])
    def test_multiple_providers(self, input_val, expected):
        """
        Test multiple scenarios with one test function.
        
        Pattern: parametrize - reduces code duplication.
        Runs this test 3 times with different inputs.
        """
        # ARRANGE
        domain = input_val
        
        # ACT
        result = f"imap.{domain}"  # Replace with your logic
        
        # ASSERT
        assert result == expected


# =====================================================
# Section 3: Mail Reactor Real Example
# =====================================================

class TestProviderDetector:
    """
    Real Mail Reactor example: Provider auto-detection.
    
    This shows how to test actual Mail Reactor code.
    Adapt this pattern for your feature.
    """

    def test_gmail_detection_from_email(self):
        """
        Test Gmail provider auto-detection.
        
        TDD Micro-cycle approach:
        1. RED: This test fails (ProviderDetector doesn't exist)
        2. GREEN: Create ProviderDetector class with detect() method
        3. RED: Add assertion for imap_port
        4. GREEN: Add imap_port field
        5. Continue micro-cycles...
        """
        # ARRANGE
        # Uncomment when implementing:
        # from mailreactor.core.provider_detector import ProviderDetector
        # detector = ProviderDetector()
        # email = "user@gmail.com"
        
        # ACT
        # settings = detector.detect(email)
        
        # ASSERT
        # assert settings.imap_host == "imap.gmail.com"
        # assert settings.imap_port == 993
        # assert settings.imap_ssl is True
        
        # Placeholder for template
        assert True


    @pytest.mark.parametrize("email,expected_host", [
        ("user@gmail.com", "imap.gmail.com"),
        ("user@outlook.com", "outlook.office365.com"),
        ("user@yahoo.com", "imap.mail.yahoo.com"),
    ])
    def test_provider_detection_parametrized(self, email, expected_host):
        """
        Test provider detection for multiple providers.
        
        Pattern: Combine parametrize with real code.
        """
        # ARRANGE
        # from mailreactor.core.provider_detector import ProviderDetector
        # detector = ProviderDetector()
        
        # ACT
        # settings = detector.detect(email)
        
        # ASSERT
        # assert settings.imap_host == expected_host
        
        # Placeholder
        assert True


# =====================================================
# Section 4: Error Handling Tests
# =====================================================

class TestErrorHandling:
    """Example: Test exceptions and error cases."""

    def test_raises_value_error_for_invalid_input(self):
        """
        Test function raises ValueError for invalid input.
        
        Pattern: pytest.raises context manager.
        """
        # ARRANGE
        invalid_input = None
        
        # ACT & ASSERT
        with pytest.raises(ValueError) as exc_info:
            if invalid_input is None:
                raise ValueError("Input cannot be None")
        
        # Verify error message contains expected text
        assert "cannot be None" in str(exc_info.value)


    def test_unknown_provider_raises_error(self):
        """Test unknown email provider raises helpful error."""
        # ARRANGE
        # from mailreactor.core.provider_detector import ProviderDetector
        # detector = ProviderDetector()
        # email = "user@unknownprovider.com"
        
        # ACT & ASSERT
        # with pytest.raises(ValueError) as exc_info:
        #     detector.detect(email)
        
        # assert "Unknown provider" in str(exc_info.value)
        
        # Placeholder
        assert True


# =====================================================
# Section 5: Mocking External Dependencies
# =====================================================

class TestWithMocking:
    """Example: Mock external dependencies (IMAP, SMTP, API calls)."""

    def test_imap_wrapper_with_mock(self):
        """
        Test IMAP wrapper without real network connection.
        
        Pattern: unittest.mock for external dependencies.
        Unit tests should NEVER make real network calls.
        """
        # ARRANGE - Create mock IMAP client
        mock_imap = Mock()
        mock_imap.list_folders.return_value = [
            (b'\\HasNoChildren', b'/', 'INBOX'),
            (b'\\HasNoChildren', b'/', 'Sent'),
        ]
        
        # ACT - Use mock in place of real IMAPClient
        # In real code, you'd patch the import:
        # with patch('mailreactor.core.imap_client.IMAPClient', return_value=mock_imap):
        #     wrapper = AsyncIMAPClient(host="localhost")
        #     folders = await wrapper.list_folders()
        
        folders = ["INBOX", "Sent"]  # Placeholder
        
        # ASSERT - Verify wrapper logic, not IMAP server
        assert "INBOX" in folders
        assert len(folders) == 2


    def test_with_patching(self):
        """
        Test using patch decorator/context manager.
        
        Pattern: patch() replaces imports during test execution.
        """
        # ARRANGE
        mock_response = Mock()
        mock_response.json.return_value = {"status": "ok"}
        
        # ACT - Patch requests.get to return mock response
        with patch('requests.get', return_value=mock_response):
            # In real code:
            # response = requests.get("https://api.example.com")
            # data = response.json()
            data = {"status": "ok"}  # Placeholder
        
        # ASSERT
        assert data["status"] == "ok"


# =====================================================
# Section 6: Multiple Assertions (When Appropriate)
# =====================================================

class TestMultipleAssertions:
    """
    Example: When to use multiple assertions in one test.
    
    General rule: One assertion per test.
    Exception: Testing multiple properties of same object.
    """

    def test_provider_settings_complete(self):
        """
        Test ProviderSettings object has all required fields.
        
        Multiple assertions OK here - testing one concept (object creation).
        """
        # ARRANGE & ACT
        # from mailreactor.core.provider_detector import ProviderSettings
        # settings = ProviderSettings(
        #     imap_host="imap.gmail.com",
        #     imap_port=993,
        #     imap_ssl=True,
        #     smtp_host="smtp.gmail.com",
        #     smtp_port=587,
        #     smtp_starttls=True,
        # )
        
        # ASSERT - All assertions test "settings object is correctly created"
        # assert settings.imap_host == "imap.gmail.com"
        # assert settings.imap_port == 993
        # assert settings.imap_ssl is True
        # assert settings.smtp_host == "smtp.gmail.com"
        # assert settings.smtp_port == 587
        # assert settings.smtp_starttls is True
        
        # Placeholder
        assert True


# =====================================================
# Section 7: Test Organization Tips
# =====================================================

"""
Tips for organizing unit tests:

1. One test class per class/module being tested
   - TestProviderDetector for ProviderDetector class
   - TestMessageParser for MessageParser class

2. Descriptive test names
   - test_gmail_detection_from_email (clear)
   - test_detect (unclear)

3. Group related tests
   - class TestProviderDetectorSuccess (happy paths)
   - class TestProviderDetectorErrors (error cases)

4. Use docstrings
   - Explain WHAT is being tested and WHY
   - Not HOW (code shows that)

5. Keep tests independent
   - No shared state between tests
   - Each test can run alone or in any order

6. Fast feedback
   - Unit tests should be <1ms each
   - Run them constantly during TDD cycles
"""


# =====================================================
# Usage Instructions
# =====================================================

"""
How to use this template:

1. Copy to tests/unit/<module>/test_<feature>.py
   Example: tests/unit/core/test_provider_detector.py

2. Replace examples with your actual code
   - Import your modules
   - Replace placeholder logic
   - Add/remove sections as needed

3. Follow TDD micro-cycles
   RED:   Write smallest failing test
   GREEN: Write minimal code to pass
   RED:   Add next failing test
   GREEN: Extend code to pass both tests
   [Repeat until feature complete]
   REFACTOR: Improve code quality

4. Run tests frequently
   pytest tests/unit/core/test_provider_detector.py -v
   
5. Check coverage
   pytest tests/unit/core/test_provider_detector.py --cov=src/mailreactor

6. Keep tests fast
   If a test takes >1ms, it's not a unit test
   Move slow tests to integration/
"""
