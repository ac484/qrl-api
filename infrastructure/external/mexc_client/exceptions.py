"""Custom exceptions for MEXC client."""


class MexcAPIError(Exception):
    """Raised for API responses that return non-2xx status codes."""


class MexcRequestError(Exception):
    """Raised for transport-level request failures."""


__all__ = ["MexcAPIError", "MexcRequestError"]
