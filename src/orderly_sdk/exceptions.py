
"""
Exception classes for Orderly SDK.

Defines custom exceptions for API and request errors.
"""



class OrderlyAPIException(Exception):
    """
    Exception raised for API errors returned by Orderly endpoints.

    Args:
        resp_json (dict): Response JSON from API.
        status_code (int): HTTP status code.
    """

    def __init__(self, resp_json, status_code):
        self.status_code = status_code
        try:
            self.code = resp_json.get("code")
            self.message = resp_json.get("message")
        except Exception:
            self.code = None
            self.message = resp_json

    def __str__(self):
        return f"APIError(status_code={self.status_code}, code={self.code}, message={self.message}"



class OrderlyRequestException(Exception):
    """
    Exception raised for invalid or unexpected API responses.

    Args:
        message (str): Error message.
    """

    def __init__(self, message) -> None:
        self.message = message

    def __str__(self) -> str:
        return f"OrderlyRequestException: {self.message}"
