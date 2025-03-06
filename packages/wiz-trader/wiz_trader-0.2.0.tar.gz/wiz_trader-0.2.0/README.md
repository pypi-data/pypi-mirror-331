# WizTrader SDK

A Python SDK for connecting to the Wizzer trading platform.

## Installation

You can install the package directly from PyPI:

```bash
pip install wiz_trader
```

## Features

- Real-time market data through WebSocket connection
- Automatic reconnection with exponential backoff
- Subscribe/unsubscribe to instruments
- Customizable logging levels

## Quick Start

```python
import asyncio
from wiz_trader import QuotesClient

# Callback function to process market data
def process_tick(data):
    print(f"Received tick: {data}")

async def main():
    # Initialize client with direct parameters
    client = QuotesClient(
        base_url="wss://your-websocket-url.com/quotes", 
        token="your-jwt-token",
        log_level="info"  # Options: "error", "info", "debug"
    )
    
    # Set callback
    client.on_tick = process_tick
    
    # Connect in the background
    connection_task = asyncio.create_task(client.connect())
    
    # Subscribe to instruments
    await client.subscribe(["NSE:SBIN:3045"])
    
    # Keep the connection running
    try:
        await asyncio.sleep(3600)  # Run for 1 hour
    except KeyboardInterrupt:
        # Unsubscribe and close
        await client.unsubscribe(["NSE:SBIN:3045"])
        await client.close()
        
    await connection_task

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

You can configure the client in two ways:

1. **Direct parameter passing** (recommended):
   ```python
   client = QuotesClient(
       base_url="wss://your-websocket-url.com/quotes", 
       token="your-jwt-token",
       log_level="info"
   )
   ```

2. **System environment variables**:
   - `WZ__QUOTES_BASE_URL`: WebSocket URL for the quotes server
   - `WZ__TOKEN`: JWT token for authentication

   ```python
   # The client will automatically use the environment variables if parameters are not provided
   client = QuotesClient(log_level="info")
   ```

## Advanced Usage

Check the `examples/` directory for more detailed examples:

- `example_manual.py`: Demonstrates direct configuration with parameters

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.