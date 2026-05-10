# Core Services Architecture

This directory contains the core microservices for the GPU Compute Marketplace Platform.

## Service Overview

### 1. Matching Engine
Matches compute job requests to available GPU resources based on requirements, pricing, and availability.

**Location**: `services/matching-engine/`

### 2. Scheduler Service
Manages job queues, priority scheduling, and resource allocation.

**Location**: `services/scheduler/`

### 3. Token Manager
Handles compute credit issuance, redemption, balance tracking, and conversions.

**Location**: `services/token-manager/`

### 4. Billing Service
Tracks usage, generates invoices, processes payments, and manages revenue sharing.

**Location**: `services/billing/`

### 5. Data Center Connector
Abstraction layer for connecting to different data center APIs and managing resources.

**Location**: `services/data-center-connector/`

## Communication Patterns

- **Synchronous**: REST APIs for request/response operations
- **Asynchronous**: Message queues (RabbitMQ/Kafka) for event-driven operations
- **Service Discovery**: Kubernetes service discovery or Consul

## Technology Stack

- **Language**: Python 3.11+ (FastAPI) or Node.js/TypeScript (Express)
- **Database**: PostgreSQL for transactional data
- **Cache**: Redis for real-time state and caching
- **Message Queue**: RabbitMQ or Apache Kafka
- **Container**: Docker with Kubernetes orchestration

## Development Setup

See individual service README files for setup instructions.

