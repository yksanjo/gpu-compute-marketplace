# GPU Compute Marketplace Platform

A marketplace platform that aggregates underutilized GPU capacity from data centers and sells it as computational tokens, accessible via APIs for AI agents and other compute consumers.

## Architecture Overview

The platform consists of several core microservices:
- **Matching Engine**: Real-time matching of compute requests to available GPU capacity
- **Scheduling Service**: Job queue management and resource allocation
- **Token Manager**: Compute credit issuance, redemption, and balance tracking
- **Billing Service**: Usage metering, billing cycles, and revenue sharing
- **Data Center Connector**: Abstraction layer for different data center APIs

## Quick Start

See [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) for setup instructions.

## Project Structure

```
.
├── services/              # Core microservices
│   ├── matching-engine/
│   ├── scheduler/
│   ├── token-manager/
│   ├── billing/
│   └── data-center-connector/
├── api/                   # API Gateway and specifications
├── sdk/                   # Client SDKs (Python, JavaScript)
├── infrastructure/        # Kubernetes, Docker configs
├── docs/                  # Documentation
└── contracts/             # Data center partnership contracts templates
```

## License

Proprietary

