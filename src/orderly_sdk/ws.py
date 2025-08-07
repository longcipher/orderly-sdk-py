
"""
Async WebSocket API clients for Orderly.Network EVM API (v2).

This module provides public and private WebSocket managers for subscribing to real-time market and account data.
"""

import asyncio
import base64
import datetime
import json as jsonlib
from collections import defaultdict
from typing import DefaultDict, Dict, Optional

import base58
import websockets
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from websockets import WebSocketClientProtocol

from .helpers import get_loop
from .log import logger



class WsTopicManager:
    """
    Base class for Orderly async WebSocket API clients.

    Handles connection, subscription, message dispatch, and topic queues.
    
    This class manages WebSocket connections to Orderly Network and provides
    topic-based message routing for real-time data streams.

    Example:
        ```python
        ws_client = OrderlyPublicWsManager(
            account_id="your_account_id", 
            endpoint="wss://testnet-ws-evm.orderly.org/ws/stream/"
        )
        ws_client.subscribe("bbos")  # Subscribe to best bid/offer
        ws_client.start()
        
        while True:
            data = await ws_client.recv("bbos")
            print(data)
        ```

    Args:
        _id (str): Client identifier for debugging.
        account_id (str): User account ID.
        endpoint (str): WebSocket endpoint URL.
        loop: Asyncio event loop (optional).
    """

    endpoint: str
    queues: DefaultDict[str, asyncio.Queue]
    websocket: WebSocketClientProtocol

    def __init__(
        self,
        _id="WS_PUBLIC",
        account_id="",
        endpoint="",
        loop=None,
    ):
        self._id = _id
        self.account_id = account_id
        self.endpoint = endpoint + self.account_id
        self.loop = loop or get_loop()
        # topic -> topic event queue
        self.queues: DefaultDict[str, asyncio.Queue] = defaultdict(asyncio.Queue)

    async def _connect(
        self,
        timeout: Optional[int | float] = None,
        **kwargs,
    ):
        async for websocket in websockets.connect(self.endpoint, **kwargs):
            try:
                self.websocket = websocket
                await self._reconnect()
                logger.debug(f"Connected to {self.endpoint}")
                while True:
                    try:
                        message = await asyncio.wait_for(
                            websocket.recv(), timeout=timeout
                        )
                        await self._handle_heartbeat(message)
                        # asyncio.create_task(self._handle_message(message))
                        await self._handle_message(message)
                    except asyncio.TimeoutError:
                        logger.warning(f"Connection to {self.endpoint} timed out")
                        break
            except websockets.ConnectionClosed:
                logger.warning(f"Disconnected from {self.endpoint}")
            except Exception as e:
                logger.exception(e)

    def start(self, timeout: Optional[int | float] = None, **kwargs):
        """
        Start the WebSocket connection in the event loop (non-blocking).
        """
        self.loop.call_soon_threadsafe(
            asyncio.create_task, self._connect(timeout, **kwargs)
        )

    def subscribe(self, topic):
        """
        Subscribe to a topic (creates a queue for topic events).

        Args:
            topic (str): Topic name.
        """
        self.queues[topic] = asyncio.Queue()

    async def do_subscribe(self, topic):
        """
        Send a subscribe request to the server for a topic.

        Args:
            topic (str): Topic name.
        """
        await self.send_json({"id": self._id, "event": "subscribe", "topic": topic})

    async def request(self, symbol: str):
        """
        Request orderbook for a symbol.

        Args:
            symbol (str): Market symbol.
        """
        params = {"params": {"type": "orderbook", "symbol": symbol}}
        await self.send_json({"id": self._id, "event": "request", **params})

    async def unsubscribe(self, topic):
        """
        Unsubscribe from a topic and remove its queue.

        Args:
            topic (str): Topic name.
        """
        await self.websocket.send(
            jsonlib.dumps({"id": self._id, "event": "unsubscribe", "topic": topic})
        )
        self.queues.pop(topic)

    async def send_json(self, message):
        """
        Send a JSON message to the WebSocket server.

        Args:
            message (dict): Message to send.
        """
        if "event" in message and message["event"] != "pong":
            logger.debug(f"sending message to {self.endpoint}: {message}")
        await self.websocket.send(jsonlib.dumps(message))

    async def _handle_heartbeat(self, message):
        message = jsonlib.loads(message)
        if "event" in message:
            if message["event"] == "ping":
                await self.send_json({"event": "pong"})

    async def _handle_request_orderbook(self, message: Dict):
        topic = message["data"]["symbol"] + "@orderbook"
        data = message["data"]
        data["ts"] = message["ts"]
        await self.queues[topic].put(data)

    async def _handle_general_message(self, message: Dict):
        data = message["data"]
        # data["ts"] = message["ts"]
        # logger.info(f"received message from {self.endpoint}: {message}")
        await self.queues[message["topic"]].put(data)

    async def recv(self, topic, timeout=10):
        """
        Receive a message from a topic queue.

        Args:
            topic (str): Topic name.
            timeout (int): Timeout in seconds.
        Returns:
            dict: Message data.
        """
        res = None
        while not res:
            try:
                res = await asyncio.wait_for(self.queues[topic].get(), timeout=timeout)
            except asyncio.TimeoutError:
                logger.info(f"no message in {timeout} seconds")
        return res

    async def _handle_message(self, message):
        message = jsonlib.loads(message)
        # logger.info(f"received message from {self.endpoint}: {message}")
        if "event" in message:
            if message["event"] not in ("ping", "pong"):
                if message["success"]:
                    if "data" in message and message["event"] == "request":
                        await self._handle_request_orderbook(message)
                    return
                else:
                    raise Exception(message)
        if "data" in message:
            await self._handle_general_message(message)

    # reconnect, resubscribe
    async def _reconnect(self):
        for topic in self.queues.keys():
            await self.do_subscribe(topic)



class OrderlyPublicWsManager(WsTopicManager):
    """
    Public async WebSocket API client for Orderly.Network.

    Used for subscribing to public market data topics like:
    - `bbos` - Best bid/offer updates
    - `trade` - Real-time trade data  
    - `orderbook` - Order book snapshots and updates
    - `24h_ticker` - 24-hour ticker statistics
    - `kline_1m`, `kline_5m`, etc. - Kline/candlestick data

    Example:
        ```python
        ws = OrderlyPublicWsManager(
            account_id="your_account_id",
            endpoint="wss://testnet-ws-evm.orderly.org/ws/stream/"
        )
        
        # Subscribe to multiple topics
        ws.subscribe("bbos")
        ws.subscribe("PERP_ETH_USDC@trade")  
        ws.start()
        
        while True:
            bbos_data = await ws.recv("bbos", timeout=30)
            print(f"Best prices: {bbos_data}")
        ```
    
    Args:
        _id (str): Client identifier.
        account_id (str): User account ID.
        endpoint (str): WebSocket endpoint URL.
        loop: Asyncio event loop.
    """

    def __init__(
        self,
        _id="WS_PUBLIC",
        account_id="",
        endpoint="",
        loop=None,
    ):
        super().__init__(
            _id=_id,
            account_id=account_id,
            endpoint=endpoint,
            loop=loop,
        )

    async def subscribe_bbos(self):
        """Subscribe to best bid/offer stream."""
        self.subscribe("bbos")
        await self.do_subscribe("bbos")

    async def subscribe_trade(self, symbol: str):
        """
        Subscribe to trade stream for a symbol.
        
        Args:
            symbol (str): Trading symbol (e.g., "PERP_ETH_USDC").
        """
        topic = f"{symbol}@trade"
        self.subscribe(topic)
        await self.do_subscribe(topic)

    async def subscribe_orderbook(self, symbol: str):
        """
        Subscribe to orderbook updates for a symbol.
        
        Args:
            symbol (str): Trading symbol (e.g., "PERP_ETH_USDC").
        """
        topic = f"{symbol}@orderbook"
        self.subscribe(topic)
        await self.do_subscribe(topic)

    async def subscribe_ticker(self, symbol: Optional[str] = None):
        """
        Subscribe to 24h ticker data.
        
        Args:
            symbol (str, optional): Trading symbol. If None, subscribes to all tickers.
        """
        topic = f"{symbol}@24h_ticker" if symbol else "24h_tickers"
        self.subscribe(topic)
        await self.do_subscribe(topic)

    async def subscribe_kline(self, symbol: str, interval: str):
        """
        Subscribe to kline/candlestick data.
        
        Args:
            symbol (str): Trading symbol (e.g., "PERP_ETH_USDC").
            interval (str): Time interval (e.g., "1m", "5m", "1h", "1d").
        """
        topic = f"{symbol}@kline_{interval}"
        self.subscribe(topic)
        await self.do_subscribe(topic)



class OrderlyPrivateWsManager(WsTopicManager):
    """
    Private async WebSocket API client for Orderly.Network.

    Used for subscribing to private account data topics that require authentication:
    - `position` - Position updates
    - `balance` - Balance updates  
    - `order` - Order status updates
    - `trade` - Private trade fills
    - `liquidation` - Liquidation events
    - `pnl` - PnL updates

    Example:
        ```python
        ws = OrderlyPrivateWsManager(
            account_id="your_account_id",
            orderly_key="your_orderly_key", 
            orderly_secret="your_orderly_secret",
            endpoint="wss://testnet-ws-private-evm.orderly.org/v2/ws/private/stream/"
        )
        
        # Subscribe to private data streams
        ws.subscribe("position")
        ws.subscribe("balance")
        ws.start()
        
        while True:
            position_data = await ws.recv("position")
            print(f"Position update: {position_data}")
        ```

    Args:
        _id (str): Client identifier.
        account_id (str): User account ID.  
        orderly_key (str): API key for authentication.
        orderly_secret (str): API secret for signing.
        endpoint (str): Private WebSocket endpoint URL.
        loop: Asyncio event loop.
    """

    def __init__(
        self,
        _id="WS_PRIVATE",
        account_id="",
        orderly_key: Optional[str] = None,
        orderly_secret: Optional[str] = None,
        endpoint="",
        loop=None,
    ):
        super().__init__(
            _id=_id,
            account_id=account_id,
            endpoint=endpoint,
            loop=loop,
        )
        self.orderly_key = orderly_key
        self.orderly_secret = orderly_secret
        if orderly_secret is not None:
            self.orderly_private_key = Ed25519PrivateKey.from_private_bytes(
                base58.b58decode(orderly_secret)[0:32]
            )

    def _signature(self, data):
        """Generate Ed25519 signature for authentication."""
        data_bytes = bytes(str(data), "utf-8")
        request_signature = base64.b64encode(
            self.orderly_private_key.sign(data_bytes)
        ).decode("utf-8")
        return request_signature

    async def _login(self) -> None:
        """Authenticate with the private WebSocket endpoint."""
        ts = round(datetime.datetime.now().timestamp() * 1000)
        await self.send_json(
            {
                "id": self._id,
                "event": "auth",
                "params": {
                    "orderly_key": f"ed25519:{self.orderly_key}",
                    "sign": self._signature(ts),
                    "timestamp": str(ts),
                },
            }
        )

    async def subscribe_position(self):
        """Subscribe to position updates."""
        self.subscribe("position")
        await self._login()
        await self.do_subscribe("position")

    async def subscribe_balance(self):
        """Subscribe to balance updates."""
        self.subscribe("balance")
        await self._login()
        await self.do_subscribe("balance")

    async def subscribe_order(self):
        """Subscribe to order status updates."""
        self.subscribe("order")
        await self._login()
        await self.do_subscribe("order")

    async def subscribe_trade(self):
        """Subscribe to private trade fills."""
        self.subscribe("trade")
        await self._login()  
        await self.do_subscribe("trade")

    async def subscribe_liquidation(self):
        """Subscribe to liquidation events."""
        self.subscribe("liquidation")
        await self._login()
        await self.do_subscribe("liquidation")

    async def subscribe_pnl(self):
        """Subscribe to PnL updates."""
        self.subscribe("pnl")
        await self._login()
        await self.do_subscribe("pnl")

    # reconnect, resubscribe
    async def _reconnect(self):
        """Reconnect and re-authenticate, then re-subscribe to all topics."""
        for topic in self.queues.keys():
            await self._login()
            await self.do_subscribe(topic)
