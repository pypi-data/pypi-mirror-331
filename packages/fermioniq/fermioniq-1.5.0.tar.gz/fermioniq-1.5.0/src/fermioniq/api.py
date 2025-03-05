import json
import urllib.parse
from datetime import datetime
from typing import Any, Optional

import requests
from pydantic import BaseModel
from requests import Response
from rich import box
from rich.table import Table

from fermioniq.custom_logging.jobs_table_functions import (
    format_gpu_resources,
    format_status,
    format_time,
)

# DOCUMENT THIS


class ApiError(RuntimeError):

    status_code: int
    reason: str
    url: str
    response_body: str

    def __init__(
        self,
        msg: Any,
        status_code: int,
        reason: str,
        url: str,
        body: str,
    ):
        super().__init__(msg)
        self.status_code = status_code
        self.reason = reason
        self.response_body = body
        self.url = url


class NoiseModel(BaseModel):
    description: str
    name: str


class JwtResponse(BaseModel):
    jwt_token: str
    user_id: str
    expiration_date: datetime


class Resource(BaseModel):
    count: int
    name: str


class ResourceDetails(BaseModel):
    elapsed_time: float
    resources: list[Resource] = []
    backend: str

    def _format_resources(self) -> dict[str, str]:
        resource_names = ("cpu", "mem")
        counts_by_name = {resource.name: resource.count for resource in self.resources}
        formatted_resources = {
            f"{name}": str(counts_by_name.get(name, "-")) for name in resource_names
        }
        formatted_resources.update(
            {
                "backend": format_gpu_resources(self.backend)
                if self.backend != ""
                else "-"
            }
        )
        return formatted_resources


class JobResponse(BaseModel):
    id: str
    job_label: Optional[str] = None
    user_id: str
    creation_time: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    status: str
    payload_digest: str
    status_code: int
    resource_details: ResourceDetails | None = None
    project_id: str | None = None

    def _format_job_data(self) -> dict[str, str]:

        formatted_data = {
            "label": self.job_label if self.job_label is not None else "-",
            "id": self.id,
            "creation_time": format_time(self.creation_time),
            "start_time": format_time(self.start_time),
            "end_time": format_time(self.end_time),
            "status": format_status(self.status, self.status_code),
        }

        if self.resource_details:
            formatted_data.update(self.resource_details._format_resources())
        else:
            formatted_data.update({"cpu": "-", "mem": "-", "backend": "-"})

        return formatted_data


class JobResponseList(BaseModel):
    job_list: list[JobResponse]

    def __rich__(self) -> Table:
        local_tz = datetime.now().astimezone().tzinfo or "UTC"
        table = Table(box=box.SIMPLE)
        column_mapping = {
            "label": "Label",
            "id": "ID",
            "creation_time": f"Submit Time\n({local_tz})",
            "start_time": f"Start Time\n({local_tz})",
            "end_time": f"End Time\n({local_tz})",
            "status": "Status\n",
            "cpu": "CPU\n(cores)",
            "mem": "Mem\n(MB)",
            "backend": "GPU\nbackend",
        }

        for column_key, column_name in column_mapping.items():
            if column_key in ["creation_time", "start_time", "end_time", "label"]:
                table.add_column(f"{column_name}", justify="center")
            else:
                table.add_column(f"{column_name}", justify="center", no_wrap=True)

        # sort jobs so scheduled jobs go at the top of the table
        sorted_jobs = sorted(
            self.job_list,
            key=lambda job: 0
            if job.status == "scheduled"
            else (1 if job.status == "running" else 2),
        )

        for job in sorted_jobs:
            formatted_data = job._format_job_data()
            # ensure ordering of keys in formatted_data matches column_mapping
            ordered_data = {key: formatted_data[key] for key in column_mapping.keys()}
            table.add_row(*ordered_data.values())

        return table


class CancelJobResponse(BaseModel):
    cancelled: bool


class DeleteJobResponse(BaseModel):
    job_id: str
    deleted: bool


class RemoteConfig(BaseModel):
    id: str
    name: str
    description: str
    default: bool


class SasUrlResponse(BaseModel):
    sas_url: str
    expiry_date: str


class Project(BaseModel):
    id: str
    name: str
    default: bool


class Api:

    _base_url: str
    _api_key: str | None

    def __init__(self, base_url: str, api_key: str | None) -> None:
        self._base_url = base_url
        self._api_key = api_key

    def _raise_for_status(self, response: requests.Response) -> None:
        http_error_msg: str | None = None
        text = response.text
        if 400 <= response.status_code < 500:
            http_error_msg = (
                f"{response.status_code} Client "
                f"Error: {response.reason} for url: "
                f"{response.url}. Message: {text}"
            )

        elif 500 <= response.status_code < 600:
            http_error_msg = (
                f"{response.status_code} Server "
                f"Error: {response.reason} for url: "
                f"{response.url}. Message: {text}"
            )

        if http_error_msg:
            raise ApiError(
                http_error_msg,
                status_code=response.status_code,
                reason=response.reason,
                url=response.url,
                body=text,
            )

    def _get_default_headers(self, token: str | None = None) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self._api_key:
            headers["x-functions-key"] = self._api_key
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def schedule_job(self, token: str, payload: dict[str, Any]) -> JobResponse:
        url: str = urllib.parse.urljoin(self._base_url, "api/jobs")
        headers: dict[str, str] = self._get_default_headers(token=token)
        headers["Content-Type"] = "application/json"

        r: Response = requests.post(url, headers=headers, data=json.dumps(payload))
        self._raise_for_status(response=r)
        return JobResponse.model_validate(r.json())

    def get_job_by_id(self, token: str, job_id: str) -> JobResponse:
        url: str = urllib.parse.urljoin(self._base_url, f"api/jobs/{job_id}")
        headers: dict[str, str] = self._get_default_headers(token=token)

        r: Response = requests.get(url, headers=headers)
        self._raise_for_status(response=r)
        return JobResponse.model_validate(r.json())

    def cancel_job(self, token: str, job_id: str) -> CancelJobResponse:
        url: str = urllib.parse.urljoin(self._base_url, f"api/jobs/{job_id}/cancel")
        headers: dict[str, str] = self._get_default_headers(token=token)

        r: Response = requests.post(url, headers=headers)
        self._raise_for_status(response=r)
        return CancelJobResponse.model_validate(r.json())

    def delete_job(self, token: str, job_id: str) -> DeleteJobResponse:
        url: str = urllib.parse.urljoin(self._base_url, f"api/jobs/{job_id}")
        headers: dict[str, str] = self._get_default_headers(token=token)

        r: Response = requests.delete(url, headers=headers)
        self._raise_for_status(response=r)
        return DeleteJobResponse.model_validate(r.json())

    def get_job_results(self, token: str, job_id: str) -> dict[str, Any]:
        url: str = urllib.parse.urljoin(self._base_url, f"api/jobs/{job_id}/results")
        headers: dict[str, str] = self._get_default_headers(token=token)

        r: Response = requests.get(url, headers=headers)
        self._raise_for_status(response=r)
        return r.json()

    def get_job_response_list(
        self, token: str, offset: int = 0, limit: int = 10
    ) -> JobResponseList:
        url: str = urllib.parse.urljoin(
            self._base_url, f"api/jobs?offset={offset}&limit={limit}"
        )
        headers: dict[str, str] = self._get_default_headers(token=token)
        r: Response = requests.get(url, headers=headers)
        self._raise_for_status(response=r)
        return JobResponseList(
            job_list=[JobResponse.model_validate(o) for o in r.json()]
        )

    def get_noise_models(self, token: str) -> list[NoiseModel]:
        url: str = urllib.parse.urljoin(self._base_url, "api/noise-models")
        headers: dict[str, str] = self._get_default_headers(token=token)

        r: Response = requests.get(url, headers=headers)
        self._raise_for_status(response=r)
        return [NoiseModel.model_validate(o) for o in r.json()]

    def get_token(
        self,
        access_token_id: str,
        access_token_secret: str,
    ) -> JwtResponse:
        url: str = urllib.parse.urljoin(self._base_url, "api/login")
        headers: dict[str, str] = self._get_default_headers()
        headers["Content-Type"] = "application/json"

        payload: dict[str, str] = {
            "access_token_id": access_token_id,
            "access_token_secret": access_token_secret,
        }
        r: Response = requests.post(url, headers=headers, data=json.dumps(payload))
        self._raise_for_status(response=r)
        return JwtResponse.model_validate(r.json())

    def get_remote_configs(self, token: str) -> list[RemoteConfig]:
        url: str = urllib.parse.urljoin(self._base_url, "api/remote-configs")
        headers: dict[str, str] = self._get_default_headers(token=token)

        r: Response = requests.get(url, headers=headers)
        self._raise_for_status(response=r)
        return [RemoteConfig.model_validate(o) for o in r.json()]

    def get_projects(self, token: str) -> list[Project]:
        url: str = urllib.parse.urljoin(self._base_url, "api/projects")
        headers: dict[str, str] = self._get_default_headers(token=token)

        r: Response = requests.get(url, headers=headers)
        self._raise_for_status(response=r)
        return [Project.model_validate(o) for o in r.json()]

    def get_job_data_sas_url(self, token: str, job_id: str) -> SasUrlResponse:
        url: str = urllib.parse.urljoin(self._base_url, f"api/jobs/{job_id}/jobdata")
        headers: dict[str, str] = self._get_default_headers(token=token)

        r: Response = requests.get(url, headers=headers)
        self._raise_for_status(response=r)
        return SasUrlResponse.model_validate(r.json())

    def get_notification_configuration(self, token: str) -> str:  # fix token type
        url: str = urllib.parse.urljoin(
            self._base_url, "api/notification_configuration"
        )
        headers: dict[str, str] = self._get_default_headers(token=token)

        r: Response = requests.get(url, headers=headers)
        self._raise_for_status(response=r)
        return r.json()

    def post_notification_configuration(
        self, token: str, notification_configuration: dict[str, str]
    ) -> dict[str, Any]:

        url: str = urllib.parse.urljoin(
            self._base_url, "api/notification_configuration"
        )
        headers: dict[str, str] = self._get_default_headers(token=token)
        payload: dict[str, str] = notification_configuration

        r: Response = requests.post(url, headers=headers, data=json.dumps(payload))
        self._raise_for_status(response=r)
        return r.json()
