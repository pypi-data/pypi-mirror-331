class KBankSDKError(Exception):
    """Base exception class for KBank SDK errors"""

    pass


class ValidationError(KBankSDKError):
    """Raised when input validation fails"""

    pass


class APIError(KBankSDKError):
    """Raised when API returns an error response"""

    pass
