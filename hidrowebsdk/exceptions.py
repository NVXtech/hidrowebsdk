"""
Exception classes for HidroWebSDK
"""


class HidroWebError(Exception):
    """Base exception class for HidroWebSDK"""
    pass


class HidroWebAPIError(HidroWebError):
    """Exception raised when the API returns an error response"""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class HidroWebConnectionError(HidroWebError):
    """Exception raised when there are connection issues with the API"""
    pass


class HidroWebValidationError(HidroWebError):
    """Exception raised when input validation fails"""
    pass