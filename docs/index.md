# Dida365/TickTick API Client Documentation

Welcome to the documentation for the Dida365/TickTick API Client. This Python package provides a modern, async interface to interact with both Dida365 and TickTick task management services.

## Quick Navigation

- [Authentication](guides/authentication.md) - Configure OAuth2 authentication
- [Projects Guide](guides/projects.md) - Working with projects
- [Tasks Guide](guides/tasks.md) - Managing tasks
- [API Reference](api/client.md) - Complete API documentation

## Features

- ✨ Full async support using `httpx`
- 🔒 OAuth2 authentication with automatic token management
- 📝 Type-safe with Pydantic v2 models
- 🌐 Works with both TickTick and Dida365 APIs
- 🛡️ Comprehensive error handling
- ⚡ Automatic retry mechanism
- 🔄 Environment file integration
- 📊 State management for tasks and projects

## Installation

```bash
pip install dida365
```

## Basic Example

```python
from dida365 import Dida365Client, ServiceType

async def main():
    # Initialize client
    client = Dida365Client(
        client_id="your_client_id",
        client_secret="your_client_secret",
        service_type=ServiceType.TICKTICK  # or DIDA365
    )
    
    # Authenticate (opens browser for OAuth)
    await client.authenticate()
    
    # Get all projects
    projects = await client.get_projects()
    print(f"Found {len(projects)} projects")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 
```