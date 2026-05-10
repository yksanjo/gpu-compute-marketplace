"""
Main client for GPU Compute Marketplace SDK
"""

import requests
from typing import Dict, Optional, List
from .exceptions import (
    GPUComputeError,
    AuthenticationError,
    InsufficientBalanceError,
    JobNotFoundError,
    APIError
)


class Client:
    """Main client for interacting with GPU Compute Marketplace API"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.gpucompute.market/v1"
    ):
        """
        Initialize the client.
        
        Args:
            api_key: API key for authentication
            base_url: Base URL for API (default: production)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
        
        # Initialize sub-clients
        self.tokens = TokenClient(self)
        self.jobs = JobClient(self)
        self.matching = MatchingClient(self)
        self.resources = ResourceClient(self)
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """Make API request"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif e.response.status_code == 402:
                raise InsufficientBalanceError("Insufficient token balance")
            elif e.response.status_code == 404:
                raise JobNotFoundError("Job not found")
            else:
                error_data = e.response.json() if e.response.content else {}
                raise APIError(
                    f"API error: {e.response.status_code}",
                    status_code=e.response.status_code,
                    error_data=error_data
                )
        except requests.exceptions.RequestException as e:
            raise GPUComputeError(f"Request failed: {str(e)}")


class TokenClient:
    """Client for token operations"""
    
    def __init__(self, parent: Client):
        self._client = parent
    
    def get_balance(self) -> Dict:
        """Get current token balance"""
        return self._client._request("GET", "/tokens/balance")
    
    def purchase(
        self,
        amount: float,
        payment_method: str = "stripe",
        payment_token: Optional[str] = None
    ) -> Dict:
        """Purchase compute credits"""
        data = {
            "amount": amount,
            "paymentMethod": payment_method
        }
        if payment_token:
            data["paymentToken"] = payment_token
        
        return self._client._request("POST", "/tokens/purchase", data=data)
    
    def reserve(
        self,
        job_id: str,
        amount: float,
        estimated_duration: float,
        gpu_type: str
    ) -> Dict:
        """Reserve tokens for a job"""
        data = {
            "jobId": job_id,
            "amount": amount,
            "estimatedDuration": estimated_duration,
            "gpuType": gpu_type
        }
        return self._client._request("POST", "/tokens/reserve", data=data)


class JobClient:
    """Client for job operations"""
    
    def __init__(self, parent: Client):
        self._client = parent
    
    def submit(
        self,
        gpu_requirements: Dict,
        container_image: str,
        priority: str = "normal",
        estimated_duration: Optional[float] = None,
        deadline: Optional[str] = None,
        environment: Optional[Dict] = None,
        command: Optional[List[str]] = None
    ) -> Dict:
        """Submit a compute job"""
        data = {
            "gpuRequirements": gpu_requirements,
            "containerImage": container_image,
            "priority": priority
        }
        
        if estimated_duration:
            data["estimatedDuration"] = estimated_duration
        if deadline:
            data["deadline"] = deadline
        if environment:
            data["environment"] = environment
        if command:
            data["command"] = command
        
        return self._client._request("POST", "/jobs", data=data)
    
    def get_status(self, job_id: str) -> Dict:
        """Get job status"""
        return self._client._request("GET", f"/jobs/{job_id}")
    
    def cancel(self, job_id: str) -> Dict:
        """Cancel a job"""
        return self._client._request("DELETE", f"/jobs/{job_id}")
    
    def wait_for_completion(
        self,
        job_id: str,
        timeout: Optional[float] = None,
        poll_interval: float = 5.0
    ) -> Dict:
        """Wait for job to complete"""
        import time
        
        start_time = time.time()
        while True:
            status = self.get_status(job_id)
            
            if status["status"] in ["completed", "failed", "cancelled"]:
                return status
            
            if timeout and (time.time() - start_time) > timeout:
                raise GPUComputeError("Timeout waiting for job completion")
            
            time.sleep(poll_interval)


class MatchingClient:
    """Client for resource matching"""
    
    def __init__(self, parent: Client):
        self._client = parent
    
    def find_matches(
        self,
        gpu_requirements: Dict,
        preferences: Optional[Dict] = None,
        urgency: str = "normal"
    ) -> List[Dict]:
        """Find matching GPU resources"""
        data = {
            "gpuRequirements": gpu_requirements,
            "urgency": urgency
        }
        if preferences:
            data["preferences"] = preferences
        
        response = self._client._request("POST", "/matching/find", data=data)
        return response.get("matches", [])
    
    def get_availability(
        self,
        gpu_type: Optional[str] = None,
        location: Optional[str] = None,
        tier: Optional[str] = None
    ) -> Dict:
        """Get resource availability"""
        params = {}
        if gpu_type:
            params["gpuType"] = gpu_type
        if location:
            params["location"] = location
        if tier:
            params["tier"] = tier
        
        return self._client._request("GET", "/matching/availability", params=params)


class ResourceClient:
    """Client for resource operations"""
    
    def __init__(self, parent: Client):
        self._client = parent
    
    def list(
        self,
        gpu_type: Optional[str] = None,
        location: Optional[str] = None,
        tier: Optional[str] = None
    ) -> List[Dict]:
        """List available resources"""
        params = {}
        if gpu_type:
            params["gpuType"] = gpu_type
        if location:
            params["location"] = location
        if tier:
            params["tier"] = tier
        
        response = self._client._request("GET", "/resources", params=params)
        return response.get("resources", [])

