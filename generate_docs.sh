#!/bin/bash

# Generate documentation for Orderly SDK
# This script uses the correct pdoc command-line arguments

echo "Generating documentation..."

# Create docs directory
mkdir -p docs

# Run pdoc with all the configuration options
uv run pdoc src/orderly_sdk \
  --output-directory docs \
  --docformat google \
  --show-source \
  --search \
  --math \
  --no-include-undocumented \
  --edit-url "orderly_sdk=https://github.com/longcipher/orderly-sdk-py/tree/master/src/orderly_sdk/" \
  --footer-text "Orderly SDK for Python - <a href='https://github.com/longcipher/orderly-sdk-py'>GitHub</a> | <a href='https://pypi.org/project/orderly-sdk/'>PyPI</a> | <a href='https://orderly.network/docs/build-on-evm/building-on-evm'>Official API Docs</a>"

echo "Documentation generated successfully in ./docs/"
echo "Open ./docs/index.html in your browser to view the documentation."
