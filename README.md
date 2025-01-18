# Dida365/TickTick API Client

An unofficial Python client library for the Dida365/TickTick API, supporting both the Chinese (Dida365) and international (TickTick) versions of the service. Built with modern async Python and robust error handling.

This is a package created to facilitate task management automation. It is not affiliated with or endorsed by Dida365 or TickTick.

## API Documentation References

- Dida365 API: https://developer.dida365.com/api#/openapi
- TickTick API: https://developer.ticktick.com/docs#/openapi

## OAuth2 Setup

1. Get your OAuth2 credentials:
   - For TickTick: Visit https://developer.ticktick.com/manage
   - For Dida365: Visit https://developer.dida365.com/manage
   - Click "New App" to create a new application
   - After creation, you'll receive your Client ID and Client Secret

2. Configure OAuth2 redirect URL:
   - In your Manage App page, click "Edit" of your newly created app
   - Add the redirect URL: `http://localhost:8080/callback` at "OAuth redirect URL"
   - Save the changes
   - Note: If you want to use a different redirect URL, make sure to update it in both:
     - The app settings on TickTick/Dida365 developer portal
     - Your .env file (see below)

3. Configure your credentials:
   ```bash
   # .env file
   DIDA365_CLIENT_ID=your_client_id        # From step 1
   DIDA365_CLIENT_SECRET=your_client_secret # From step 1
   DIDA365_REDIRECT_URI=http://localhost:8080/callback  # From step 2
   DIDA365_SERVICE_TYPE=ticktick  # or dida365
   ```

## Features

- ✨ Full async support using `httpx`
- 🔒 OAuth2 authentication with automatic token management
- 📝 Type-safe with Pydantic v2 models
- 🌐 Configurable endpoints (Dida365/TickTick)
- 🛡️ Comprehensive error handling
- ⚡ Automatic retry mechanism
- 🔄 Environment file integration
- 📊 State management for tasks and projects

## Installation

```bash
pip install dida365
```

## Quick Start

```python
import asyncio
from datetime import datetime, timezone
from dida365 import Dida365Client, ServiceType, TaskCreate, ProjectCreate, TaskPriority

async def main():
    # Initialize client (credentials can also be loaded from .env file)
    client = Dida365Client(
        client_id="your_client_id",  # Optional if in .env
        client_secret="your_client_secret",  # Optional if in .env
        service_type=ServiceType.TICKTICK,  # or DIDA365
        redirect_uri="http://localhost:8080/callback",  # Optional
        save_to_env=True  # Automatically save credentials and tokens to .env
    )

    # First-time authentication:
    if not client.auth.token:
        # This will start a local server at the redirect_uri
        # and open your browser for authorization
        await client.authenticate()
        # Token will be automatically saved to .env if save_to_env=True

    # Create a project
    project = await client.create_project(
        ProjectCreate(
            name="My Project",
            color="#FF0000"
        )
    )

    # Create a task
    task = await client.create_task(
        TaskCreate(
            project_id=project.id,
            title="My new task",
            content="Task description",
            priority=TaskPriority.HIGH,
            start_date=datetime.now(timezone.utc),
            is_all_day=False,
            time_zone="UTC"
        )
    )
    
    print(f"Created task: {task.title}")

if __name__ == "__main__":
    asyncio.run(main())
```

## CRUD Operations

### Projects

```python
from dida365 import ProjectCreate, ProjectUpdate, ViewMode, ProjectKind, Dida365Client

async def manage_projects(client: Dida365Client):
    # Create a project
    project = await client.create_project(
        ProjectCreate(
            name="My Project",
            color="#FF0000",  # Optional: hex color code
            view_mode=ViewMode.KANBAN,  # Optional: LIST, KANBAN, TIMELINE
            kind=ProjectKind.TASK  # Optional: TASK, NOTE
        )
    )

    # Get project we just created
    project = await client.get_project(project_id=project.id)

    # Get project with all tasks and columns
    project_data = await client.get_project_with_data(project_id=project.id)
    print(f"Project {project_data.project.name} has {len(project_data.tasks)} tasks")
    for column in project_data.columns:  # Only present in KANBAN view
        print(f"Column: {column.name}")

    # Update project
    updated_project = await client.update_project(
        ProjectUpdate(
            id=project.id,
            name="Updated Project Name",
            color="#00FF00",
            view_mode=ViewMode.LIST
        )
    )

    # Delete project
    await client.delete_project(project_id=project.id)

    # List all projects
    projects = await client.get_projects()
    for project in projects:
        print(f"Project: {project.name} ({project.id})")
```

### Tasks

```python
from datetime import datetime, timezone
from dida365 import TaskCreate, TaskUpdate, TaskPriority, Dida365Client, Project

async def manage_tasks(client: Dida365Client, project: Project):
    # Create a task
    task = await client.create_task(
        TaskCreate(
            project_id=project.id,  # Required: tasks must belong to a project
            title="Complete documentation",
            content="Add CRUD examples",
            priority=TaskPriority.HIGH,  # Enum: NONE, LOW, MEDIUM, HIGH
            start_date=datetime.now(timezone.utc),
            due_date=datetime.now(timezone.utc),
            is_all_day=True,
            time_zone="UTC"
        )
    )

    # Read a task
    task = await client.get_task(project_id=project.id, task_id=task.id)

    # Update a task
    updated_task = await client.update_task(
        TaskUpdate(
            id=task.id,
            project_id=task.project_id,  # Both id and project_id are required
            title="Updated title",
            content="Added more details",
            priority=TaskPriority.MEDIUM
        )
    )

    # Complete a task
    await client.complete_task(project_id=task.project_id, task_id=task.id)
    
    # Delete a task
    await client.delete_task(project_id=task.project_id, task_id=task.id)
```

### State Management

The client maintains an internal state of tasks and projects:

```python
# Access cached state
tasks = client.state["tasks"]
projects = client.state["projects"]
tags = client.state["tags"]

# State is automatically updated when you:
# 1. Create new items
# 2. Update existing items
# 3. Delete items
```

## Configuration

The client can be configured through:
1. Environment variables
2. Constructor parameters
3. pyproject.toml settings

### Environment Variables

Create a `.env` file:
```bash
# Required credentials
DIDA365_CLIENT_ID=your_client_id
DIDA365_CLIENT_SECRET=your_client_secret

# Optional configurations
DIDA365_SERVICE_TYPE=ticktick     # or dida365 (default)
DIDA365_ACCESS_TOKEN=your_token   # Will be saved automatically after auth
DIDA365_BASE_URL=custom_url      # Optional: custom API endpoint
DIDA365_LOG_LEVEL=INFO          # Optional: DEBUG, INFO, WARNING, ERROR
```

You can also use a custom `.env` file location:
```python
from dotenv import load_dotenv

load_dotenv("/path/to/your/.env")
client = Dida365Client()  # Will load from the specified .env file
```

### Request Timeouts

Configure request timeouts in `pyproject.toml`:
```toml
[tool.dida365.request_timeout]
connect = 10.0  # Connection timeout
read = 30.0     # Read timeout
write = 30.0    # Write timeout
pool = 5.0      # Pool timeout
```

### Logging Configuration

```toml
[tool.dida365]
log_level = "INFO"
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
log_date_format = "%Y-%m-%d %H:%M:%S"
log_file = ""  # Set to a path to enable file logging
debug = false
```

## Error Handling

The library provides detailed error handling:

```python
from dida365.exceptions import (
    ApiError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError
)

try:
    task = await client.get_task("project_id", "task_id")
except NotFoundError:
    print("Task not found")
except AuthenticationError:
    print("Authentication failed - token may have expired")
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
except ValidationError as e:
    print(f"Invalid data: {e}")
except ApiError as e:
    print(f"API error: {e.status_code} - {e.message}")
```

## Author

Carter Yifeng Cheng ([@cyfine](https://github.com/cyfine))

## License

This project is licensed under the MIT License - see the LICENSE file for details. 