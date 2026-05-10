"""
GPU Compute Marketplace Platform Simulator
Demonstrates the trading platform with mock data and interactions
"""

import time
import random
from datetime import datetime, timedelta
from typing import Dict, List
from dataclasses import dataclass, asdict
import json


@dataclass
class GPUResource:
    """Mock GPU resource"""
    id: str
    data_center_id: str
    gpu_type: str
    available: bool
    price_per_hour: float
    location: str
    tier: str
    current_load: float


@dataclass
class ComputeJob:
    """Mock compute job"""
    id: str
    user_id: str
    status: str
    gpu_type: str
    tokens_reserved: float
    tokens_consumed: float
    created_at: datetime
    started_at: datetime = None
    completed_at: datetime = None


@dataclass
class TokenTransaction:
    """Mock token transaction"""
    id: str
    user_id: str
    type: str
    amount: float
    balance_after: float
    timestamp: datetime


class PlatformSimulator:
    """Simulates the GPU Compute Marketplace Platform"""
    
    def __init__(self):
        self.users = {}
        self.resources = self._generate_resources()
        self.jobs = []
        self.transactions = []
        self.token_balances = {}
        
    def _generate_resources(self) -> List[GPUResource]:
        """Generate mock GPU resources"""
        resources = []
        gpu_types = ["A100", "H100", "V100", "RTX4090"]
        locations = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]
        tiers = ["on-demand", "spot", "reserved"]
        
        for i in range(20):
            resources.append(GPUResource(
                id=f"gpu-{i+1}",
                data_center_id=f"dc-{(i % 4) + 1}",
                gpu_type=random.choice(gpu_types),
                available=random.random() > 0.3,  # 70% available
                price_per_hour=round(random.uniform(1.5, 5.0), 2),
                location=random.choice(locations),
                tier=random.choice(tiers),
                current_load=random.uniform(0.0, 0.9)
            ))
        
        return resources
    
    def create_user(self, user_id: str, initial_balance: float = 0.0):
        """Create a new user"""
        self.users[user_id] = {
            "id": user_id,
            "created_at": datetime.now()
        }
        self.token_balances[user_id] = initial_balance
        return self.token_balances[user_id]
    
    def purchase_tokens(self, user_id: str, amount: float) -> Dict:
        """Simulate token purchase"""
        if user_id not in self.token_balances:
            self.create_user(user_id)
        
        self.token_balances[user_id] += amount
        
        transaction = TokenTransaction(
            id=f"tx-{len(self.transactions) + 1}",
            user_id=user_id,
            type="purchase",
            amount=amount,
            balance_after=self.token_balances[user_id],
            timestamp=datetime.now()
        )
        self.transactions.append(transaction)
        
        return {
            "transaction_id": transaction.id,
            "amount": amount,
            "new_balance": self.token_balances[user_id]
        }
    
    def find_matches(self, gpu_type: str, max_price: float = None) -> List[Dict]:
        """Find matching GPU resources"""
        matches = []
        for resource in self.resources:
            if (resource.gpu_type == gpu_type and 
                resource.available and 
                resource.current_load < 0.9):
                if max_price is None or resource.price_per_hour <= max_price:
                    matches.append({
                        "resource_id": resource.id,
                        "gpu_type": resource.gpu_type,
                        "price_per_hour": resource.price_per_hour,
                        "location": resource.location,
                        "tier": resource.tier,
                        "data_center": resource.data_center_id
                    })
        
        # Sort by price
        matches.sort(key=lambda x: x["price_per_hour"])
        return matches
    
    def submit_job(self, user_id: str, gpu_type: str, estimated_hours: float) -> Dict:
        """Simulate job submission"""
        if user_id not in self.token_balances:
            self.create_user(user_id)
        
        # Find best match
        matches = self.find_matches(gpu_type)
        if not matches:
            return {"error": "No available resources"}
        
        best_match = matches[0]
        tokens_needed = best_match["price_per_hour"] * estimated_hours
        
        if self.token_balances[user_id] < tokens_needed:
            return {"error": f"Insufficient balance. Need {tokens_needed} CC, have {self.token_balances[user_id]} CC"}
        
        # Reserve tokens
        self.token_balances[user_id] -= tokens_needed
        
        # Create job
        job = ComputeJob(
            id=f"job-{len(self.jobs) + 1}",
            user_id=user_id,
            status="queued",
            gpu_type=gpu_type,
            tokens_reserved=tokens_needed,
            tokens_consumed=0.0,
            created_at=datetime.now()
        )
        self.jobs.append(job)
        
        # Record transaction
        transaction = TokenTransaction(
            id=f"tx-{len(self.transactions) + 1}",
            user_id=user_id,
            type="reservation",
            amount=-tokens_needed,
            balance_after=self.token_balances[user_id],
            timestamp=datetime.now()
        )
        self.transactions.append(transaction)
        
        return {
            "job_id": job.id,
            "status": job.status,
            "resource": best_match,
            "tokens_reserved": tokens_needed,
            "balance_remaining": self.token_balances[user_id]
        }
    
    def get_balance(self, user_id: str) -> Dict:
        """Get token balance"""
        if user_id not in self.token_balances:
            return {"active": 0.0, "reserved": 0.0, "total": 0.0}
        
        # Calculate reserved tokens
        reserved = sum(
            job.tokens_reserved - job.tokens_consumed
            for job in self.jobs
            if job.user_id == user_id and job.status in ["queued", "running"]
        )
        
        return {
            "active": self.token_balances[user_id] - reserved,
            "reserved": reserved,
            "total": self.token_balances[user_id]
        }
    
    def get_stats(self) -> Dict:
        """Get platform statistics"""
        total_resources = len(self.resources)
        available_resources = sum(1 for r in self.resources if r.available)
        total_jobs = len(self.jobs)
        active_jobs = sum(1 for j in self.jobs if j.status in ["queued", "running"])
        total_tokens = sum(self.token_balances.values())
        total_transactions = len(self.transactions)
        
        return {
            "resources": {
                "total": total_resources,
                "available": available_resources,
                "utilization": round((total_resources - available_resources) / total_resources * 100, 2) if total_resources > 0 else 0
            },
            "jobs": {
                "total": total_jobs,
                "active": active_jobs,
                "completed": sum(1 for j in self.jobs if j.status == "completed")
            },
            "tokens": {
                "total_circulation": round(total_tokens, 2),
                "total_transactions": total_transactions
            },
            "users": len(self.users)
        }
    
    def simulate_trading_session(self):
        """Simulate a complete trading session"""
        print("=" * 60)
        print("GPU COMPUTE MARKETPLACE - TRADING SIMULATION")
        print("=" * 60)
        print()
        
        # Create users
        user1 = "user-alice"
        user2 = "user-bob"
        self.create_user(user1, 500.0)
        self.create_user(user2, 300.0)
        
        print(f"✅ Created users: {user1} (500 CC), {user2} (300 CC)")
        print()
        
        # Show available resources
        print("📊 Available GPU Resources:")
        print("-" * 60)
        for resource in self.resources[:5]:
            status = "✅ Available" if resource.available else "❌ Busy"
            print(f"{resource.id}: {resource.gpu_type} @ {resource.location} - "
                  f"${resource.price_per_hour}/hr ({resource.tier}) - {status}")
        print()
        
        # User 1 purchases more tokens
        print(f"💰 {user1} purchases 200 CC")
        purchase = self.purchase_tokens(user1, 200.0)
        print(f"   Transaction: {purchase['transaction_id']}")
        print(f"   New Balance: {purchase['new_balance']} CC")
        print()
        
        # User 1 submits a job
        print(f"🚀 {user1} submits a job (A100, 2 hours)")
        job1 = self.submit_job(user1, "A100", 2.0)
        if "error" not in job1:
            print(f"   Job ID: {job1['job_id']}")
            print(f"   Resource: {job1['resource']['resource_id']} @ {job1['resource']['location']}")
            print(f"   Cost: {job1['tokens_reserved']} CC")
            print(f"   Balance Remaining: {job1['balance_remaining']} CC")
        else:
            print(f"   ❌ Error: {job1['error']}")
        print()
        
        # User 2 submits a job
        print(f"🚀 {user2} submits a job (H100, 1.5 hours)")
        job2 = self.submit_job(user2, "H100", 1.5)
        if "error" not in job2:
            print(f"   Job ID: {job2['job_id']}")
            print(f"   Resource: {job2['resource']['resource_id']} @ {job2['resource']['location']}")
            print(f"   Cost: {job2['tokens_reserved']} CC")
            print(f"   Balance Remaining: {job2['balance_remaining']} CC")
        else:
            print(f"   ❌ Error: {job2['error']}")
        print()
        
        # Show balances
        print("💳 Token Balances:")
        print("-" * 60)
        for user_id in [user1, user2]:
            balance = self.get_balance(user_id)
            print(f"{user_id}:")
            print(f"   Active: {balance['active']} CC")
            print(f"   Reserved: {balance['reserved']} CC")
            print(f"   Total: {balance['total']} CC")
        print()
        
        # Show platform stats
        stats = self.get_stats()
        print("📈 Platform Statistics:")
        print("-" * 60)
        print(f"Resources: {stats['resources']['available']}/{stats['resources']['total']} available "
              f"({stats['resources']['utilization']}% utilization)")
        print(f"Jobs: {stats['jobs']['active']} active, {stats['jobs']['completed']} completed")
        print(f"Total Tokens: {stats['tokens']['total_circulation']} CC")
        print(f"Users: {stats['users']}")
        print()
        
        print("=" * 60)
        print("Simulation Complete!")
        print("=" * 60)


if __name__ == "__main__":
    simulator = PlatformSimulator()
    simulator.simulate_trading_session()








