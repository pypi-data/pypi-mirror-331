import os
import tempfile
from typing import List, Optional, Dict, Literal, Any
from urllib.parse import urlparse

import httpx
from httpx import Response, HTTPError
from pydantic import BaseModel, Field

from ipfabric.tools import raise_for_status


class Extension(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    slug: str
    status: str
    type: Optional[Literal["docker-zip", "docker-image"]] = None
    environmentVariables: Optional[List[Dict[str, str]]] = None


class ExtensionsResponse(BaseModel):
    extensions: List[Extension]


class Extensions(BaseModel):
    client: Any = Field(exclude=True)

    @property
    def extensions(self) -> List[Extension]:
        """
        Fetch all extensions.

        Returns:
            List[Extension]: List of all available extensions
        """
        response = ExtensionsResponse(extensions=raise_for_status(self.client.get("extensions")).json()["extensions"])
        return response.extensions

    def extension_by_id(self, extension_id: str) -> Extension:
        """
        Fetch a specific extension by ID.

        Args:
            extension_id (str): The ID of the extension to fetch

        Returns:
            Extension: The requested extension
        """
        return Extension(**raise_for_status(self.client.get(f"extensions/{extension_id}")).json())

    def logs_by_extension_id(self, extension_id: str) -> Dict:
        """
        Fetch paginated logs for a specific extension.

        Args:
            extension_id (str): The ID of the extension to fetch logs for

        Returns:
            Dict: The paginated logs response
        """
        return raise_for_status(self.client.get(f"extensions/{extension_id}/logs")).json()

    def extension_by_name(self, name: str) -> Extension:
        """
        Fetch a specific extension by name.
        """
        extension = next((ext for ext in self.extensions if ext.name == name), None)
        if extension is None:
            raise ValueError(f"Extension with name '{name}' not found")
        return extension

    def extension_by_slug(self, slug: str) -> Extension:
        """
        Fetch a specific extension by slug.
        """
        extension = next((ext for ext in self.extensions if ext.slug == slug), None)
        if extension is None:
            raise ValueError(f"Extension with slug '{slug}' not found")
        return extension

    def register_docker_zip(
        self,
        file: bytes,
        name: str,
        slug: str,
        description: str,
        environment_variables: Optional[Dict[str, str]] = None,
    ) -> Response:
        """
        Register a new extension using zipped source code. Raises an exception if the extension is not registered successfully.

        Args:
            file (bytes): The zipped source code file
            name (str): Name of the extension
            slug (str): Slug for the extension
            description (str): Description of the extension
            environment_variables (Optional[Dict[str, str]]): Environment variables for the extension
        """
        files = {"file": ("extension.zip", file, "application/zip")}

        data = {"name": name, "slug": slug, "description": description}

        if environment_variables:
            data["environmentVariables"] = environment_variables

        return raise_for_status(self.client.post("extensions/docker-zip", files=files, data=data, timeout=300))

    def register_docker_image(
        self,
        file: bytes,
        name: str,
        slug: str,
        description: str,
        environment_variables: Optional[Dict[str, str]] = None,
    ) -> Response:
        """
        Register a new extension using a docker image. Raises an exception if the extension is not registered successfully.

        Args:
            file (bytes): The tar file of the docker image
            name (str): Name of the extension
            slug (str): Slug for the extension
            description (str): Description of the extension
            environment_variables (Optional[Dict[str, str]]): Environment variables for the extension
        """
        files = {"file": ("image.tar", file, "application/x-tar")}

        data = {"name": name, "slug": slug, "description": description}

        if environment_variables:
            data["environmentVariables"] = [
                {"name": key, "value": value} for key, value in environment_variables.items()
            ]

        return raise_for_status(self.client.post("extensions/docker-image", files=files, data=data, timeout=300))

    def start_extension(self, extension_id: str) -> Response:
        """
        Start an extension by its ID. Raises an exception if the extension fails to start.

        Args:
            extension_id (str): The ID of the extension to start
        """
        return raise_for_status(self.client.post(f"extensions/{extension_id}/start"))

    def stop_extension(self, extension_id: str) -> Response:
        """
        Stop an extension by its ID. Raises an exception if the extension fails to stop.

        Args:
            extension_id (str): The ID of the extension to stop
        """
        return raise_for_status(self.client.post(f"extensions/{extension_id}/stop"))

    def unregister_extension(self, extension_id: str) -> Response:
        """
        Unregister an extension by its ID. Raises an exception if the extension fails to unregister.

        Args:
            extension_id (str): The ID of the extension to unregister
        """
        return raise_for_status(self.client.delete(f"extensions/{extension_id}"))

    def register_from_git_url(
        self,
        git_url: str,
        name: str,
        slug: str,
        description: str,
        branch: str = "main",
        environment_variables: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Register an extension from a Git repository URL. Supports GitHub and GitLab repositories.
        Downloads the repository, creates a ZIP file, and registers it as a docker-zip extension.

        Args:
            git_url (str): URL to the Git repository (GitHub or GitLab)
            name (str): Name of the extension
            slug (str): Slug for the extension
            description (str): Description of the extension
            branch (str): Branch to download (default: "main")
            environment_variables (Optional[Dict[str, str]]): Environment variables for the extension

        Example:
            client.extensions.register_from_git_url(
                "https://github.com/username/repo",
                "My Extension",
                "my-extension",
                "Description",
                branch="main"
            )
        """
        parsed_url = urlparse(git_url)

        path_parts = parsed_url.path.rstrip(".git").strip("/").split("/")

        if "github.com" in parsed_url.netloc:
            if len(path_parts) != 2:
                raise ValueError("Invalid GitHub URL format")
            user, repo = path_parts
            download_url = f"https://github.com/{user}/{repo}/archive/{branch}.zip"

        elif "gitlab.com" in parsed_url.netloc:
            if len(path_parts) < 2:
                raise ValueError("Invalid GitLab URL format")
            project = path_parts[-1]  # Last part is the project name
            group = "/".join(path_parts[:-1])  # Everything else is the group path
            download_url = f"https://gitlab.com/{group}/{project}/-/archive/{branch}/{project}-{branch}.zip"

        else:
            raise ValueError("Only GitHub and GitLab repositories are supported")

        response = httpx.get(download_url)
        if response.status_code != 200:
            raise HTTPError(f"Failed to download repository: {response.status_code}")

        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(response.content)

        try:
            with open(tmp_file.name, "rb") as f:
                self.register_docker_zip(
                    file=f.read(),
                    name=name,
                    slug=slug,
                    description=description,
                    environment_variables=environment_variables,
                )
        finally:
            os.unlink(tmp_file.name)
