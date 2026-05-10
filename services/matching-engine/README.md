# Matching Engine Service

## Overview

The Matching Engine is responsible for finding the best available GPU resources for incoming compute job requests. It considers factors such as:
- GPU type and specifications
- Geographic location
- Current availability
- Pricing (on-demand, reserved, spot)
- Data center capacity
- Network latency

## Architecture

```
Job Request → Matching Engine → Resource Candidates → Optimization Algorithm → Best Match
```

## Key Features

1. **Real-time Matching**: Sub-second matching for urgent jobs
2. **Multi-criteria Optimization**: Balance cost, performance, and location
3. **Load Balancing**: Distribute jobs across data centers
4. **Spot Market Integration**: Match spot jobs to available capacity
5. **Reservation Support**: Handle reserved capacity allocations

## API Endpoints

### Find Matching Resources
```http
POST /api/v1/matching/find
Content-Type: application/json

{
  "gpuRequirements": {
    "type": "A100",
    "count": 4,
    "memory": 40
  },
  "preferences": {
    "maxPrice": 10.0,
    "location": "us-east-1",
    "tier": "spot"
  },
  "urgency": "normal"
}
```

### Get Resource Availability
```http
GET /api/v1/matching/availability?gpuType=A100&location=us-east-1
```

## Matching Algorithm

### Scoring Function
```
Score = (Price Weight × Price Score) + 
        (Performance Weight × Performance Score) + 
        (Location Weight × Location Score) + 
        (Availability Weight × Availability Score)
```

### Optimization Strategies
1. **Cost Optimization**: Lowest price first
2. **Performance Optimization**: Best GPU specs first
3. **Latency Optimization**: Nearest location first
4. **Balanced**: Weighted combination of all factors

## Implementation

See `services/matching-engine/src/` for implementation details.

