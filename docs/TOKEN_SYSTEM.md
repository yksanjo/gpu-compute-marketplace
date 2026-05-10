# Compute Token System Design

## Overview

The platform uses a fungible token system called **Compute Credits (CC)** to represent GPU compute time. Tokens can be purchased, traded, and redeemed for actual GPU compute resources.

## Token Unit Definition

### Base Unit: Compute Credit (CC)
- **1 CC = 1 GPU-hour** of standard GPU compute
- Standard GPU: NVIDIA A100 40GB (baseline)
- All other GPU types have conversion rates relative to A100

### GPU Conversion Rates

| GPU Type | Conversion Rate | Notes |
|----------|----------------|-------|
| NVIDIA A100 40GB | 1.0 CC/hour | Baseline |
| NVIDIA A100 80GB | 1.2 CC/hour | More memory |
| NVIDIA H100 80GB | 1.5 CC/hour | Next-gen performance |
| NVIDIA H100 120GB | 1.8 CC/hour | More memory |
| NVIDIA V100 32GB | 0.7 CC/hour | Older generation |
| NVIDIA RTX 4090 | 0.5 CC/hour | Consumer GPU |
| AMD MI250X | 1.1 CC/hour | Alternative architecture |
| AMD MI300X | 1.4 CC/hour | Latest AMD |

**Formula**: `Actual Cost = Base Hours × Conversion Rate × Tier Multiplier`

## Token Types

### 1. Prepaid Credits
- **Purchase**: Users buy credits upfront
- **Pricing**: Volume discounts available
- **Expiration**: 12 months from purchase (configurable)
- **Refund**: Partial refunds available for unused credits
- **Use Case**: Pay-as-you-go model

### 2. Subscription Tokens
- **Allocation**: Monthly token allocation
- **Pricing**: Reduced rate (20-30% discount)
- **Expiration**: End of billing cycle
- **Rollover**: Up to 20% can roll over to next month
- **Use Case**: Predictable monthly workloads

### 3. Spot Tokens
- **Allocation**: Time-limited tokens from spot market
- **Pricing**: 50-70% discount
- **Expiration**: 24-48 hours from allocation
- **Refund**: No refunds (use-it-or-lose-it)
- **Use Case**: Flexible, interruptible workloads

### 4. Enterprise Tokens
- **Allocation**: Custom allocation based on contract
- **Pricing**: Negotiated rates
- **Expiration**: Per contract terms
- **Features**: Priority scheduling, SLA guarantees
- **Use Case**: Enterprise customers with SLAs

## Token Lifecycle

```
Purchase/Allocation → Active Balance → Reservation → Consumption → Expiration
```

### States
1. **Active**: Available for use
2. **Reserved**: Allocated to a job but not yet consumed
3. **Consumed**: Used for compute (non-refundable)
4. **Expired**: Past expiration date (non-refundable)
5. **Refunded**: Returned to user (prepaid only)

## Token Operations

### Issuance
- **Purchase**: User buys credits via payment gateway
- **Subscription**: Monthly allocation on billing date
- **Promotion**: Free credits for marketing
- **Referral**: Credits for referring new users

### Redemption
- **Job Submission**: Tokens reserved when job is submitted
- **Consumption**: Tokens consumed based on actual GPU-hours used
- **Refund**: Unused reserved tokens returned after job completion

### Conversion
- **GPU Tier Upgrade**: Pay difference in conversion rates
- **GPU Tier Downgrade**: Receive credit for difference
- **Tier Transfer**: Convert between token types (with fees)

## Pricing Model

### Base Pricing (On-Demand)
- **A100 40GB**: $3.00/hour = 3.0 CC/hour
- **H100 80GB**: $4.50/hour = 4.5 CC/hour
- **V100 32GB**: $2.10/hour = 2.1 CC/hour

### Volume Discounts
- **0-100 CC**: No discount
- **101-1,000 CC**: 5% discount
- **1,001-10,000 CC**: 10% discount
- **10,001+ CC**: 15% discount

### Tier Multipliers
- **On-Demand**: 1.0x (baseline)
- **Reserved (1-year)**: 0.6x (40% discount)
- **Spot**: 0.3x (70% discount)
- **Subscription**: 0.8x (20% discount)

## Token Economics

### Supply
- **Total Supply**: Unlimited (fiat-backed)
- **Circulation**: Tokens in user accounts
- **Reserved**: Tokens allocated to active jobs
- **Consumed**: Tokens used for compute (removed from circulation)

### Demand Drivers
- AI/ML training workloads
- Inference serving
- Rendering jobs
- Research compute
- Development and testing

### Price Stability
- **Fiat Peg**: Tokens backed by fiat currency
- **No Speculation**: Tokens are utility tokens, not investment vehicles
- **Refund Policy**: Unused prepaid credits can be refunded (minus fees)

## API Design

### Token Balance
```typescript
GET /api/v1/tokens/balance
Response: {
  active: number,
  reserved: number,
  total: number,
  expiresAt?: Date
}
```

### Token Purchase
```typescript
POST /api/v1/tokens/purchase
Request: {
  amount: number,  // CC to purchase
  paymentMethod: string
}
Response: {
  transactionId: string,
  newBalance: number
}
```

### Token Reservation
```typescript
POST /api/v1/tokens/reserve
Request: {
  jobId: string,
  amount: number,  // CC to reserve
  estimatedDuration: number  // hours
}
Response: {
  reservationId: string,
  reservedAmount: number,
  expiresAt: Date
}
```

### Token Consumption
```typescript
POST /api/v1/tokens/consume
Request: {
  jobId: string,
  actualHours: number,
  gpuType: string
}
Response: {
  consumed: number,
  refunded: number,
  newBalance: number
}
```

## Database Schema

See [database/schemas/tokens.sql](../database/schemas/tokens.sql) for detailed schema.

## Security Considerations

1. **Token Theft Prevention**
   - API key authentication
   - Rate limiting on token operations
   - Transaction logging and monitoring
   - Fraud detection algorithms

2. **Double Spending Prevention**
   - Atomic transactions for reservations
   - Database-level constraints
   - Distributed locking for concurrent operations

3. **Expiration Handling**
   - Automated expiration checks
   - Grace period notifications (7 days, 3 days, 1 day)
   - Automatic refunds for unused prepaid credits (optional)

## Reporting and Analytics

### User Metrics
- Total tokens purchased
- Total tokens consumed
- Average cost per GPU-hour
- Token utilization rate
- Expired token value

### Platform Metrics
- Total token supply
- Token velocity (tokens consumed per day)
- Revenue from token sales
- Average token lifetime
- Conversion rates between tiers

