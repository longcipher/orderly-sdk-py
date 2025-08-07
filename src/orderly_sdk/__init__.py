
"""
Orderly SDK for Python

Async REST and WebSocket client for Orderly.Network EVM API (v2).

This package provides:
- AsyncClient: REST API client for trading and account management
- OrderlyPublicWsManager: Public WebSocket client for market data
- OrderlyPrivateWsManager: Private WebSocket client for account data
- Custom exceptions for API errors
- Logging utilities

Basic usage:
    ```python
    from orderly_sdk.rest import AsyncClient
    from orderly_sdk.ws import OrderlyPublicWsManager
    
    # REST API
    client = AsyncClient(account_id=..., orderly_key=..., orderly_secret=..., endpoint=...)
    
    # WebSocket API
    ws_client = OrderlyPublicWsManager(account_id=..., endpoint=...)
    ```

For detailed documentation, see: https://longcipher.github.io/orderly-sdk-py/
"""

# Import main classes for easier access
from .rest import AsyncClient
from .ws import OrderlyPublicWsManager, OrderlyPrivateWsManager
from .exceptions import OrderlyAPIException, OrderlyRequestException

__version__ = "0.3.1"
__all__ = [
    "AsyncClient",
    "OrderlyPublicWsManager", 
    "OrderlyPrivateWsManager",
    "OrderlyAPIException",
    "OrderlyRequestException",
]
