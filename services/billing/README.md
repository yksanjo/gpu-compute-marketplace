# Billing Service

## Overview

The Billing Service tracks usage, generates invoices, processes payments, and manages revenue sharing with data centers.

## Key Features

1. **Usage Metering**: Track actual GPU-hours consumed
2. **Billing Cycles**: Generate invoices for subscriptions and usage
3. **Payment Processing**: Integrate with payment gateways
4. **Revenue Sharing**: Calculate and distribute revenue to data centers
5. **Invoice Generation**: Generate PDF invoices
6. **Usage Analytics**: Provide usage reports and analytics

## API Endpoints

### Get Usage
```http
GET /api/v1/billing/usage?startDate=2024-01-01&endDate=2024-01-31
```

### Get Invoices
```http
GET /api/v1/billing/invoices
```

### Get Revenue Share
```http
GET /api/v1/billing/revenue-share?dataCenterId=dc-123&month=2024-01
```

## Revenue Sharing

The platform uses a revenue share model:
- **Platform Commission**: 20-30% of revenue
- **Data Center Share**: 70-80% of revenue

Revenue is calculated monthly based on actual GPU-hours consumed.

## Implementation

See `services/billing/src/` for implementation details.

