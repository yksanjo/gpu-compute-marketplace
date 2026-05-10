# Getting Started

## Overview

This guide will help you get started with the GPU Compute Marketplace Platform, whether you're a developer, data center operator, or end user.

## For Developers

### Prerequisites

- Python 3.8+
- Node.js 16+ (for JavaScript SDK)
- Docker and Docker Compose
- Kubernetes cluster (for production)
- PostgreSQL 14+
- Redis 6+

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/gpucompute/platform.git
   cd platform
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start dependencies**
   ```bash
   docker-compose up -d postgres redis rabbitmq
   ```

4. **Run database migrations**
   ```bash
   cd services/token-manager
   alembic upgrade head
   ```

5. **Start services**
   ```bash
   # Terminal 1: API Gateway
   cd api/gateway
   python -m uvicorn main:app --reload
   
   # Terminal 2: Matching Engine
   cd services/matching-engine
   python -m uvicorn main:app --reload --port 8001
   
   # Terminal 3: Scheduler
   cd services/scheduler
   python -m uvicorn main:app --reload --port 8002
   
   # Terminal 4: Token Manager
   cd services/token-manager
   python -m uvicorn main:app --reload --port 8003
   ```

6. **Run tests**
   ```bash
   pytest tests/
   ```

## For Data Center Operators

### Onboarding Process

1. **Initial Contact**
   - Reach out to partnerships@gpucompute.market
   - Schedule technical assessment call

2. **Technical Requirements**
   - Kubernetes cluster with GPU support
   - NVIDIA Container Toolkit
   - Network connectivity (VPN or private link)
   - Monitoring and logging systems

3. **Integration**
   - Deploy data center connector agent
   - Configure API credentials
   - Test resource provisioning
   - Set up monitoring

4. **Go Live**
   - Final testing
   - Production deployment
   - Monitor initial usage

### Documentation

- [Data Center Integration Guide](DATA_CENTER_INTEGRATION.md)
- [API Documentation](api/README.md)
- [Partnership Agreement Template](../contracts/partnership_agreement_template.md)

## For End Users

### Quick Start

1. **Sign Up**
   - Visit https://gpucompute.market
   - Create an account
   - Verify your email

2. **Get API Key**
   - Go to Dashboard → API Keys
   - Generate a new API key
   - Save it securely

3. **Install SDK**
   ```bash
   pip install gpucompute-sdk
   ```

4. **Purchase Credits**
   - Go to Dashboard → Tokens
   - Purchase compute credits
   - Credits are available immediately

5. **Submit Your First Job**
   ```python
   from gpucompute import Client
   
   client = Client(api_key="your-api-key")
   
   job = client.jobs.submit(
       gpu_requirements={
           "type": "A100",
           "count": 1,
           "memory": 40
       },
       container_image="docker.io/your/image:latest",
       priority="normal"
   )
   
   print(f"Job ID: {job['id']}")
   ```

6. **Monitor Job**
   ```python
   status = client.jobs.get_status(job['id'])
   print(f"Status: {status['status']}")
   ```

### Documentation

- [User Guide](USER_GUIDE.md)
- [API Reference](api/openapi.yaml)
- [Python SDK Documentation](../sdk/python/README.md)
- [Examples](../api/examples/)

## Next Steps

- Read the [Architecture Overview](ARCHITECTURE.md)
- Check out [API Examples](../api/examples/)
- Join our [Community Discord](https://discord.gg/gpucompute)
- Follow us on [Twitter](https://twitter.com/gpucompute)

## Support

- **Email**: support@gpucompute.market
- **Documentation**: https://docs.gpucompute.market
- **Community**: https://discord.gg/gpucompute
- **GitHub Issues**: https://github.com/gpucompute/platform/issues

