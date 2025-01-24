"""Main client module for the API."""
from typing import List, Optional, Dict, Any
import os
from pathlib import Path

from .auth import TokenInfo, OAuth2Manager
from .config import ApiConfig, ServiceType
from .http import HttpClient
from .models.project import Project, ProjectCreate, ProjectUpdate, ProjectData
from .models.task import Task, TaskCreate, TaskUpdate
from .settings import settings
from .exceptions import ValidationError
from .logger import logger


class Dida365Client:
    """Client for interacting with the Dida365/TickTick API."""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        service_type: ServiceType = None,
        redirect_uri: str = "http://localhost:8080/callback",
        save_to_env: bool = True
    ):
        """Initialize the client.
        
        Args:
            client_id: OAuth2 client ID (can be set via DIDA365_CLIENT_ID env var)
            client_secret: OAuth2 client secret (can be set via DIDA365_CLIENT_SECRET env var)
            service_type: Service type (dida365 or ticktick)
            redirect_uri: OAuth2 redirect URI
            save_to_env: Whether to save credentials and token to .env file
        """
        self.save_to_env = save_to_env
        
        # Try to get credentials from args or env
        self.client_id = client_id or settings.client_id
        self.client_secret = client_secret or settings.client_secret
        self.service_type = service_type or settings.service_type
        
        if not self.client_id or not self.client_secret:
            raise ValidationError(
                "Client ID and secret must be provided either through constructor "
                "or environment variables (DIDA365_CLIENT_ID, DIDA365_CLIENT_SECRET)"
            )
        
        self.config = ApiConfig(service_type=service_type)
        self.auth = OAuth2Manager(
            client_id=self.client_id,
            client_secret=self.client_secret,
            config=self.config,
            redirect_uri=redirect_uri
        )
        self.http = HttpClient(config=self.config)
        self.state: Dict[str, List[Any]] = {
            "tasks": [],
            "projects": [],
            "tags": [],
            "project_folders": []
        }

        # Load token from env if available and matches current client
        if settings.access_token and self._verify_token_client():
            logger.debug("Loading existing token from environment")
            self.auth.token = TokenInfo(
                access_token=settings.access_token,
                token_type="Bearer",
                expires_in=3600,  # Default 1 hour
                scope="tasks:write tasks:read"
            )
            self.http.token = settings.access_token

    def _verify_token_client(self) -> bool:
        """Verify that the token in env belongs to current client_id."""
        env_client_id = settings.client_id
        return bool(env_client_id and env_client_id == self.client_id)

    def _update_env_file(self, access_token: Optional[str] = None) -> None:
        """Update or create .env file with credentials and token.
        
        Args:
            access_token: Optional new access token to save
        """
        if not self.save_to_env:
            return

        env_path = Path(".env")
        existing_lines = []
        
        # Read existing env file if it exists
        if env_path.exists():
            with open(env_path, "r") as f:
                existing_lines = f.readlines()

        # Helper to update or add a variable
        def update_var(lines: List[str], key: str, value: str) -> List[str]:
            if not value:
                return lines
            new_line = f"{key}={value}\n"
            for i, line in enumerate(lines):
                if line.startswith(f"{key}="):
                    lines[i] = new_line
                    break
            else:
                lines.append(new_line)
            return lines

        # Update credentials and token
        lines = existing_lines
        lines = update_var(lines, "DIDA365_CLIENT_ID", self.client_id)
        lines = update_var(lines, "DIDA365_CLIENT_SECRET", self.client_secret)
        lines = update_var(lines, "DIDA365_SERVICE_TYPE", "ticktick" if self.config.service_type == ServiceType.TICKTICK else "dida365")  # Update service type
        if access_token:
            lines = update_var(lines, "DIDA365_ACCESS_TOKEN", access_token)

        # Write back to file
        with open(env_path, "w") as f:
            f.writelines(lines)
        
        logger.debug("Updated .env file with new credentials/token")

    async def authenticate(
        self,
        scope: str = "tasks:write tasks:read",
        state: str = "state",
        port: int = 8080
    ) -> TokenInfo:
        """Complete OAuth2 authentication flow."""
        token_info = await self.auth.authenticate(scope=scope, state=state, port=port)
        if token_info:
            await self.http.set_token(token_info.access_token)
            if self.save_to_env:
                self._update_env_file(access_token=token_info.access_token)
        return token_info

    async def exchange_code(self, code: str) -> TokenInfo:
        """Exchange authorization code for access token."""
        token_info = await self.auth.exchange_code(code)
        if token_info:
            await self.http.set_token(token_info.access_token)
            if self.save_to_env:
                self._update_env_file(access_token=token_info.access_token)
        return token_info



    # Task-related methods

    async def get_task(self, project_id: str, task_id: str) -> Task:
        """Get a task by project ID and task ID."""
        task = await self.http.get(
            f"project/{project_id}/task/{task_id}",
            model=Task,
        )
        return task

    async def create_task(self, task: TaskCreate) -> Task:
        """Create a new task."""
        created_task = await self.http.post(
            "task",
            json_data=task.model_dump(by_alias=True, exclude_none=True),
            model=Task,
        )
        if created_task:
            self.state["tasks"].append(created_task.model_dump())
        return created_task

    async def update_task(self, task: TaskUpdate) -> Task:
        """Update an existing task."""
        updated_task = await self.http.post(
            f"task/{task.id}",
            json_data=task.model_dump(by_alias=True, exclude_none=True),
            model=Task,
        )
        if updated_task:
            # Update state
            for i, t in enumerate(self.state["tasks"]):
                if t["id"] == task.id:
                    self.state["tasks"][i] = updated_task.model_dump()
                    break
        return updated_task

    async def complete_task(self, project_id: str, task_id: str) -> None:
        """Mark a task as completed."""
        await self.http.post(f"project/{project_id}/task/{task_id}/complete")
        # Update state
        for task in self.state["tasks"]:
            if task["id"] == task_id:
                task["status"] = 2  # Completed status
                break

    async def delete_task(self, project_id: str, task_id: str) -> None:
        """Delete a task."""
        await self.http.delete(f"project/{project_id}/task/{task_id}")
        # Update state
        self.state["tasks"] = [
            t for t in self.state["tasks"] if t["id"] != task_id]

    # Project-related methods

    async def get_projects(self) -> List[Project]:
        """Get all projects."""
        projects = await self.http.get("project", model=List[Project])
        if projects:
            self.state["projects"] = [p.model_dump() for p in projects]
        return projects

    async def get_project(self, project_id: str) -> Project:
        """Get a project by ID."""
        return await self.http.get(f"project/{project_id}", model=Project)

    async def get_project_with_data(self, project_id: str) -> ProjectData:
        """Get a project with its tasks and columns."""
        data = await self.http.get(f"project/{project_id}/data", model=ProjectData)
        if data:
            # Update state with project tasks
            for task in data.tasks:
                task_dict = task.model_dump()
                for i, t in enumerate(self.state["tasks"]):
                    if t["id"] == task.id:
                        self.state["tasks"][i] = task_dict
                        break
                else:
                    self.state["tasks"].append(task_dict)
        return data

    async def create_project(self, project: ProjectCreate) -> Project:
        """Create a new project."""
        created_project = await self.http.post(
            "project",
            json_data=project.model_dump(by_alias=True, exclude_none=True),
            model=Project,
        )
        if created_project:
            self.state["projects"].append(created_project.model_dump())
        return created_project

    async def update_project(self, project: ProjectUpdate) -> Project:
        """Update an existing project."""
        updated_project = await self.http.post(
            f"project/{project.id}",
            json_data=project.model_dump(by_alias=True, exclude_none=True),
            model=Project,
        )
        if updated_project:
            # Update state
            for i, p in enumerate(self.state["projects"]):
                if p["id"] == project.id:
                    self.state["projects"][i] = updated_project.model_dump()
                    break
        return updated_project

    async def delete_project(self, project_id: str) -> None:
        """Delete a project."""
        await self.http.delete(f"project/{project_id}")
        # Update state
        self.state["projects"] = [
            p for p in self.state["projects"] if p["id"] != project_id]

    # Authentication methods

    def get_authorization_url(
        self,
        scope: str = "tasks:write tasks:read",
        state: str = "state",
    ) -> str:
        """Get the authorization URL for OAuth2 flow."""
        return self.auth.get_authorization_url(scope=scope, state=state)
