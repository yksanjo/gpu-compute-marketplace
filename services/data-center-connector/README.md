# Data Center Connector Service

## Overview

The Data Center Connector provides an abstraction layer for connecting to different data center APIs and managing GPU resources across multiple providers.

## Key Features

1. **Multi-Provider Support**: Unified interface for different data center APIs
2. **Resource Discovery**: Discover available GPU resources
3. **Health Monitoring**: Monitor data center and GPU health
4. **Capacity Reporting**: Track available capacity
5. **Failover**: Automatic failover to backup data centers
6. **Secure Connections**: VPN tunnels and secure API connections

## Supported Providers

- **Kubernetes Clusters**: Standard Kubernetes API
- **Custom APIs**: REST APIs from data center partners
- **Cloud Providers**: AWS, GCP, Azure (future)

## Architecture

```
Platform Services → Data Center Connector → Provider Adapters → Data Center APIs
```

## Implementation

See `services/data-center-connector/src/` for implementation details.

