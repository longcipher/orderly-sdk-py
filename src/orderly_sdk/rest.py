
"""
Async REST API client for Orderly.Network EVM API (v2).

This module provides the `AsyncClient` class for interacting with Orderly's REST endpoints.
Supports both public and private endpoints, with Ed25519 signature authentication for private endpoints.
"""

import base64
import datetime
import json as jsonlib
from collections import defaultdict
from typing import Dict, Optional
from urllib.parse import urlencode, urlparse

import aiohttp
import base58
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from .exceptions import OrderlyRequestException
from .helpers import get_loop
from .log import logger



class AsyncClient:
    """
    Asynchronous REST API client for Orderly.Network EVM API.

    Example usage:
        client = AsyncClient(account_id=..., orderly_key=..., orderly_secret=..., endpoint=...)
        await client.get_user_statistics()
        await client.close_connection()

    Args:
        _id (str): Client identifier (default: "rest_client").
        account_id (str, optional): User account ID.
        orderly_key (str, optional): API key for authentication.
        orderly_secret (str, optional): API secret for signing requests.
        endpoint (str, optional): REST API endpoint URL.
        loop: Asyncio event loop.
    """

    _id: str
    account_id: Optional[str]
    orderly_key: Optional[str]
    orderly_secret: Optional[str]
    endpoint: Optional[str]
    api_version: str = "v1"
    timeout = 30

    def __init__(
        self,
        _id="rest_client",
        account_id: Optional[str] = None,
        orderly_key: Optional[str] = None,
        orderly_secret: Optional[str] = None,
        endpoint: Optional[str] = None,
        loop=None,
    ):
        self._id = _id
        self.account_id = account_id
        self.orderly_key = orderly_key
        self.orderly_secret = orderly_secret
        if orderly_secret is not None:
            self.orderly_private_key = Ed25519PrivateKey.from_private_bytes(
                base58.b58decode(orderly_secret)[0:32]
            )
        self.endpoint = endpoint
        self.loop = loop or get_loop()
        self.session = self._init_session()
        self.headers: Dict[str, str] = defaultdict(str)
        self.response = None

    def _get_headers(self) -> Dict:
        """Get default headers for HTTP requests."""
        headers = {
            "Accept": "application/json",
        }
        if self.orderly_key:
            headers["orderly-key"] = self.orderly_key
        return headers

    def _init_session(self) -> aiohttp.ClientSession:
        """Initialize aiohttp client session with default headers."""
        return aiohttp.ClientSession(loop=self.loop, headers=self._get_headers())

    async def close_connection(self):
        """
        Close the underlying aiohttp session.
        Call this when you are done with the client to free resources.
        """
        if self.session:
            assert self.session
            await self.session.close()

    async def _request(
        self,
        method,
        uri: str,
        signed: bool,
        params: Optional[Dict],
        json: Optional[Dict],
    ):
        if signed:
            ts = round(datetime.datetime.now().timestamp() * 1000)
            json_str = ""
            if json is not None:
                logger.debug(f"request json body: {json}")
                json_str = jsonlib.dumps(json)
            path = urlparse(uri).path
            if params:
                query = urlencode(params)
                path = f"{path}?{query}"
            signature_str = f"{ts}{method.upper()}{path}{json_str}"
            logger.debug(f"request signature: {signature_str}")
            data_bytes = bytes(signature_str, "utf-8")

            req_signature = base64.b64encode(
                self.orderly_private_key.sign(data_bytes)
            ).decode("utf-8")

            self.headers["orderly-signature"] = req_signature
            if self.account_id is not None:
                self.headers["orderly-account-id"] = self.account_id
            else:
                pass
            self.headers["orderly-key"] = f"ed25519:{self.orderly_key}"
            self.headers["orderly-timestamp"] = str(ts)
            self.headers["Content-Type"] = (
                "application/json" if json else "application/x-www-form-urlencoded"
            )
            self.headers["Cache-Control"] = "no-cache"
            self.session.headers.update(self.headers)

        logger.debug("request uri: {}", uri)
        async with getattr(self.session, method)(
            uri, params=params, json=json
        ) as response:
            self.response = response
            return await self._handle_response(response)

    async def _handle_response(self, response: aiohttp.ClientResponse):
        if not str(response.status).startswith("2"):
            logger.error("response: {}", response)
        try:
            return await response.json()
        except ValueError as exc:
            txt = await response.text()
            raise OrderlyRequestException(f"Invalid Response: {txt}") from exc

    def _create_rest_uri(self, ep: str, v: str = ""):
        if not v:
            v = self.api_version
        return f"{self.endpoint}/{v}/{ep}"

    async def _request_api(
        self, method, ep: str, signed: bool, v: str = "", params=None, json=None
    ):
        uri = self._create_rest_uri(ep, v)
        return await self._request(method, uri, signed, params=params, json=json)

    async def _get(self, ep, signed=False, v: str = "", params=None, json=None):
        return await self._request_api("get", ep, signed, v, params, json)

    async def _post(self, ep, signed=False, v: str = "", params=None, json=None):
        return await self._request_api("post", ep, signed, v, params, json)

    async def _put(self, ep, signed=False, v: str = "", params=None, json=None):
        return await self._request_api("put", ep, signed, v, params, json)

    async def _delete(self, ep, signed=False, v: str = "", params=None, json=None):
        return await self._request_api("delete", ep, signed, v, params, json)

    async def get_maintenance_info(self) -> Dict:
        """
        Get system maintenance status (public endpoint).

        Returns:
            dict: Maintenance status and system info.
        API doc: https://orderly.network/docs/build-on-evm/evm-api/restful-api/public/get-system-maintenance-status
        """
        return await self._get("public/system_info")

    async def get_user_statistics(self) -> Dict:
        """
        Get user statistics (private endpoint).

        Returns:
            dict: User statistics.
        API doc: https://orderly.network/docs/build-on-evm/evm-api/restful-api/private/get-user-statistics
        """
        return await self._get("client/statistics", True)

    async def create_order(self, json: Dict) -> Dict:
        """
        Create a new order (private endpoint).

        Args:
            json (dict): Order parameters.
        Returns:
            dict: Order creation result.
        API doc: https://orderly.network/docs/build-on-evm/evm-api/restful-api/private/create-order
        """
        return await self._post("order", True, json=json)

    async def claim_liquidated_positions(self, json: Dict) -> Dict:
        """
        Claim liquidated positions (private endpoint).

        Args:
            json (dict): Claim parameters.
        Returns:
            dict: Claim result.
        API doc: https://orderly.network/docs/build-on-evm/evm-api/restful-api/private/claim-liquidated-positions
        """
        return await self._post("liquidation", True, json=json)

    async def claim_insurance_fund(self, json: Dict) -> Dict:
        """
        Claim insurance fund (private endpoint).

        Args:
            json (dict): Claim parameters.
        Returns:
            dict: Claim result.
        API doc: https://orderly.network/docs/build-on-evm/evm-api/restful-api/private/claim-insurance-fund
        """
        return await self._post("claim_insurance_fund", True, json=json)

    async def get_all_positions(self) -> Dict:
        """
        Get all positions info (private endpoint).

        Returns:
            dict: All positions information.
        API doc: https://orderly.network/docs/build-on-evm/evm-api/restful-api/private/get-all-positions-info
        """
        return await self._get("positions", True)

    async def get_liquidation(self, params) -> Dict:
        """
        Get positions under liquidation (public endpoint).

        Args:
            params (dict): Query parameters.
        Returns:
            dict: Liquidation info.
        API doc: https://orderly.network/docs/build-on-evm/evm-api/restful-api/public/get-positions-under-liquidation
        """
        return await self._get("public/liquidation", params=params)

    async def get_liquidated_positions(self, params) -> Dict:
        """
        Get liquidated positions info (public endpoint).

        Args:
            params (dict): Query parameters.
        Returns:
            dict: Liquidated positions info.
        API doc: https://orderly.network/docs/build-on-evm/evm-api/restful-api/public/get-liquidated-positions-info
        """
        return await self._get("public/liquidated_positions", params=params)

    async def get_insurance_fund(self) -> Dict:
        """
        Get insurance fund info (public endpoint).

        Returns:
            dict: Insurance fund info.
        API doc: https://orderly.network/docs/build-on-evm/evm-api/restful-api/public/get-insurance-fund-info
        """
        return await self._get("public/insurancefund")

    async def get_available_symbols(self) -> Dict:
        """
        Get available trading symbols (public endpoint).

        Returns:
            dict: Available symbols.
        API doc: https://orderly.network/docs/build-on-evm/evm-api/restful-api/public/get-available-symbols
        """
        return await self._get("public/info")

    async def get_futures_for_one_market(self, symbol) -> Dict:
        """
        Get futures info for a single market (public endpoint).

        Args:
            symbol (str): Market symbol.
        Returns:
            dict: Futures info for the market.
        API doc: https://orderly.network/docs/build-on-evm/evm-api/restful-api/public/get-futures-info-for-one-market
        """
        return await self._get("public/futures/" + symbol)

    async def get_current_holding(self) -> Dict:
        """
        Get current holding (private endpoint).

        Returns:
            dict: Current holding info.
        API doc: https://orderly.network/docs/build-on-evm/evm-api/restful-api/private/get-current-holding
        """
        return await self._get("client/holding", True)

    async def get_account_info(self) -> Dict:
        """
        Get account information (private endpoint).

        Returns:
            dict: Account info.
        API doc: https://orderly.network/docs/build-on-evm/evm-api/restful-api/private/get-account-information
        """
        return await self._get("client/info", True)

    async def batch_cancel_orders(self, order_ids: list) -> Dict:
        """
        Batch cancel orders (private endpoint).

        Args:
            order_ids (list): List of order IDs to cancel.
        Returns:
            dict: Batch cancel result.
        API doc: https://orderly.network/docs/build-on-evm/evm-api/restful-api/private/batch-cancel-orders
        """
        formatted_order_ids = ",".join(order_ids)
        params = {"order_ids": formatted_order_ids}

        return await self._delete("batch-order", True, params=params)

    async def get_order(self, order_id: str) -> Dict:
        """
        Get order details by order ID (private endpoint).

        Args:
            order_id (str): Order ID.
        Returns:
            dict: Order details.
        """
        return await self._get(f"order/{order_id}", True)

    async def cancel_order(self, order_id: str) -> Dict:
        """
        Cancel a single order (private endpoint).

        Args:
            order_id (str): Order ID to cancel.
        Returns:
            dict: Cancel result.
        """
        return await self._delete(f"order/{order_id}", True)

    async def get_orders(self, params: Optional[Dict] = None) -> Dict:
        """
        Get orders list (private endpoint).

        Args:
            params (dict, optional): Query parameters like status, symbol, etc.
        Returns:
            dict: Orders list.
        """
        return await self._get("orders", True, params=params)

    async def get_trades(self, params: Optional[Dict] = None) -> Dict:
        """
        Get trades history (private endpoint).

        Args:
            params (dict, optional): Query parameters like symbol, start_time, etc.
        Returns:
            dict: Trades history.
        """
        return await self._get("trades", True, params=params)

    async def get_funding_fee_history(self, params: Optional[Dict] = None) -> Dict:
        """
        Get funding fee history (private endpoint).

        Args:
            params (dict, optional): Query parameters.
        Returns:
            dict: Funding fee history.
        """
        return await self._get("funding_fee/history", True, params=params)

    async def get_funding_rates(self, symbol: Optional[str] = None) -> Dict:
        """
        Get funding rates (public endpoint).

        Args:
            symbol (str, optional): Market symbol. If None, gets all symbols.
        Returns:
            dict: Funding rates.
        """
        if symbol:
            return await self._get(f"public/funding_rate/{symbol}")
        return await self._get("public/funding_rates")

    async def get_orderbook(self, symbol: str, max_level: Optional[int] = None) -> Dict:
        """
        Get orderbook for a symbol (public endpoint).

        Args:
            symbol (str): Market symbol.
            max_level (int, optional): Maximum depth level.
        Returns:
            dict: Orderbook data.
        """
        params = {}
        if max_level is not None:
            params["max_level"] = max_level
        return await self._get(f"orderbook/{symbol}", params=params)

    async def get_kline(self, symbol: str, kline_type: str, params: Optional[Dict] = None) -> Dict:
        """
        Get kline/candlestick data (public endpoint).

        Args:
            symbol (str): Market symbol.
            kline_type (str): Kline type (e.g., "1m", "5m", "1h", "1d").
            params (dict, optional): Additional query parameters.
        Returns:
            dict: Kline data.
        """
        return await self._get(f"kline/{symbol}/{kline_type}", params=params)

    async def get_market_trades(self, symbol: str, params: Optional[Dict] = None) -> Dict:
        """
        Get recent market trades (public endpoint).

        Args:
            symbol (str): Market symbol.
            params (dict, optional): Query parameters.
        Returns:
            dict: Recent market trades.
        """
        return await self._get(f"market_trades/{symbol}", params=params)
