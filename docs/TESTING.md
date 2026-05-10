# Testing Guide

## Overview

This guide covers how to test the GPU Compute Marketplace Platform components, including unit tests, integration tests, and end-to-end testing.

## Test Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_matching_engine.py
│   ├── test_scheduler.py
│   ├── test_token_manager.py
│   └── test_client.py
├── integration/             # Integration tests
│   ├── test_api_endpoints.py
│   ├── test_job_lifecycle.py
│   └── test_token_flow.py
└── e2e/                     # End-to-end tests
    └── test_full_workflow.py
```

## Running Tests

### Prerequisites

```bash
pip install pytest pytest-cov pytest-asyncio
```

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Suite

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# E2E tests only
pytest tests/e2e/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=services --cov=api --cov=sdk --cov-report=html
```

## Unit Tests

### Testing Matching Engine

```python
# tests/unit/test_matching_engine.py
import pytest
from services.matching_engine.src.matching_engine import (
    MatchingEngine, GPURequirement, MatchingPreferences, 
    GPUResource, GPUTier, Urgency
)

def test_matching_engine_find_matches():
    engine = MatchingEngine()
    
    # Add test resources
    resource = GPUResource(
        id="gpu-1",
        data_center_id="dc-1",
        gpu_type="A100",
        available=True,
        current_load=0.5,
        price_per_hour=3.0,
        location="us-east-1",
        tier=GPUTier.ON_DEMAND,
        specs={"memory": 40, "compute_capability": "8.0"},
        availability_score=0.99
    )
    engine.update_resource(resource)
    
    # Test matching
    requirements = GPURequirement(type="A100", count=1, memory=40)
    preferences = MatchingPreferences(max_price=5.0, tier=GPUTier.ON_DEMAND)
    
    matches = engine.find_matches(requirements, preferences, Urgency.NORMAL)
    
    assert len(matches) > 0
    assert matches[0].gpu_type == "A100"
    assert matches[0].price_per_hour <= 5.0
```

### Testing Scheduler

```python
# tests/unit/test_scheduler.py
import pytest
from services.scheduler.src.scheduler import (
    Scheduler, GPURequirement, JobPriority, JobStatus
)

def test_scheduler_submit_job():
    scheduler = Scheduler()
    
    requirements = GPURequirement(type="A100", count=1, memory=40)
    job = scheduler.submit_job(
        user_id="user-1",
        gpu_requirements=requirements,
        container_image="test:latest",
        priority=JobPriority.NORMAL
    )
    
    assert job.id is not None
    assert job.status == JobStatus.QUEUED
    assert job.priority == JobPriority.NORMAL
```

### Testing Token Manager

```python
# tests/unit/test_token_manager.py
import pytest
from services.token_manager.src.token_manager import TokenManager

def test_token_purchase():
    manager = TokenManager()
    
    result = manager.purchase_tokens(
        user_id="user-1",
        amount=100.0,
        payment_method="stripe"
    )
    
    assert result["amount"] == 100.0
    assert result["newBalance"] == 100.0
    
    balance = manager.get_balance("user-1")
    assert balance["active"] == 100.0
```

## Integration Tests

### Testing API Endpoints

```python
# tests/integration/test_api_endpoints.py
import pytest
import requests

BASE_URL = "http://localhost:8000/v1"

def test_get_token_balance(api_key):
    response = requests.get(
        f"{BASE_URL}/tokens/balance",
        headers={"Authorization": f"Bearer {api_key}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "active" in data
    assert "reserved" in data

def test_submit_job(api_key):
    response = requests.post(
        f"{BASE_URL}/jobs",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "gpuRequirements": {
                "type": "A100",
                "count": 1,
                "memory": 40
            },
            "containerImage": "test:latest",
            "priority": "normal"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["status"] == "queued"
```

## End-to-End Tests

### Full Workflow Test

```python
# tests/e2e/test_full_workflow.py
import pytest
from gpucompute import Client

def test_full_workflow():
    client = Client(api_key="test-key")
    
    # 1. Check balance
    balance = client.tokens.get_balance()
    initial_balance = balance["active"]
    
    # 2. Purchase tokens
    purchase = client.tokens.purchase(amount=100.0, payment_method="test")
    assert purchase["amount"] == 100.0
    
    # 3. Submit job
    job = client.jobs.submit(
        gpu_requirements={"type": "A100", "count": 1, "memory": 40},
        container_image="test:latest"
    )
    assert job["status"] == "queued"
    
    # 4. Check job status
    status = client.jobs.get_status(job["id"])
    assert status["id"] == job["id"]
    
    # 5. Cancel job
    client.jobs.cancel(job["id"])
```

## Manual Testing

### Test Token Operations

```bash
# 1. Get balance
curl -X GET http://localhost:8000/v1/tokens/balance \
  -H "Authorization: Bearer YOUR_API_KEY"

# 2. Purchase tokens
curl -X POST http://localhost:8000/v1/tokens/purchase \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100.0, "paymentMethod": "stripe"}'

# 3. Reserve tokens
curl -X POST http://localhost:8000/v1/tokens/reserve \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "jobId": "job-123",
    "amount": 50.0,
    "estimatedDuration": 2.0,
    "gpuType": "A100"
  }'
```

### Test Job Operations

```bash
# 1. Submit job
curl -X POST http://localhost:8000/v1/jobs \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "gpuRequirements": {
      "type": "A100",
      "count": 1,
      "memory": 40
    },
    "containerImage": "docker.io/test:latest",
    "priority": "normal"
  }'

# 2. Get job status
curl -X GET http://localhost:8000/v1/jobs/JOB_ID \
  -H "Authorization: Bearer YOUR_API_KEY"

# 3. Cancel job
curl -X DELETE http://localhost:8000/v1/jobs/JOB_ID \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Performance Testing

### Load Testing

```python
# tests/performance/test_load.py
import pytest
import concurrent.futures
from gpucompute import Client

def test_concurrent_job_submissions():
    client = Client(api_key="test-key")
    
    def submit_job(i):
        return client.jobs.submit(
            gpu_requirements={"type": "A100", "count": 1, "memory": 40},
            container_image=f"test:{i}",
            priority="normal"
        )
    
    # Submit 100 jobs concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(submit_job, i) for i in range(100)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    assert len(results) == 100
    assert all(r["status"] == "queued" for r in results)
```

## Test Data Setup

### Fixtures

```python
# tests/conftest.py
import pytest
from services.token_manager.src.token_manager import TokenManager
from services.scheduler.src.scheduler import Scheduler

@pytest.fixture
def token_manager():
    return TokenManager()

@pytest.fixture
def scheduler():
    return Scheduler()

@pytest.fixture
def api_key():
    return "test-api-key-12345"
```

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-cov
      - run: pytest tests/ --cov=. --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Test Checklist

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Code coverage > 80%
- [ ] No linting errors
- [ ] API documentation matches implementation
- [ ] Error handling works correctly
- [ ] Performance meets requirements

