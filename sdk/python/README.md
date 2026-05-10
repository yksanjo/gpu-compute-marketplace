# Python SDK for GPU Compute Marketplace

Official Python SDK for interacting with the GPU Compute Marketplace Platform.

## Installation

```bash
pip install gpucompute-sdk
```

## Quick Start

```python
from gpucompute import Client

# Initialize client
client = Client(api_key="your-api-key")

# Check token balance
balance = client.tokens.get_balance()
print(f"Balance: {balance['active']} CC")

# Submit a compute job
job = client.jobs.submit(
    gpu_requirements={
        "type": "A100",
        "count": 4,
        "memory": 40
    },
    container_image="docker.io/user/model-training:latest",
    priority="normal",
    estimated_duration=2.5
)

print(f"Job submitted: {job['id']}")

# Monitor job status
status = client.jobs.get_status(job['id'])
print(f"Status: {status['status']}")
```

## Features

- **Job Management**: Submit, monitor, and cancel compute jobs
- **Token Operations**: Purchase, reserve, and manage compute credits
- **Resource Discovery**: Find available GPU resources
- **Async Support**: Async/await support for concurrent operations
- **WebSocket**: Real-time job status updates

## Documentation

See [docs/](docs/) for detailed documentation.

