"""
Token Manager Service
Handles compute credit issuance, redemption, and balance tracking.
"""

from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import logging
import uuid

logger = logging.getLogger(__name__)


class TokenType(Enum):
    """Token allocation types"""
    PREPAID = "prepaid"
    SUBSCRIPTION = "subscription"
    SPOT = "spot"
    ENTERPRISE = "enterprise"


class TransactionType(Enum):
    """Token transaction types"""
    PURCHASE = "purchase"
    SUBSCRIPTION = "subscription"
    RESERVATION = "reservation"
    CONSUMPTION = "consumption"
    REFUND = "refund"
    EXPIRATION = "expiration"
    PROMOTION = "promotion"


# GPU conversion rates (relative to A100 40GB = 1.0)
GPU_CONVERSION_RATES = {
    "A100-40GB": 1.0,
    "A100-80GB": 1.2,
    "H100-80GB": 1.5,
    "H100-120GB": 1.8,
    "V100-32GB": 0.7,
    "RTX4090": 0.5,
    "MI250X": 1.1,
    "MI300X": 1.4,
}


@dataclass
class TokenAccount:
    """User token account"""
    user_id: str
    account_id: str
    active_balance: float = 0.0
    reserved_balance: float = 0.0
    total_purchased: float = 0.0
    total_consumed: float = 0.0


@dataclass
class TokenAllocation:
    """Token allocation with expiration"""
    id: str
    account_id: str
    type: TokenType
    amount: float
    remaining: float
    expires_at: Optional[datetime] = None
    tier: Optional[str] = None


@dataclass
class TokenReservation:
    """Token reservation for a job"""
    id: str
    account_id: str
    job_id: str
    amount: float
    gpu_type: str
    estimated_hours: float
    status: str = "active"  # active, consumed, refunded, expired
    expires_at: Optional[datetime] = None


class TokenManager:
    """Core token manager implementation"""
    
    def __init__(self):
        self.accounts: Dict[str, TokenAccount] = {}
        self.allocations: Dict[str, TokenAllocation] = {}
        self.reservations: Dict[str, TokenReservation] = {}
        self.transactions: List[Dict] = []
    
    def get_balance(self, user_id: str) -> Optional[Dict]:
        """Get token balance for a user"""
        account = self.accounts.get(user_id)
        if not account:
            return None
        
        # Find earliest expiration
        expires_at = None
        for allocation in self.allocations.values():
            if allocation.account_id == account.account_id and allocation.remaining > 0:
                if expires_at is None or (allocation.expires_at and allocation.expires_at < expires_at):
                    expires_at = allocation.expires_at
        
        return {
            "active": account.active_balance,
            "reserved": account.reserved_balance,
            "total": account.active_balance + account.reserved_balance,
            "expiresAt": expires_at.isoformat() if expires_at else None
        }
    
    def purchase_tokens(
        self,
        user_id: str,
        amount: float,
        payment_method: str,
        payment_token: Optional[str] = None
    ) -> Dict:
        """Purchase compute credits"""
        # Get or create account
        account = self.accounts.get(user_id)
        if not account:
            account = TokenAccount(
                user_id=user_id,
                account_id=str(uuid.uuid4())
            )
            self.accounts[user_id] = account
        
        # Calculate price (simplified - in production, integrate with payment gateway)
        price_per_cc = 1.0  # $1 per compute credit
        total_price = amount * price_per_cc
        
        # Apply volume discount
        discount = self._calculate_volume_discount(amount)
        final_price = total_price * (1 - discount)
        
        # Add tokens to account
        account.active_balance += amount
        account.total_purchased += amount
        
        # Create allocation (prepaid tokens expire in 12 months)
        allocation = TokenAllocation(
            id=str(uuid.uuid4()),
            account_id=account.account_id,
            type=TokenType.PREPAID,
            amount=amount,
            remaining=amount,
            expires_at=datetime.utcnow() + timedelta(days=365),
            tier="on-demand"
        )
        self.allocations[allocation.id] = allocation
        
        # Record transaction
        transaction_id = self._record_transaction(
            user_id, account.account_id, TransactionType.PURCHASE,
            amount, {"payment_method": payment_method, "price": final_price}
        )
        
        logger.info(f"User {user_id} purchased {amount} CC")
        
        return {
            "transactionId": transaction_id,
            "amount": amount,
            "newBalance": account.active_balance
        }
    
    def reserve_tokens(
        self,
        user_id: str,
        job_id: str,
        amount: float,
        estimated_duration: float,
        gpu_type: str
    ) -> Dict:
        """Reserve tokens for a job"""
        account = self.accounts.get(user_id)
        if not account:
            raise ValueError("Account not found")
        
        # Check sufficient balance
        if account.active_balance < amount:
            raise ValueError(f"Insufficient balance: {account.active_balance} < {amount}")
        
        # Calculate actual cost based on GPU type
        conversion_rate = GPU_CONVERSION_RATES.get(gpu_type, 1.0)
        actual_cost = amount * conversion_rate
        
        if account.active_balance < actual_cost:
            raise ValueError(f"Insufficient balance for GPU type {gpu_type}")
        
        # Reserve tokens
        account.active_balance -= actual_cost
        account.reserved_balance += actual_cost
        
        # Create reservation
        reservation = TokenReservation(
            id=str(uuid.uuid4()),
            account_id=account.account_id,
            job_id=job_id,
            amount=actual_cost,
            gpu_type=gpu_type,
            estimated_hours=estimated_duration,
            status="active",
            expires_at=datetime.utcnow() + timedelta(hours=estimated_duration * 2)  # 2x buffer
        )
        self.reservations[reservation.id] = reservation
        
        # Record transaction
        transaction_id = self._record_transaction(
            user_id, account.account_id, TransactionType.RESERVATION,
            -actual_cost, {"job_id": job_id, "gpu_type": gpu_type}
        )
        
        logger.info(f"Reserved {actual_cost} CC for job {job_id}")
        
        return {
            "reservationId": reservation.id,
            "reservedAmount": actual_cost,
            "expiresAt": reservation.expires_at.isoformat()
        }
    
    def consume_tokens(
        self,
        user_id: str,
        job_id: str,
        actual_hours: float,
        gpu_type: str
    ) -> Dict:
        """Consume tokens for completed job"""
        account = self.accounts.get(user_id)
        if not account:
            raise ValueError("Account not found")
        
        # Find reservation
        reservation = None
        for r in self.reservations.values():
            if r.job_id == job_id and r.status == "active":
                reservation = r
                break
        
        if not reservation:
            raise ValueError(f"No active reservation found for job {job_id}")
        
        # Calculate actual cost
        conversion_rate = GPU_CONVERSION_RATES.get(gpu_type, 1.0)
        actual_cost = actual_hours * conversion_rate
        
        # Consume from reservation
        consumed = min(actual_cost, reservation.amount)
        refunded = reservation.amount - consumed
        
        # Update balances
        account.reserved_balance -= reservation.amount
        account.total_consumed += consumed
        if refunded > 0:
            account.active_balance += refunded
        
        # Update reservation
        reservation.status = "consumed"
        
        # Record transaction
        transaction_id = self._record_transaction(
            user_id, account.account_id, TransactionType.CONSUMPTION,
            -consumed, {"job_id": job_id, "actual_hours": actual_hours, "gpu_type": gpu_type}
        )
        
        if refunded > 0:
            self._record_transaction(
                user_id, account.account_id, TransactionType.REFUND,
                refunded, {"job_id": job_id}
            )
        
        logger.info(f"Consumed {consumed} CC for job {job_id}, refunded {refunded} CC")
        
        return {
            "consumed": consumed,
            "refunded": refunded,
            "newBalance": account.active_balance
        }
    
    def _calculate_volume_discount(self, amount: float) -> float:
        """Calculate volume discount percentage"""
        if amount >= 10000:
            return 0.15
        elif amount >= 1000:
            return 0.10
        elif amount >= 100:
            return 0.05
        return 0.0
    
    def _record_transaction(
        self,
        user_id: str,
        account_id: str,
        transaction_type: TransactionType,
        amount: float,
        metadata: Dict
    ) -> str:
        """Record a token transaction"""
        transaction_id = str(uuid.uuid4())
        transaction = {
            "id": transaction_id,
            "user_id": user_id,
            "account_id": account_id,
            "type": transaction_type.value,
            "amount": amount,
            "metadata": metadata,
            "created_at": datetime.utcnow().isoformat()
        }
        self.transactions.append(transaction)
        return transaction_id
    
    def check_expirations(self) -> List[str]:
        """Check and expire old allocations"""
        now = datetime.utcnow()
        expired = []
        
        for allocation in list(self.allocations.values()):
            if allocation.expires_at and allocation.expires_at < now:
                if allocation.remaining > 0:
                    # Expire remaining tokens
                    account = None
                    for acc in self.accounts.values():
                        if acc.account_id == allocation.account_id:
                            account = acc
                            break
                    
                    if account:
                        account.active_balance -= allocation.remaining
                        self._record_transaction(
                            account.user_id, account.account_id,
                            TransactionType.EXPIRATION,
                            -allocation.remaining,
                            {"allocation_id": allocation.id}
                        )
                        expired.append(allocation.id)
                    
                    allocation.remaining = 0
        
        return expired

