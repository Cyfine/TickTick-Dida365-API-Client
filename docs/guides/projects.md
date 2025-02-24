# Working with Projects

This guide covers all project-related operations available in the API client.

## Project Models

### ProjectCreate
Used when creating a new project:

```python
from dida365 import ProjectCreate, ViewMode, ProjectKind

project = ProjectCreate(
    name="My Project",              # Required: Project name
    color="#FF0000",               # Optional: Hex color code or "#transparent" for no color
    view_mode=ViewMode.KANBAN,     # Optional: LIST, KANBAN, TIMELINE
    kind=ProjectKind.TASK          # Optional: TASK, NOTE
)
```

### ProjectUpdate
Used when updating an existing project:

```python
from dida365 import ProjectUpdate

update = ProjectUpdate(
    id="project_id",              # Required: Project ID
    name="Updated Name",          # Optional: New name
    color="#transparent",         # Optional: New color (use "#transparent" to remove color)
    view_mode=ViewMode.LIST,     # Optional: New view mode
    kind=ProjectKind.TASK        # Optional: New kind
)
```

## Basic Operations

### Create a Project

```python
# Simple creation
project = await client.create_project(
    ProjectCreate(name="Simple Project")
)

# Full options
project = await client.create_project(
    ProjectCreate(
        name="Detailed Project",
        color="#FF0000",  # Or use "#transparent" for no color
        view_mode=ViewMode.KANBAN,
        kind=ProjectKind.TASK
    )
)
```

### Get Projects

```python
# Get all projects
projects = await client.get_projects()

# Get a specific project
project = await client.get_project("project_id")

# Get project with all its data (tasks and columns)
project_data = await client.get_project_with_data("project_id")
print(f"Project has {len(project_data.tasks)} tasks")
for column in project_data.columns:  # Only in KANBAN view
    print(f"Column: {column.name}")
```


!!! Inbox
    The inbox is a special type of project that is not returned by `get_projects()`. However, you can still create tasks in the inbox by using an empty string (`""`) as the `project_id`. When you create a task in the inbox, the returned task's `project_id` will contain the actual inbox project_id.



### Update a Project

```python
# Update specific fields
updated = await client.update_project(
    ProjectUpdate(
        id="project_id",
        name="New Name"
    )
)

# Full update
updated = await client.update_project(
    ProjectUpdate(
        id="project_id",
        name="Updated Project",
        color="#00FF00",  # Or use "#transparent" to remove color
        view_mode=ViewMode.TIMELINE,
        kind=ProjectKind.TASK
    )
)
```

### Delete a Project

```python
await client.delete_project("project_id")
```

## Project Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | str | Yes (update) | Project identifier |
| `name` | str | Yes (create) | Project name |
| `color` | str | No | Hex color code (e.g., "#FF0000") or "#transparent" for no color |
| `view_mode` | ViewMode | No | View mode (LIST, KANBAN, TIMELINE) |
| `kind` | ProjectKind | No | Project kind (TASK, NOTE) |
| `closed` | bool | No | Whether project is closed |
| `group_id` | str | No | Project group identifier |
| `permission` | ProjectPermission | No | Access level (READ, WRITE, COMMENT) |

## View Modes

```python
from dida365 import ViewMode

# Available view modes:
ViewMode.LIST      # Default list view
ViewMode.KANBAN    # Kanban board view
ViewMode.TIMELINE  # Timeline/calendar view
```

## Project Kinds

```python
from dida365 import ProjectKind

# Available project kinds:
ProjectKind.TASK  # Regular task project
ProjectKind.NOTE  # Note-taking project
```

## Error Handling

```python
from dida365.exceptions import NotFoundError, ValidationError

try:
    project = await client.get_project("non_existent_id")
except NotFoundError:
    print("Project not found")
except ValidationError as e:
    print(f"Invalid data: {e}")
```

## Complete Example

```python
from dida365 import (
    Dida365Client,
    ProjectCreate,
    ProjectUpdate,
    ViewMode,
    ProjectKind
)

async def manage_projects():
    client = Dida365Client()
    
    # Create a project
    project = await client.create_project(
        ProjectCreate(
            name="My Project",
            color="#FF0000",  # Or use "#transparent" for no color
            view_mode=ViewMode.KANBAN
        )
    )
    
    # Get all tasks in the project
    data = await client.get_project_with_data(project.id)
    print(f"Project has {len(data.tasks)} tasks")
    
    # Update project
    updated = await client.update_project(
        ProjectUpdate(
            id=project.id,
            name="Updated Project",
            view_mode=ViewMode.TIMELINE
        )
    )
    
    # Delete when done
    await client.delete_project(project.id)
``` 