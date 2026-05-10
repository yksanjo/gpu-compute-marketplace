"""
Scheduler Service
Manages job queues, priority scheduling, and resource allocation.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import logging
import uuid

logger = logging.getLogger(__name__)


class JobPriority(Enum):
    """Job priority levels"""
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class JobStatus(Enum):
    """Job status states"""
    QUEUED = "queued"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PREEMPTED = "preempted"
    CANCELLED = "cancelled"


@dataclass
class GPURequirement:
    """GPU requirements"""
    type: str
    count: int
    memory: int


@dataclass
class ComputeJob:
    """Compute job definition"""
    id: str
    user_id: str
    status: JobStatus
    priority: JobPriority
    gpu_requirements: GPURequirement
    container_image: str
    estimated_duration: float  # hours
    deadline: Optional[datetime] = None
    tokens_reserved: float = 0.0
    tokens_consumed: float = 0.0
    assigned_resource_id: Optional[str] = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}


class JobQueue:
    """Priority-based job queue"""
    
    def __init__(self):
        self.queues = {
            JobPriority.URGENT: [],
            JobPriority.HIGH: [],
            JobPriority.NORMAL: [],
            JobPriority.LOW: []
        }
    
    def enqueue(self, job: ComputeJob):
        """Add job to appropriate priority queue"""
        self.queues[job.priority].append(job)
        logger.info(f"Job {job.id} queued with priority {job.priority.value}")
    
    def dequeue(self, priority: Optional[JobPriority] = None) -> Optional[ComputeJob]:
        """Get next job from queue"""
        priorities = [priority] if priority else [
            JobPriority.URGENT,
            JobPriority.HIGH,
            JobPriority.NORMAL,
            JobPriority.LOW
        ]
        
        for p in priorities:
            if self.queues[p]:
                return self.queues[p].pop(0)
        
        return None
    
    def peek(self, priority: Optional[JobPriority] = None) -> Optional[ComputeJob]:
        """Peek at next job without removing it"""
        priorities = [priority] if priority else [
            JobPriority.URGENT,
            JobPriority.HIGH,
            JobPriority.NORMAL,
            JobPriority.LOW
        ]
        
        for p in priorities:
            if self.queues[p]:
                return self.queues[p][0]
        
        return None
    
    def remove(self, job_id: str) -> bool:
        """Remove job from queue"""
        for queue in self.queues.values():
            for i, job in enumerate(queue):
                if job.id == job_id:
                    queue.pop(i)
                    return True
        return False
    
    def size(self) -> int:
        """Get total queue size"""
        return sum(len(queue) for queue in self.queues.values())
    
    def size_by_priority(self, priority: JobPriority) -> int:
        """Get queue size for specific priority"""
        return len(self.queues[priority])


class Scheduler:
    """Core scheduler implementation"""
    
    def __init__(self):
        self.job_queue = JobQueue()
        self.active_jobs: Dict[str, ComputeJob] = {}
        self.completed_jobs: Dict[str, ComputeJob] = {}
        self.preemption_grace_period = timedelta(minutes=5)
    
    def submit_job(
        self,
        user_id: str,
        gpu_requirements: GPURequirement,
        container_image: str,
        priority: JobPriority = JobPriority.NORMAL,
        estimated_duration: float = 1.0,
        deadline: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ) -> ComputeJob:
        """Submit a new compute job"""
        job = ComputeJob(
            id=str(uuid.uuid4()),
            user_id=user_id,
            status=JobStatus.QUEUED,
            priority=priority,
            gpu_requirements=gpu_requirements,
            container_image=container_image,
            estimated_duration=estimated_duration,
            deadline=deadline,
            metadata=metadata or {}
        )
        
        self.job_queue.enqueue(job)
        logger.info(f"Job {job.id} submitted by user {user_id}")
        
        return job
    
    def schedule_job(self, job: ComputeJob, resource_id: str) -> bool:
        """Schedule a job to a resource"""
        if job.status != JobStatus.QUEUED:
            logger.warning(f"Job {job.id} is not in queued state")
            return False
        
        job.status = JobStatus.SCHEDULED
        job.assigned_resource_id = resource_id
        self.active_jobs[job.id] = job
        
        logger.info(f"Job {job.id} scheduled to resource {resource_id}")
        return True
    
    def start_job(self, job_id: str) -> bool:
        """Mark job as running"""
        if job_id not in self.active_jobs:
            return False
        
        job = self.active_jobs[job_id]
        if job.status != JobStatus.SCHEDULED:
            return False
        
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        
        logger.info(f"Job {job_id} started")
        return True
    
    def complete_job(self, job_id: str, success: bool = True) -> bool:
        """Mark job as completed or failed"""
        if job_id not in self.active_jobs:
            return False
        
        job = self.active_jobs[job_id]
        job.status = JobStatus.COMPLETED if success else JobStatus.FAILED
        job.completed_at = datetime.utcnow()
        
        # Move to completed jobs
        self.completed_jobs[job_id] = job
        del self.active_jobs[job_id]
        
        logger.info(f"Job {job_id} {'completed' if success else 'failed'}")
        return True
    
    def preempt_job(self, job_id: str) -> bool:
        """Preempt a running job (for spot instances)"""
        if job_id not in self.active_jobs:
            return False
        
        job = self.active_jobs[job_id]
        if job.status != JobStatus.RUNNING:
            return False
        
        job.status = JobStatus.PREEMPTED
        job.completed_at = datetime.utcnow()
        
        # Move back to queue with higher priority
        job.priority = JobPriority.HIGH  # Boost priority after preemption
        self.job_queue.enqueue(job)
        
        # Remove from active jobs
        del self.active_jobs[job_id]
        
        logger.warning(f"Job {job_id} preempted")
        return True
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a queued or scheduled job"""
        # Check if in queue
        if self.job_queue.remove(job_id):
            logger.info(f"Job {job_id} cancelled from queue")
            return True
        
        # Check if active
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            if job.status in [JobStatus.QUEUED, JobStatus.SCHEDULED]:
                job.status = JobStatus.CANCELLED
                del self.active_jobs[job_id]
                logger.info(f"Job {job_id} cancelled")
                return True
        
        return False
    
    def get_next_job(self, priority: Optional[JobPriority] = None) -> Optional[ComputeJob]:
        """Get next job to schedule"""
        return self.job_queue.dequeue(priority)
    
    def get_job(self, job_id: str) -> Optional[ComputeJob]:
        """Get job by ID"""
        if job_id in self.active_jobs:
            return self.active_jobs[job_id]
        if job_id in self.completed_jobs:
            return self.completed_jobs[job_id]
        return None
    
    def get_queue_stats(self) -> Dict:
        """Get queue statistics"""
        return {
            'total_queued': self.job_queue.size(),
            'by_priority': {
                priority.value: self.job_queue.size_by_priority(priority)
                for priority in JobPriority
            },
            'active_jobs': len(self.active_jobs),
            'completed_jobs': len(self.completed_jobs)
        }
    
    def check_deadlines(self) -> List[str]:
        """Check for jobs approaching deadlines"""
        now = datetime.utcnow()
        approaching_deadline = []
        
        for job in self.active_jobs.values():
            if job.deadline and job.deadline < now + timedelta(hours=1):
                if job.status == JobStatus.QUEUED:
                    # Boost priority
                    job.priority = JobPriority.URGENT
                    approaching_deadline.append(job.id)
        
        return approaching_deadline

