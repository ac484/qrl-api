"""Custom exceptions for MEXC client."""


class MexcAPIError(Exception):
    """Raised for API responses that return non-2xx status codes."""


class MexcRequestError(Exception):
    """Raised for transport-level request failures."""


# Backward-compatible alias expected by legacy imports
MEXCAPIException = MexcAPIError

__all__ = ["MexcAPIError", "MexcRequestError", "MEXCAPIException"]
