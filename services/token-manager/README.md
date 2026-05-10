# Token Manager Service

## Overview

The Token Manager Service handles all compute credit operations including issuance, redemption, balance tracking, conversions, and expiration management.

## Key Features

1. **Token Issuance**: Purchase, subscription allocation, promotions
2. **Token Redemption**: Job reservation and consumption
3. **Balance Management**: Track active, reserved, and consumed balances
4. **Token Conversion**: Convert between GPU tiers and token types
5. **Expiration Handling**: Automated expiration and notifications
6. **Transaction History**: Complete audit trail of all token operations

## API Endpoints

### Get Balance
```http
GET /api/v1/tokens/balance
Authorization: Bearer {api_key}
```

### Purchase Tokens
```http
POST /api/v1/tokens/purchase
Content-Type: application/json

{
  "amount": 100.0,
  "paymentMethod": "stripe",
  "paymentToken": "tok_xxx"
}
```

### Reserve Tokens
```http
POST /api/v1/tokens/reserve
Content-Type: application/json

{
  "jobId": "job-123",
  "amount": 50.0,
  "estimatedDuration": 2.5,
  "gpuType": "A100"
}
```

### Consume Tokens
```http
POST /api/v1/tokens/consume
Content-Type: application/json

{
  "jobId": "job-123",
  "actualHours": 2.3,
  "gpuType": "A100"
}
```

## Token Lifecycle

See [docs/TOKEN_SYSTEM.md](../../docs/TOKEN_SYSTEM.md) for detailed token system design.

## Implementation

See `services/token-manager/src/` for implementation details.

