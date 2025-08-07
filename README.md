
# Orderly SDK for Python

[![PyPI version](https://badge.fury.io/py/orderly-sdk.svg)](https://badge.fury.io/py/orderly-sdk)
[![Documentation](https://img.shields.io/badge/docs-orderly_sdk-green)](https://longcipher.github.io/orderly-sdk-py/)

Async Python SDK for [Orderly.Network](https://orderly.network/) EVM API (v2). Provides easy-to-use, fully async REST and WebSocket clients for trading, account management, and market data.

> **Note:** Only async REST and WebSocket APIs are maintained.

---

## Features

- Fully async REST API client (`AsyncClient`)
- Async WebSocket clients for public and private streams
- Ed25519 signature support for secure authentication
- Simple logging and error handling
- Example scripts for quick start

---

## Installation

```bash
pip install orderly-sdk
```

---

## Quick Start

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
	stats = await client.get_user_statistics()
	logger.info(stats)
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
	ws_client.subscribe("bbos")
	ws_client.start()
	while True:
		res = await ws_client.recv("bbos")
		logger.info("bbos: {}", res)

run(main())
```

---

## Configuration

Set your credentials and endpoints in your code or via environment variables. See `examples/configs.py` for a template:

```python
ACCOUNT_ID = "0x..."
ORDERLY_KEY = "..."
ORDERLY_SECRET = "..."
REST_ENDPOINT = "https://testnet-api-evm.orderly.org"
WS_PUBLIC_ENDPOINT = "wss://testnet-ws-evm.orderly.org/ws/stream/"
WS_PRIVATE_ENDPOINT = "wss://testnet-ws-private-evm.orderly.org/v2/ws/private/stream/"
```

---

## API Reference

- [Orderly EVM API Docs](https://orderly.network/docs/build-on-evm/building-on-evm)
- [Auto-generated Python SDK Docs (pdoc)](https://longcipher.github.io/orderly-sdk-py/)

---

## Examples

See the [`examples/`](./examples/) directory for ready-to-run scripts:

- `public_rest.py` — Query public REST endpoints
- `private_rest.py` — Query private REST endpoints (requires credentials)
- `public_ws.py` — Subscribe to public WebSocket topics
- `private_ws.py` — Subscribe to private WebSocket topics (requires credentials)

---

## Contributing

Contributions, issues, and feature requests are welcome! Please open an issue or pull request on [GitHub](https://github.com/longcipher/orderly-sdk-py).

---

## License

Apache-2.0
