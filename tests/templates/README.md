# Test Templates

Copy these templates to create new tests following Mail Reactor TDD standards.

---

## Quick Start

### Unit Test
```bash
cp tests/templates/test_unit_template.py tests/unit/core/test_my_feature.py
# Edit: Replace examples with your actual tests
# Run: pytest tests/unit/core/test_my_feature.py -v
```

### Integration Test
```bash
cp tests/templates/test_integration_template.py tests/integration/api/test_my_endpoint.py
# Edit: Replace examples with your API endpoint tests
# Run: pytest tests/integration/api/test_my_endpoint.py -v
```

### E2E Test
```bash
cp tests/templates/test_e2e_template.py tests/e2e/test_my_journey.py
# Edit: Replace examples with your user journey
# Run: pytest tests/e2e/test_my_journey.py -v
```

---

## Template Contents

Each template includes:

- ✅ **Basic test structure** (Arrange-Act-Assert pattern)
- ✅ **Common pytest patterns** (parametrize, markers, async)
- ✅ **Error handling examples** (pytest.raises)
- ✅ **Real Mail Reactor examples** (ProviderDetector, IMAP/SMTP)
- ✅ **Generic placeholders** (adaptable to any feature)
- ✅ **Inline comments** explaining key patterns

---

## Test Distribution (from Test Design)

- **Unit Tests (50%):** Pure Python logic, no network/I/O, <1ms per test
- **Integration Tests (35%):** API endpoints with local test servers, ~100ms per test
- **E2E Tests (15%):** Critical paths with real servers, ~5s per test

---

## TDD Workflow Reminder

Follow the **micro-cycle** approach:

```
RED → Write smallest failing test (import fails)
  ↓
GREEN → Create empty file/class
  ↓
RED → Add method test (method missing)
  ↓
GREEN → Add method stub
  ↓
RED → Test specific behavior (Gmail detection)
  ↓
GREEN → Hardcode Gmail result
  ↓
RED → Add Outlook test (forces generalization)
  ↓
GREEN → Add if/elif logic
  ↓
[Continue micro-cycles until feature complete]
  ↓
REFACTOR → Improve code quality (all tests stay green)
```

**Each cycle: seconds to minutes, not hours.**

---

## Files in This Directory

| File | Purpose |
|------|---------|
| `test_unit_template.py` | Unit test patterns (mocking, parametrize, error handling) |
| `test_integration_template.py` | Integration test patterns (FastAPI, async, test servers) |
| `test_e2e_template.py` | E2E test patterns (multi-step journeys, markers, cleanup) |
| `anti-patterns.md` | Common TDD mistakes and how to avoid them |
| `README.md` | This file |

---

## Next Steps After Copying Template

1. **Rename file** to match your feature (`test_provider_detector.py`)
2. **Write first micro-test** (e.g., import fails)
3. **Run test** (should fail - RED)
4. **Write minimal code** to pass (GREEN)
5. **Add next test** (RED again)
6. **Repeat micro-cycles** until feature complete
7. **Refactor** while tests stay green
8. **Check coverage**: `pytest --cov=src/mailreactor --cov-report=html`

---

## Resources

- **TDD Guide:** `docs/tdd-guide.md`
- **Test Design:** `docs/test-design-system.md`
- **Architecture:** `docs/architecture.md`
- **Development Practices:** `docs/development-practices.md`

---

**Remember:** Test FIRST, then implement. RED → GREEN → RED → GREEN (micro-cycles).

---

**Generated:** 2025-11-27  
**Author:** Murat (TEA - Test Architect)  
**For:** Mail Reactor MVP - Sprint 0 Task #2.2
