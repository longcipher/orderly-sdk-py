
"""
Helper functions for Orderly SDK.

Provides utility functions for event loop management and async support.
"""

import asyncio


def get_loop():
    """
    Get or create an asyncio event loop for the current thread.

    Returns:
        asyncio.AbstractEventLoop: The event loop.
    """
    try:
        loop = asyncio.get_event_loop()
        return loop
    except RuntimeError as e:
        if str(e).startswith("There is no current event loop in thread"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
        else:
            raise
