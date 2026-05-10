# Scheduler Service

## Overview

The Scheduler Service manages job queues, priority scheduling, resource allocation, and job lifecycle management. It coordinates with the Matching Engine to assign jobs to resources and handles preemption for spot instances.

## Key Features

1. **Job Queue Management**: Multiple priority queues (urgent, high, normal, low)
2. **Resource Allocation**: Assign jobs to matched GPU resources
3. **Preemption Handling**: Graceful preemption for spot instances
4. **Checkpointing**: Support for job checkpointing and resumption
5. **Deadline Management**: Schedule jobs based on deadlines
6. **Fair Scheduling**: Ensure fair resource distribution

## Job States

```
queued → scheduled → running → completed
                ↓
            failed/preempted
```

## API Endpoints

### Submit Job
```http
POST /api/v1/scheduler/jobs
Content-Type: application/json

{
  "userId": "user-123",
  "gpuRequirements": {
    "type": "A100",
    "count": 4,
    "memory": 40
  },
  "containerImage": "docker.io/user/model-training:latest",
  "priority": "normal",
  "deadline": "2024-12-31T23:59:59Z",
  "estimatedDuration": 2.5
}
```

### Get Job Status
```http
GET /api/v1/scheduler/jobs/{jobId}
```

### Cancel Job
```http
DELETE /api/v1/scheduler/jobs/{jobId}
```

## Scheduling Algorithms

### Priority-Based Scheduling
- Urgent: Immediate scheduling
- High: Scheduled within 5 minutes
- Normal: Scheduled within 30 minutes
- Low: Scheduled when capacity available

### Fair Share Scheduling
- Distribute resources fairly across users
- Prevent resource hoarding
- Implement quotas and limits

### Preemption Policy
- Spot jobs can be preempted by on-demand/reserved jobs
- 5-minute grace period for checkpointing
- Automatic rescheduling of preempted jobs

## Implementation

See `services/scheduler/src/` for implementation details.

