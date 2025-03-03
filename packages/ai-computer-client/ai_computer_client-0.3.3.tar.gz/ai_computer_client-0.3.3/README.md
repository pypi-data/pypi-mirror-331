# AI Computer Python Client

A Python client for interacting with the AI Computer service. This client provides a simple interface for executing Python code in an isolated sandbox environment.

## Installation

```bash
pip install ai-computer-client
```

## Quick Start

```python
import asyncio
from ai_computer import SandboxClient

async def main():
    # Initialize the client
    client = SandboxClient()
    
    # Setup the client (gets token and creates sandbox)
    setup_response = await client.setup()
    if not setup_response.success:
        print(f"Setup failed: {setup_response.error}")
        return
    
    try:
        # Example 1: Simple code execution
        code = """x = 10
y = 20
result = x + y
print(f"The sum is: {result}")"""
        
        print("\nExample 1: Simple execution")
        print("-" * 50)
        response = await client.execute_code(code)
        if response.success:
            print("Execution result:", response.data)
        else:
            print("Execution failed:", response.error)

        # Example 2: Streaming execution
        code = """import time

for i in range(5):
    print(f"Processing step {i + 1}")
    time.sleep(1)  # Simulate work
    
result = "Calculation complete!"
print(result)"""
        
        print("\nExample 2: Streaming execution")
        print("-" * 50)
        async for event in client.execute_code_stream(code):
            if event.type == 'stdout':
                print(f"Output: {event.data}")
            elif event.type == 'stderr':
                print(f"Error: {event.data}")
            elif event.type == 'error':
                print(f"Execution error: {event.data}")
                break
            elif event.type == 'completed':
                print("Execution completed")
                break
    
    finally:
        # Clean up
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
```

Example output:
```
Example 1: Simple execution
--------------------------------------------------
Execution result: {'output': 'The sum is: 30\n', 'sandbox_id': '06a30496-b535-47b0-9fe7-34f7ec483cd7'}

Example 2: Streaming execution
--------------------------------------------------
Output: Processing step 1
Output: Processing step 2
Output: Processing step 3
Output: Processing step 4
Output: Processing step 5
Output: Calculation complete!
Execution completed
```

## Features

- Asynchronous API for efficient execution
- Real-time streaming of code output
- Automatic sandbox management
- Error handling and timeouts
- Type hints for better IDE support

## API Reference

### SandboxClient

The main client class for interacting with the AI Computer service.

```python
client = SandboxClient(base_url="http://api.aicomputer.dev")
```

#### Methods

##### `async setup() -> SandboxResponse`
Initialize the client and create a sandbox. This must be called before executing any code.

```python
response = await client.setup()
if response.success:
    print("Sandbox ready")
```

##### `async execute_code(code: str, timeout: int = 30) -> SandboxResponse`
Execute Python code and return the combined output.

```python
code = """
x = 10
y = 20
result = x + y
print(f"The sum is: {result}")
"""

response = await client.execute_code(code)
if response.success:
    print("Output:", response.data['output'])
```

##### `async execute_code_stream(code: str, timeout: int = 30) -> AsyncGenerator[StreamEvent, None]`
Execute Python code and stream the output in real-time.

```python
async for event in client.execute_code_stream(code):
    if event.type == 'stdout':
        print("Output:", event.data)
    elif event.type == 'stderr':
        print("Error:", event.data)
```

##### `async cleanup() -> SandboxResponse`
Delete the sandbox and clean up resources.

```python
await client.cleanup()
```

### Response Types

#### SandboxResponse
```python
@dataclass
class SandboxResponse:
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
```

#### StreamEvent
```python
@dataclass
class StreamEvent:
    type: str  # 'stdout', 'stderr', 'error', 'completed'
    data: str
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License 