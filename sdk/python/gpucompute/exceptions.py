"""
Exception classes for GPU Compute SDK
"""


class GPUComputeError(Exception):
    """Base exception for all SDK errors"""
    pass


class AuthenticationError(GPUComputeError):
    """Authentication failed"""
    pass


class InsufficientBalanceError(GPUComputeError):
    """Insufficient token balance"""
    pass


class JobNotFoundError(GPUComputeError):
    """Job not found"""
    pass


class APIError(GPUComputeError):
    """API error response"""
    
    def __init__(self, message: str, status_code: int = None, error_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_data = error_data or {}

