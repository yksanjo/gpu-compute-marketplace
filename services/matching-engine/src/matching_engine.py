"""
Matching Engine Service
Matches compute job requests to available GPU resources.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class GPUTier(Enum):
    """GPU pricing tiers"""
    ON_DEMAND = "on-demand"
    RESERVED = "reserved"
    SPOT = "spot"
    SUBSCRIPTION = "subscription"


class Urgency(Enum):
    """Job urgency levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class GPURequirement:
    """GPU requirements for a job"""
    type: str  # e.g., "A100", "H100"
    count: int
    memory: int  # GB
    compute_capability: Optional[str] = None


@dataclass
class MatchingPreferences:
    """User preferences for matching"""
    max_price: Optional[float] = None  # Max price per GPU-hour in CC
    location: Optional[str] = None  # Preferred region
    tier: GPUTier = GPUTier.ON_DEMAND
    data_center_id: Optional[str] = None  # Preferred data center
    min_availability: float = 0.95  # Minimum uptime guarantee


@dataclass
class GPUResource:
    """Available GPU resource"""
    id: str
    data_center_id: str
    gpu_type: str
    available: bool
    current_load: float  # 0.0 to 1.0
    price_per_hour: float  # in compute credits
    location: str
    tier: GPUTier
    specs: Dict
    availability_score: float  # Historical uptime
    network_latency: Optional[float] = None  # ms to user location


@dataclass
class MatchResult:
    """Result of matching operation"""
    resource_id: str
    data_center_id: str
    gpu_type: str
    count: int
    price_per_hour: float
    total_estimated_cost: float
    estimated_availability: float
    match_score: float
    location: str


class MatchingEngine:
    """Core matching engine implementation"""
    
    def __init__(self):
        self.resources: Dict[str, GPUResource] = {}
        self.optimization_weights = {
            'price': 0.4,
            'performance': 0.3,
            'location': 0.2,
            'availability': 0.1
        }
    
    def find_matches(
        self,
        requirements: GPURequirement,
        preferences: MatchingPreferences,
        urgency: Urgency = Urgency.NORMAL
    ) -> List[MatchResult]:
        """
        Find matching GPU resources for a job request.
        
        Args:
            requirements: GPU requirements
            preferences: User preferences
            urgency: Job urgency level
            
        Returns:
            List of match results, sorted by match score
        """
        # Filter available resources
        candidates = self._filter_resources(requirements, preferences)
        
        if not candidates:
            logger.warning(f"No matching resources found for {requirements.type}")
            return []
        
        # Score and rank candidates
        scored_matches = []
        for resource in candidates:
            score = self._calculate_match_score(
                resource, requirements, preferences, urgency
            )
            
            # Calculate total cost
            total_cost = resource.price_per_hour * requirements.count
            
            match = MatchResult(
                resource_id=resource.id,
                data_center_id=resource.data_center_id,
                gpu_type=resource.gpu_type,
                count=requirements.count,
                price_per_hour=resource.price_per_hour,
                total_estimated_cost=total_cost,
                estimated_availability=resource.availability_score,
                match_score=score,
                location=resource.location
            )
            scored_matches.append(match)
        
        # Sort by match score (highest first)
        scored_matches.sort(key=lambda x: x.match_score, reverse=True)
        
        return scored_matches
    
    def _filter_resources(
        self,
        requirements: GPURequirement,
        preferences: MatchingPreferences
    ) -> List[GPUResource]:
        """Filter resources based on requirements and preferences"""
        candidates = []
        
        for resource in self.resources.values():
            # Check availability
            if not resource.available:
                continue
            
            # Check GPU type match
            if resource.gpu_type != requirements.type:
                continue
            
            # Check tier match
            if resource.tier != preferences.tier:
                continue
            
            # Check price constraint
            if preferences.max_price and resource.price_per_hour > preferences.max_price:
                continue
            
            # Check location preference
            if preferences.location and resource.location != preferences.location:
                continue
            
            # Check data center preference
            if preferences.data_center_id and resource.data_center_id != preferences.data_center_id:
                continue
            
            # Check availability score
            if resource.availability_score < preferences.min_availability:
                continue
            
            # Check current load (don't match if overloaded)
            if resource.current_load > 0.9:
                continue
            
            candidates.append(resource)
        
        return candidates
    
    def _calculate_match_score(
        self,
        resource: GPUResource,
        requirements: GPURequirement,
        preferences: MatchingPreferences,
        urgency: Urgency
    ) -> float:
        """Calculate match score for a resource"""
        scores = {}
        
        # Price score (lower is better, normalized to 0-1)
        max_price = preferences.max_price or 100.0
        price_score = 1.0 - min(resource.price_per_hour / max_price, 1.0)
        scores['price'] = price_score
        
        # Performance score (based on GPU specs)
        performance_score = self._calculate_performance_score(resource, requirements)
        scores['performance'] = performance_score
        
        # Location score (lower latency is better)
        location_score = 1.0
        if resource.network_latency:
            # Normalize latency (0-100ms = 1.0, 200ms+ = 0.0)
            location_score = max(0.0, 1.0 - (resource.network_latency / 200.0))
        scores['location'] = location_score
        
        # Availability score (historical uptime)
        availability_score = resource.availability_score
        scores['availability'] = availability_score
        
        # Weighted combination
        total_score = sum(
            self.optimization_weights[key] * scores[key]
            for key in scores
        )
        
        # Adjust for urgency (urgent jobs prioritize availability over price)
        if urgency == Urgency.URGENT:
            total_score = (
                0.2 * scores['price'] +
                0.2 * scores['performance'] +
                0.2 * scores['location'] +
                0.4 * scores['availability']
            )
        elif urgency == Urgency.HIGH:
            total_score = (
                0.3 * scores['price'] +
                0.3 * scores['performance'] +
                0.2 * scores['location'] +
                0.2 * scores['availability']
            )
        
        return total_score
    
    def _calculate_performance_score(
        self,
        resource: GPUResource,
        requirements: GPURequirement
    ) -> float:
        """Calculate performance score based on GPU specs"""
        score = 1.0
        
        # Memory match
        resource_memory = resource.specs.get('memory', 0)
        if resource_memory >= requirements.memory:
            score *= 1.0
        else:
            # Penalize if memory is insufficient
            score *= 0.5
        
        # Compute capability match
        if requirements.compute_capability:
            resource_capability = resource.specs.get('compute_capability', '')
            if resource_capability >= requirements.compute_capability:
                score *= 1.0
            else:
                score *= 0.8
        
        return score
    
    def update_resource(self, resource: GPUResource):
        """Update resource information"""
        self.resources[resource.id] = resource
    
    def remove_resource(self, resource_id: str):
        """Remove a resource from the pool"""
        if resource_id in self.resources:
            del self.resources[resource_id]
    
    def get_availability(
        self,
        gpu_type: Optional[str] = None,
        location: Optional[str] = None,
        tier: Optional[GPUTier] = None
    ) -> Dict:
        """Get availability statistics"""
        filtered = list(self.resources.values())
        
        if gpu_type:
            filtered = [r for r in filtered if r.gpu_type == gpu_type]
        if location:
            filtered = [r for r in filtered if r.location == location]
        if tier:
            filtered = [r for r in filtered if r.tier == tier]
        
        available = [r for r in filtered if r.available and r.current_load < 0.9]
        
        return {
            'total': len(filtered),
            'available': len(available),
            'utilization': sum(r.current_load for r in filtered) / len(filtered) if filtered else 0.0,
            'average_price': sum(r.price_per_hour for r in available) / len(available) if available else 0.0
        }

