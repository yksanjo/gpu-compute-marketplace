# Platform Simulator

## Overview

The simulator demonstrates how the GPU Compute Marketplace Platform works with mock data and interactions.

## Running the Simulator

### Basic Simulation

```bash
cd simulator
python demo.py
```

This will run a complete trading session simulation showing:
- User creation
- Token purchases
- Job submissions
- Resource matching
- Balance tracking
- Platform statistics

## Interactive Simulation

### Using Python REPL

```python
from demo import PlatformSimulator

# Create simulator
sim = PlatformSimulator()

# Create a user
sim.create_user("user-123", initial_balance=500.0)

# Purchase tokens
sim.purchase_tokens("user-123", 200.0)

# Find available resources
matches = sim.find_matches("A100", max_price=4.0)
print(f"Found {len(matches)} matching resources")

# Submit a job
job = sim.submit_job("user-123", "A100", estimated_hours=2.0)
print(f"Job submitted: {job['job_id']}")

# Check balance
balance = sim.get_balance("user-123")
print(f"Balance: {balance}")

# Get platform stats
stats = sim.get_stats()
print(f"Platform stats: {stats}")
```

## Example Output

```
============================================================
GPU COMPUTE MARKETPLACE - TRADING SIMULATION
============================================================

✅ Created users: user-alice (500 CC), user-bob (300 CC)

📊 Available GPU Resources:
------------------------------------------------------------
gpu-1: A100 @ us-east-1 - $3.00/hr (on-demand) - ✅ Available
gpu-2: H100 @ us-west-2 - $4.50/hr (on-demand) - ✅ Available
...

💰 user-alice purchases 200 CC
   Transaction: tx-1
   New Balance: 700.0 CC

🚀 user-alice submits a job (A100, 2 hours)
   Job ID: job-1
   Resource: gpu-1 @ us-east-1
   Cost: 6.0 CC
   Balance Remaining: 694.0 CC

💳 Token Balances:
------------------------------------------------------------
user-alice:
   Active: 694.0 CC
   Reserved: 6.0 CC
   Total: 700.0 CC

📈 Platform Statistics:
------------------------------------------------------------
Resources: 14/20 available (30.0% utilization)
Jobs: 2 active, 0 completed
Total Tokens: 1000.0 CC
Users: 2
```

## Integration with UI

The simulator can be integrated with the web dashboard by:

1. Converting the Python simulator to a REST API
2. Connecting the dashboard to the API
3. Using WebSockets for real-time updates

## Extending the Simulator

You can extend the simulator by:

- Adding more realistic resource generation
- Implementing job execution simulation
- Adding time-based events
- Simulating multiple users concurrently
- Adding market dynamics (price changes, demand fluctuations)








