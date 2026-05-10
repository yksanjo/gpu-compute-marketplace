# Test Suite

## Overview

This directory contains the test suite for the GPU Compute Marketplace Platform.

## Test Structure

```
tests/
├── unit/                    # Unit tests
├── integration/             # Integration tests
├── e2e/                     # End-to-end tests
└── conftest.py             # Pytest fixtures
```

## Running Tests

See `docs/TESTING.md` for detailed testing instructions.

## Test Coverage Goals

- Unit tests: >90% coverage
- Integration tests: >80% coverage
- E2E tests: Critical paths covered

## Writing Tests

### Example Unit Test

```python
# tests/unit/test_matching_engine.py
import pytest
from services.matching_engine.src.matching_engine import MatchingEngine

def test_find_matches():
    engine = MatchingEngine()
    # Add test resources
    # Test matching logic
    assert True  # Replace with actual test
```

### Example Integration Test

```python
# tests/integration/test_api.py
import pytest
import requests

def test_token_balance_endpoint():
    response = requests.get("http://localhost:8000/v1/tokens/balance")
    assert response.status_code == 200
```

## Test Data

- Use fixtures for test data
- Clean up after tests
- Use factories for complex objects

## CI/CD

Tests run automatically on:
- Pull requests
- Commits to main branch
- Scheduled runs

See `.github/workflows/test.yml` for CI configuration.








