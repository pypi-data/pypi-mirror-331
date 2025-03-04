from factory_sdk.datasets import Dataset
from factory_sdk.models import Models
from factory_sdk.adapters import Adapters
from factory_sdk.preprocessors import Preprocessors
from factory_sdk.dto.project import Project
from factory_sdk.dto.tenant import Tenant
from factory_sdk.evaluation import Evaluation
from factory_sdk.deployment import Deployment
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn, TransferSpeedColumn, TimeRemainingColumn


import requests
from pydantic import BaseModel
from factory_sdk.logging import logger
from typing import Optional, Type, Any
import os
from factory_sdk.exceptions.api import (
    NotFoundException,
    GeneralAPIException,
    ConflictException,
    AuthenticationException,
)
from rich import print
from hashlib import sha256
from requests.adapters import HTTPAdapter, Retry
from factory_sdk.recipe import RecipeBuilder

import logging

logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)

# Import tqdm for progress bar
from tqdm.auto import tqdm
from factory_sdk.dto.project import (
    WandbLoggingIntegration,
    NeptuneLoggingIntegration,
)

from requests_toolbelt.multipart.encoder import (
    MultipartEncoder,
    MultipartEncoderMonitor,
)

retry_adapter = HTTPAdapter(
    max_retries=Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
)


class Integrations:
    def __init__(self, client):
        self.client = client

    def use(self, wandb=None, neptune=None):
        assert (
            isinstance(wandb, WandbLoggingIntegration) or wandb is None
        ), "wandb must be an instance of WandbLoggingIntegration"
        assert (
            isinstance(neptune, NeptuneLoggingIntegration) or neptune is None
        ), "neptune must be an instance of NeptuneLoggingIntegration"

        project: Project = self.client.get(
            f"projects/{self.client._project.id}",
            response_class=Project,
            scope="tenant",
        )
        project.integrations.wandb = wandb
        project.integrations.neptune = neptune
        return self.client.put(
            f"projects/{self.client._project.id}", project, Project, scope="tenant"
        )


class FactoryClient:
    def __init__(
        self,
        tenant: str,
        project: str,
        token: str,
        host: str = "https://localhost:8443",
        verify_ssl: bool = True,
    ):
        """
        Initialize the FactoryClient with project, host, port, and SSL settings.
        """

        self._host = host
        self._token = token
        self.evalution = Evaluation(client=self)
        # self.environment=EnvironmentClient(client=self)
        self.integration = Integrations(client=self)
        self.dataset = Dataset(client=self)
        self.base_model = Models(client=self)
        self.adapter = Adapters(client=self)
        #self.preprocessor = Preprocessors(client=self)
        self.recipe = RecipeBuilder(client=self)
        self.deployment=Deployment(client=self)
        
        self._session = (
            requests.Session()
        )  # Use a session for performance and connection pooling
        self._verify_ssl = verify_ssl

        tenant, project = self._init(tenant, project)
        self._tenant: Tenant = tenant
        self._project: Project = project

        # print sucessuffly connetced
        print(
            f"🛸 FactoryClient is successfully connected and starts working on project [bold blue]{project.name}[/bold blue]\n"
        )

    def get_init_params(self):
        return {
            "tenant": self._tenant.name,
            "project": self._project.name,
            "host": self._host,
            "token": self._token,
            "verify_ssl": self._verify_ssl,
        }

    def _init(self, tenant, project):
        # fetch project and tenant id
        tenant: Tenant = self.get(
            f"tenants/{tenant}", response_class=Tenant, scope="names"
        )
        try:
            project = self.get(
                f"tenants/{tenant.id}/projects/{project}",
                response_class=Project,
                scope="names",
            )
        except NotFoundException:
            # create project
            print(
                f"Project [bold blue]{project}[/bold blue] not found. Creating new project..."
            )
            self._tenant = tenant
            project = self.post(
                f"projects",
                Project(name=project, tenant=tenant.id),
                response_class=Project,
                scope="tenant",
            )
        return tenant, project

    def _api_url(self, scope="project") -> str:
        """
        Construct the base API URL based on the host, port, SSL, and project.
        """

        if scope == "names":
            return f"{self._host}/api/1/names"
        if scope == "tenant":
            return f"{self._host}/api/1/tenants/{self._tenant.id}"
        return (
            f"{self._host}/api/1/tenants/{self._tenant.id}/projects/{self._project.id}"
        )

    def _request(self, method: str, path: str, scope="project", **kwargs) -> Any:
        """
        Internal method to handle HTTP requests.

        Args:
            method (str): HTTP method ('GET', 'POST', 'PUT', etc.).
            path (str): API endpoint path.
            **kwargs: Additional arguments to pass to the request.

        Returns:
            Any: The response JSON or content.
        """
        url = f"{self._api_url(scope=scope)}/{path}"
        res = self._session.request(
            method,
            url,
            headers={"Authorization": f"Bearer {self._token}"},
            verify=self._verify_ssl,
            **kwargs,
        )

        if res.status_code == 404:
            raise NotFoundException(f"Resource not found: {method} {path}")
        elif res.status_code == 409:
            raise ConflictException(f"Conflict: {method} {path}")
        elif res.status_code == 401:
            raise AuthenticationException(f"Authentication failed: {method} {path}")
        if res.status_code != 200 and res.status_code != 201:
            try:
                error_msg = res.json()
                logger.error(error_msg)
                raise GeneralAPIException(error_msg)
            except ValueError:
                raise GeneralAPIException(
                    f"Failed to {method} {path}. Status code: {res.status_code}"
                )

        try:
            return res.json()
        except ValueError:
            return res.content  # Return raw content if response is not JSON

    def get(
        self,
        path: str,
        response_class: Optional[Type[BaseModel]] = None,
        scope="project",
    ) -> Any:
        """
        Perform a GET request to the specified path.

        Args:
            path (str): The API endpoint path.
            response_class (Type[BaseModel], optional): Pydantic model class to parse the response.

        Returns:
            Any: The parsed response or raw JSON.
        """
        res_json = self._request("GET", path, scope=scope)
        if response_class and res_json:
            return response_class(**res_json)
        return res_json

    def post(
        self,
        path: str,
        data: BaseModel,
        response_class: Optional[Type[BaseModel]] = None,
        scope="project",
    ) -> Any:
        """
        Perform a POST request to the specified path with the provided data.

        Args:
            path (str): The API endpoint path.
            data (BaseModel): The data to send in the POST request.
            response_class (Type[BaseModel], optional): Pydantic model class to parse the response.

        Returns:
            Any: The parsed response or raw JSON.
        """
        res_json = self._request(
            "POST", path, json=data.model_dump() if data else None, scope=scope
        )
        if response_class and res_json:
            return response_class(**res_json)
        return res_json

    def put(
        self,
        path: str,
        data: BaseModel,
        response_class: Optional[Type[BaseModel]] = None,
        scope="project",
    ) -> Any:
        """
        Perform a PUT request to the specified path with the provided data.

        Args:
            path (str): The API endpoint path.
            data (BaseModel): The data to send in the PUT request.
            response_class (Type[BaseModel], optional): Pydantic model class to parse the response.

        Returns:
            Any: The parsed response or raw JSON.
        """
        res_json = self._request("PUT", path, json=data.model_dump(), scope=scope)
        if response_class and res_json:
            return response_class(**res_json)
        return res_json

    def download_files(self, url, target_path, scope="project"):
        base_url = f"{self._api_url(scope=scope)}/{url}"
        with requests.Session() as session:
            session.mount("", retry_adapter)
            res = session.get(
                base_url,
                headers={"Authorization": f"Bearer {self._token}"},
                verify=self._verify_ssl,
            )
            paths = res.json()

            with Progress(
                SpinnerColumn(),
                *Progress.get_default_columns(),
                TimeElapsedColumn(),
            ) as progress:
                # Create a task for overall file download progress
                overall_task = progress.add_task(
                    "[green]Downloading files...",
                    total=len(paths)
                )

                for path in paths:
                    url = f"{base_url}/{path['path']}"
                    res = session.get(
                        url,
                        headers={"Authorization": f"Bearer {self._token}"},
                        verify=self._verify_ssl,
                    )
                    download_url = res.json()["download_url"]
                    res = session.get(download_url, stream=True)
                    file_path = os.path.join(target_path, path["path"])
                    total_size = int(res.headers.get("content-length", 0))
                    
                    # Create a task for individual file download
                    file_task = progress.add_task(
                        f"[cyan]{os.path.basename(file_path)}",
                        total=total_size,
                        unit="B",
                        unit_scale=True
                    )

                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, "wb") as f:
                        for chunk in res.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                                progress.update(file_task, advance=len(chunk))
                    
                    # Update overall progress
                    progress.update(overall_task, advance=1)

    def download_file_or_directory(self, url, path, scope="project"):
        base_url = f"{self._api_url(scope=scope)}/{url}"
        with requests.Session() as session:
            session.mount("", retry_adapter)
            res = session.get(
                base_url,
                headers={"Authorization": f"Bearer {self._token}"},
                verify=self._verify_ssl,
                stream=True,
            )
            refs = res.json()

            for file in refs["files"]:
                download_url = file["download_url"]
                res = session.get(download_url, stream=True)
                subpath = file["path"].split("/")
                file_path = os.path.join(path, *subpath)

                total_size = int(res.headers.get("content-length", 0))
                with tqdm(
                    total=total_size,
                    unit="B",
                    unit_scale=True,
                    desc=os.path.basename(file_path),
                ) as progress_bar:
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, "wb") as f:
                        for chunk in res.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                                progress_bar.update(len(chunk))

    def upload_file(self, url, file_path, scope="project", progress=None):
        """
        Upload a file with progress tracking using Rich.

        Args:
            url (str): The upload endpoint
            file_path (str): Path to the file to upload
            scope (str, optional): Scope of the upload. Defaults to "project".
            progress (Progress, optional): Existing Rich progress bar to use. If None, creates a new one.
        """
        
        base_url = f"{self._api_url(scope=scope)}/{url}"
        upload_id = None
        should_close_progress = False

        try:
            with requests.Session() as session:
                session.mount("", retry_adapter)

                file_size = os.path.getsize(file_path)

                # Compute hash using buffer of 64MB
                digest = sha256()
                buffer_size = 64 * 1024 * 1024
                with open(file_path, "rb") as f:
                    while True:
                        part = f.read(buffer_size)
                        digest.update(part)
                        if not part:
                            break

                fingerprint = digest.hexdigest()

                try:
                    res = session.post(
                        base_url,
                        json={"size": file_size, "hash": fingerprint},
                        headers={"Authorization": f"Bearer {self._token}"},
                        verify=self._verify_ssl,
                    )
                    res.raise_for_status()  # Raise exception for non-2xx status codes
                    data = res.json()
                    upload_id = data["upload_id"]
                    upload_url = data["upload_url"]
                    upload_fields = data["upload_fields"]
                except requests.exceptions.RequestException as e:
                    error_msg = f"Error initializing upload: {str(e)}"
                    if hasattr(e, 'response') and e.response is not None:
                        try:
                            error_detail = e.response.json()
                            error_msg += f"\nResponse: {error_detail}"
                        except ValueError:
                            error_msg += f"\nResponse text: {e.response.text}"
                    raise RuntimeError(error_msg) from e

                # Create or use existing progress bar
                if progress is None:
                    progress = Progress(
                        *Progress.get_default_columns(),
                        TransferSpeedColumn(),
                        TimeRemainingColumn(),
                    )
                    should_close_progress = True
                    progress.start()

                with open(file_path, "rb") as f:
                    task_id = progress.add_task(
                        f"[cyan]Uploading {os.path.basename(file_path)}",
                        total=file_size,
                    )

                    def create_callback(progress_bar, task_id):
                        def callback(monitor):
                            progress_bar.update(task_id, completed=monitor.bytes_read)

                        return callback

                    encoder = MultipartEncoder(
                        fields={
                            **upload_fields,
                            "file": (os.path.basename(file_path), f),
                        }
                    )

                    monitor = MultipartEncoderMonitor(
                        encoder, create_callback(progress, task_id)
                    )

                    try:
                        res = requests.post(
                            upload_url,
                            data=monitor,
                            verify=self._verify_ssl,
                            headers={"Content-Type": monitor.content_type},
                        )
                        res.raise_for_status()
                    except requests.exceptions.RequestException as e:
                        error_msg = f"S3 upload error: {str(e)}"
                        if hasattr(e, 'response') and e.response is not None:
                            try:
                                error_detail = e.response.json()
                                error_msg += f"\nResponse: {error_detail}"
                            except ValueError:
                                error_msg += f"\nResponse text: {e.response.text}"
                        raise RuntimeError(error_msg) from e

                    # Remove task from progress bar if we're using an external one
                    if not should_close_progress:
                        progress.remove_task(task_id)

                try:
                    complete_url = f"{base_url}/complete/{upload_id}"
                    res = session.post(
                        complete_url,
                        headers={"Authorization": f"Bearer {self._token}"},
                        json={"fingerprint": fingerprint},
                        verify=self._verify_ssl,
                    )
                    res.raise_for_status()
                except requests.exceptions.RequestException as e:
                    error_msg = f"Error completing upload: {str(e)}"
                    if hasattr(e, 'response') and e.response is not None:
                        try:
                            error_detail = e.response.json()
                            error_msg += f"\nResponse: {error_detail}"
                        except ValueError:
                            error_msg += f"\nResponse text: {e.response.text}"
                    raise RuntimeError(error_msg) from e

        except Exception as e:
            # Catch all errors to ensure they are properly displayed
            print(f"Upload failed: {str(e)}")
            raise
        finally:
            # Close the progress bar if we created it
            if should_close_progress and progress is not None:
                progress.stop()
