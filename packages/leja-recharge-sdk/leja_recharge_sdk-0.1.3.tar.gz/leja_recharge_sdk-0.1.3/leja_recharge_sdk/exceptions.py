"""
Custom exceptions for the Leja Recharge SDK.
"""

class LejaRechargeError(Exception):
    """Base exception for all Leja Recharge SDK errors."""
    pass


class AuthenticationError(LejaRechargeError):
    """Raised when there are authentication issues."""
    pass


class ValidationError(LejaRechargeError):
    """Raised when request validation fails."""
    pass


class APIError(LejaRechargeError):
    """Raised when the API returns an error."""
    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(message)


class NetworkError(LejaRechargeError):
    """Raised when there are network-related issues."""
    pass 