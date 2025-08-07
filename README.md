
# Orderly SDK for Python

[![PyPI version](https://badge.fury.io/py/orderly-sdk.svg)](https://badge.fury.io/py/orderly-sdk)
[![Documentation](https://img.shields.io/badge/docs-orderly_sdk-green)](https://longcipher.github.io/orderly-sdk-py/)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/longcipher/orderly-sdk-py/blob/master/LICENSE)

Async Python SDK for [Orderly.Network](https://orderly.network/) EVM API (v2). Provides easy-to-use, fully async REST and WebSocket clients for trading, account management, and market data.

> **Note:** Only async REST and WebSocket APIs are maintained.

---

## ✨ Features

- 🚀 **Fully async** REST API client (`AsyncClient`)
- 📡 **Real-time WebSocket** clients for public and private streams
- 🔐 **Ed25519 signature** support for secure authentication
- 📊 **Complete API coverage** - trading, positions, market data, account management
- 🛠️ **Type hints** throughout the codebase
- 📝 **Comprehensive logging** and error handling
- 📖 **Example scripts** for quick start
- 🔧 **Easy configuration** with environment variables support

---

## 🚀 Installation

```bash
pip install orderly-sdk
```

**Requirements:** Python 3.13+

---

## 🏃 Quick Start

### REST API Example

```python
from asyncio import run
from orderly_sdk.rest import AsyncClient
from orderly_sdk.log import logger

async def main():
    client = AsyncClient(
        account_id="<YOUR_ACCOUNT_ID>",
        orderly_key="<YOUR_ORDERLY_KEY>",
        orderly_secret="<YOUR_ORDERLY_SECRET>",
        endpoint="https://testnet-api-evm.orderly.org",
    )
    
    # Get account info
    account_info = await client.get_account_info()
    logger.info(f"Account: {account_info}")
    
    # Get positions
    positions = await client.get_all_positions()
    logger.info(f"Positions: {positions}")
    
    # Get available symbols
    symbols = await client.get_available_symbols()
    logger.info(f"Available symbols: {symbols}")
    
    await client.close_connection()

run(main())
```

### WebSocket API Example

```python
from asyncio import run
from orderly_sdk.ws import OrderlyPublicWsManager
from orderly_sdk.log import logger

async def main():
    ws_client = OrderlyPublicWsManager(
        account_id="<YOUR_ACCOUNT_ID>",
        endpoint="wss://testnet-ws-evm.orderly.org/ws/stream/",
    )
    
    # Subscribe to market data
    await ws_client.subscribe_bbos()  # Best bid/offer
    await ws_client.subscribe_trade("PERP_ETH_USDC")  # Trades
    await ws_client.subscribe_ticker()  # 24h tickers
    
    ws_client.start()
    
    while True:
        bbos_data = await ws_client.recv("bbos", timeout=30)
        logger.info(f"BBOS: {bbos_data}")

run(main())
```

---## ⚙️ Configuration

### Environment Setup

You can set credentials via environment variables or directly in code:

```bash
export ORDERLY_ACCOUNT_ID="0x..."
export ORDERLY_KEY="..."
export ORDERLY_SECRET="..."
export ORDERLY_REST_ENDPOINT="https://testnet-api-evm.orderly.org"
export ORDERLY_WS_PUBLIC_ENDPOINT="wss://testnet-ws-evm.orderly.org/ws/stream/"
export ORDERLY_WS_PRIVATE_ENDPOINT="wss://testnet-ws-private-evm.orderly.org/v2/ws/private/stream/"
```

### Configuration Template

See `examples/configs.py` for a complete configuration template:

```python
# Testnet Configuration
ACCOUNT_ID = "0x4546c076e1d6ae0013195316c0c7b405699c839bb760a42f41005103134dcf3f"
ORDERLY_KEY = "your_orderly_key_here"
ORDERLY_SECRET = "your_orderly_secret_here"
REST_ENDPOINT = "https://testnet-api-evm.orderly.org"
WS_PUBLIC_ENDPOINT = "wss://testnet-ws-evm.orderly.org/ws/stream/"
WS_PRIVATE_ENDPOINT = "wss://testnet-ws-private-evm.orderly.org/v2/ws/private/stream/"

# Mainnet Configuration
# REST_ENDPOINT = "https://api-evm.orderly.org"
# WS_PUBLIC_ENDPOINT = "wss://ws-evm.orderly.org/ws/stream/"
# WS_PRIVATE_ENDPOINT = "wss://ws-private-evm.orderly.org/v2/ws/private/stream/"
```

---

## 📚 API Usage Examples

### REST API - Trading Operations

```python
from orderly_sdk import AsyncClient

async def trading_example():
    client = AsyncClient(
        account_id="your_account_id",
        orderly_key="your_key", 
        orderly_secret="your_secret",
        endpoint="https://testnet-api-evm.orderly.org"
    )
    
    # Create a limit order
    order = await client.create_order({
        "symbol": "PERP_ETH_USDC",
        "order_type": "LIMIT",
        "side": "BUY", 
        "order_quantity": "0.1",
        "order_price": "2000.00"
    })
    
    # Get order status
    order_detail = await client.get_order(order["order_id"])
    
    # Cancel order
    cancel_result = await client.cancel_order(order["order_id"])
    
    # Get trading history
    trades = await client.get_trades({
        "symbol": "PERP_ETH_USDC",
        "limit": 50
    })
    
    await client.close_connection()
```

### REST API - Market Data

```python
async def market_data_example():
    client = AsyncClient(endpoint="https://testnet-api-evm.orderly.org")
    
    # Get available symbols
    symbols = await client.get_available_symbols()
    
    # Get orderbook
    orderbook = await client.get_orderbook("PERP_ETH_USDC", max_level=20)
    
    # Get kline data
    klines = await client.get_kline("PERP_ETH_USDC", "1h", {
        "limit": 100
    })
    
    # Get recent trades
    trades = await client.get_market_trades("PERP_ETH_USDC")
    
    # Get funding rates
    funding = await client.get_funding_rates("PERP_ETH_USDC")
    
    await client.close_connection()
```

### WebSocket - Private Data Streams

```python
from orderly_sdk import OrderlyPrivateWsManager

async def private_websocket_example():
    ws = OrderlyPrivateWsManager(
        account_id="your_account_id",
        orderly_key="your_key",
        orderly_secret="your_secret", 
        endpoint="wss://testnet-ws-private-evm.orderly.org/v2/ws/private/stream/"
    )
    
    # Subscribe to private data feeds
    await ws.subscribe_position()  # Position updates
    await ws.subscribe_balance()   # Balance changes
    await ws.subscribe_order()     # Order status updates
    await ws.subscribe_trade()     # Private trade fills
    
    ws.start()
    
    # Listen to different data streams
    while True:
        try:
            # Get position updates
            position_update = await ws.recv("position", timeout=10)
            print(f"Position: {position_update}")
            
        except asyncio.TimeoutError:
            # Handle timeout - no position updates
            print("No position updates")
            continue
```

---

## 📖 API Reference

### REST Client Methods

| Method | Description | Endpoint Type |
|--------|-------------|---------------|
| `get_maintenance_info()` | Get system maintenance status | Public |
| `get_available_symbols()` | Get available trading symbols | Public |
| `get_orderbook(symbol, max_level)` | Get orderbook data | Public |
| `get_kline(symbol, type, params)` | Get kline/candlestick data | Public |
| `get_market_trades(symbol)` | Get recent market trades | Public |
| `get_funding_rates(symbol)` | Get funding rates | Public |
| `get_account_info()` | Get account information | Private |
| `get_user_statistics()` | Get user trading statistics | Private |
| `get_all_positions()` | Get all positions | Private |
| `get_current_holding()` | Get current asset holdings | Private |
| `create_order(order_params)` | Create a new order | Private |
| `get_order(order_id)` | Get order details | Private |
| `cancel_order(order_id)` | Cancel an order | Private |
| `batch_cancel_orders(order_ids)` | Cancel multiple orders | Private |
| `get_orders(params)` | Get orders list | Private |
| `get_trades(params)` | Get trade history | Private |

### WebSocket Topics

#### Public Topics
- `bbos` - Best bid/offer updates
- `{symbol}@trade` - Real-time trades
- `{symbol}@orderbook` - Orderbook updates  
- `{symbol}@kline_{interval}` - Kline data
- `24h_tickers` - 24h ticker statistics

#### Private Topics (requires authentication)
- `position` - Position updates
- `balance` - Balance changes
- `order` - Order status updates
- `trade` - Private trade fills
- `liquidation` - Liquidation events

### Error Handling

```python
from orderly_sdk.exceptions import OrderlyAPIException, OrderlyRequestException

try:
    result = await client.create_order(order_params)
except OrderlyAPIException as e:
    print(f"API Error: {e.message} (Code: {e.code})")
except OrderlyRequestException as e:
    print(f"Request Error: {e.message}")
```

---

## 🔧 Advanced Usage

### Custom Logging

```python
from orderly_sdk.log import set_level

# Set log level
set_level("DEBUG")  # Options: DEBUG, INFO, WARNING, ERROR
```

### Connection Management

```python
# REST Client - Always close connections
async with AsyncClient(...) as client:
    result = await client.get_account_info()
# Automatically closed

# Or manually
client = AsyncClient(...)
try:
    result = await client.get_account_info()
finally:
    await client.close_connection()
```

### WebSocket Reconnection

The WebSocket clients handle reconnection automatically:
- Automatic ping/pong heartbeat
- Reconnection on connection loss
- Re-subscription to topics after reconnection
- Authentication renewal for private streams

---

## 📂 Project Structure

```
orderly-sdk-py/
├── src/orderly_sdk/
│   ├── __init__.py          # Package initialization and exports
│   ├── rest.py             # REST API client
│   ├── ws.py               # WebSocket clients
│   ├── exceptions.py       # Custom exceptions
│   ├── helpers.py          # Helper utilities
│   └── log.py              # Logging configuration
├── examples/               # Usage examples
│   ├── configs.py          # Configuration template
│   ├── public_rest.py      # Public REST API examples
│   ├── private_rest.py     # Private REST API examples
│   ├── public_ws.py        # Public WebSocket examples
│   └── private_ws.py       # Private WebSocket examples
├── tests/                  # Test files
├── pyproject.toml         # Project configuration
├── README.md              # This file
└── LICENSE                # Apache 2.0 License
```

---

## 🧪 Examples

See the [`examples/`](./examples/) directory for ready-to-run scripts:

- **`public_rest.py`** — Query public REST endpoints (market data, system info)
- **`private_rest.py`** — Query private REST endpoints (requires credentials)  
- **`public_ws.py`** — Subscribe to public WebSocket topics (market streams)
- **`private_ws.py`** — Subscribe to private WebSocket topics (account streams)

Run examples:
```bash
cd examples/
# Edit configs.py with your credentials
python public_rest.py
python private_ws.py
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/longcipher/orderly-sdk-py.git
   cd orderly-sdk-py
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run tests**
   ```bash
   pytest tests/
   ```

5. **Format code**
   ```bash
   ruff format .
   ruff check .
   ```

6. **Generate documentation**
   ```bash
   pdoc orderly_sdk -o docs/
   ```

### Contribution Guidelines

- Fork the repository and create a feature branch
- Write tests for new functionality
- Follow existing code style (use `ruff` for formatting)
- Update documentation and examples as needed
- Submit a pull request with a clear description

### Reporting Issues

Please use the [GitHub Issues](https://github.com/longcipher/orderly-sdk-py/issues) page to report bugs or request features.

---

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- [Official Orderly.Network Documentation](https://orderly.network/docs/build-on-evm/building-on-evm)
- [Python SDK Documentation (pdoc)](https://longcipher.github.io/orderly-sdk-py/)
- [PyPI Package](https://pypi.org/project/orderly-sdk/)
- [GitHub Repository](https://github.com/longcipher/orderly-sdk-py)

---

**Happy Trading! 🚀**
