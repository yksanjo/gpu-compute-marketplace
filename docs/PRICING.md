# Pricing Model and Revenue Sharing

## Overview

The GPU Compute Marketplace uses a token-based pricing model with flexible pricing tiers and revenue sharing with data center partners.

## Token Pricing

### Base Pricing (On-Demand)

| GPU Type | Price per Hour (USD) | Compute Credits per Hour |
|----------|---------------------|-------------------------|
| NVIDIA A100 40GB | $3.00 | 3.0 CC |
| NVIDIA A100 80GB | $3.60 | 3.6 CC |
| NVIDIA H100 80GB | $4.50 | 4.5 CC |
| NVIDIA H100 120GB | $5.40 | 5.4 CC |
| NVIDIA V100 32GB | $2.10 | 2.1 CC |
| NVIDIA RTX 4090 | $1.50 | 1.5 CC |
| AMD MI250X | $3.30 | 3.3 CC |
| AMD MI300X | $4.20 | 4.2 CC |

**Note**: 1 Compute Credit (CC) = $1.00 USD

### Pricing Tiers

#### 1. On-Demand
- **Pricing**: Standard hourly rates (see above)
- **Availability**: Immediate
- **Preemption**: No preemption
- **Use Case**: Production workloads, time-sensitive jobs
- **Discount**: None

#### 2. Reserved Instances
- **Pricing**: 30-40% discount from on-demand
- **Commitment**: 1-year term
- **Availability**: Guaranteed capacity
- **Preemption**: No preemption
- **Use Case**: Predictable, long-running workloads
- **Discount**: 30-40% off on-demand

#### 3. Spot Instances
- **Pricing**: 50-70% discount from on-demand
- **Availability**: Best effort
- **Preemption**: Can be preempted with 5-minute notice
- **Use Case**: Flexible, fault-tolerant workloads
- **Discount**: 50-70% off on-demand

#### 4. Subscription
- **Pricing**: 20-30% discount from on-demand
- **Allocation**: Monthly token allocation
- **Availability**: Priority scheduling
- **Preemption**: No preemption
- **Use Case**: Regular monthly workloads
- **Discount**: 20-30% off on-demand

### Volume Discounts

When purchasing compute credits:

| Purchase Amount | Discount |
|----------------|----------|
| 0 - 100 CC | 0% |
| 101 - 1,000 CC | 5% |
| 1,001 - 10,000 CC | 10% |
| 10,001+ CC | 15% |

## Revenue Sharing Model

### Standard Revenue Share

The platform uses a revenue share model with data center partners:

- **Platform Commission**: 20-30% of revenue
- **Data Center Share**: 70-80% of revenue

### Revenue Calculation

```
Monthly Revenue = Total GPU-hours consumed × Average price per hour
Platform Share = Monthly Revenue × Commission Rate (20-30%)
Data Center Share = Monthly Revenue × (1 - Commission Rate)
```

### Example

If a data center provides 1,000 GPU-hours in a month at an average price of $3.00/hour:

- **Total Revenue**: $3,000
- **Platform Share (25%)**: $750
- **Data Center Share (75%)**: $2,250

### Revenue Share Variations

#### Tier 1 Partners (High Volume)
- **Commission**: 20%
- **Requirements**: >10,000 GPU-hours/month
- **Benefits**: Priority support, co-marketing

#### Tier 2 Partners (Standard)
- **Commission**: 25%
- **Requirements**: 1,000-10,000 GPU-hours/month
- **Benefits**: Standard support

#### Tier 3 Partners (Small)
- **Commission**: 30%
- **Requirements**: <1,000 GPU-hours/month
- **Benefits**: Basic support

## Pricing Strategy

### Market Positioning

- **Competitive with**: AWS EC2 GPU instances, Google Cloud GPUs, Azure GPU VMs
- **Value Proposition**: 
  - Lower prices through underutilized capacity
  - Token-based model for flexibility
  - Spot market for cost optimization
  - Multi-provider aggregation

### Dynamic Pricing

For spot instances, pricing can vary based on:
- **Demand**: Higher demand = higher prices
- **Supply**: More available capacity = lower prices
- **Time of Day**: Peak hours may have higher prices
- **Geographic Location**: Regional price variations

### Price Guarantees

- **On-Demand**: Fixed prices (may change with 30-day notice)
- **Reserved**: Locked prices for commitment term
- **Spot**: Variable prices (no guarantees)
- **Subscription**: Fixed monthly allocation price

## Payment Terms

### For Customers

- **Prepaid Credits**: Pay upfront, use as needed
- **Subscription**: Monthly billing
- **Pay-as-you-go**: Post-paid for enterprise customers
- **Payment Methods**: Credit card, wire transfer, ACH

### For Data Centers

- **Payment Frequency**: Monthly
- **Payment Terms**: Net 30 days
- **Payment Method**: Wire transfer or ACH
- **Currency**: USD (or local currency per agreement)

## Cost Optimization Tips

### For Customers

1. **Use Spot Instances**: 50-70% savings for fault-tolerant workloads
2. **Reserve Capacity**: 30-40% savings for predictable workloads
3. **Volume Purchases**: Up to 15% discount on credit purchases
4. **Right-Size Jobs**: Match GPU type to workload requirements
5. **Monitor Usage**: Track consumption to optimize spending

### For Data Centers

1. **Increase Utilization**: Higher utilization = more revenue
2. **Tier 1 Partnership**: Lower commission at higher volumes
3. **Peak Hours**: Higher prices during peak demand
4. **Long-term Contracts**: Guaranteed revenue with reserved instances

## Billing and Invoicing

### Customer Billing

- **Invoices**: Generated monthly or per transaction
- **Usage Reports**: Detailed breakdown of GPU-hours consumed
- **Payment History**: Complete transaction history
- **Tax Handling**: Automatic tax calculation where applicable

### Data Center Payments

- **Revenue Reports**: Monthly revenue statements
- **Usage Breakdown**: Detailed usage by customer and GPU type
- **Payment Processing**: Automated payment processing
- **Reconciliation**: Monthly reconciliation reports

## Pricing Transparency

- **Public Pricing**: All on-demand prices publicly available
- **Price Calculator**: Online calculator for cost estimation
- **No Hidden Fees**: Transparent pricing with no surprise charges
- **Price History**: Track price changes over time

## Future Pricing Considerations

- **Market-Based Pricing**: Real-time market pricing for spot instances
- **Bundled Services**: Discounts for bundled compute + storage
- **Enterprise Contracts**: Custom pricing for large customers
- **Regional Pricing**: Adjust prices based on regional costs

