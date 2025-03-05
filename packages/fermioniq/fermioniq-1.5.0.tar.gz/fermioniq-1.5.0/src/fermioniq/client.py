"""The client module provides an interface to use the Fermioniq services.

It allows you to schedule and monitor jobs, and to retrieve the
results of completed jobs.
"""


import asyncio
import os
import sys
from asyncio import AbstractEventLoop
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Literal, Optional

from pydantic import BaseModel, ConfigDict

from fermioniq.api import (
    Api,
    ApiError,
    CancelJobResponse,
    DeleteJobResponse,
    JobResponse,
    JobResponseList,
    NoiseModel,
    Project,
    RemoteConfig,
    SasUrlResponse,
)
from fermioniq.custom_logging.printing import Printer, StringMessage
from fermioniq.emulator_job import EmulatorJob, JobResult, jsonify_and_compress_inputs
from fermioniq.emulator_message import EmulatorMessage


class NoResultsErrorReason(Enum):
    JOB_FAILED = 1
    JOB_NOT_FINISHED = 2


class NoResultsError(RuntimeError):
    """Exception raised when results are not available for a job.

    Parameters
    ----------
    msg
        The error message.
    reason
        The reason for the error. See class :py:meth:`fermioniq.client.NoResultsErrorReason` for different reasons.
    """

    def __init__(
        self,
        msg: Any,
        reason: NoResultsErrorReason,
    ):
        super().__init__(msg)
        self.reason = reason


class ClientConfig(BaseModel):
    """Class for configuring the :py:meth:`fermioniq.client.Client` class.

    Attributes
    ----------
    access_token_id
        API Key. Can be overwritten with environment variable FERMIONIQ_ACCESS_TOKEN_ID.
    access_token_secret
        API Secret. Can be overwritten with environment variable FERMIONIQ_ACCESS_TOKEN_SECRET.
    polling_interval
        The interval in seconds between polling requests. Defaults to 1 second.
    verbosity_level
        Level of Client verbosity. The higher the number, the more emulator output will
        be sent to the client. This has an impact on runtime performance and costs.

    Examples
    --------
    >>> config = ClientConfig(polling_interval=2.0)  # Poll every 2 seconds
    >>> client = Client(config=config)
    """

    polling_interval: float = 1.0
    access_token_id: str | None = None
    access_token_secret: str | None = None
    verbosity_level: int = 0
    model_config = ConfigDict(arbitrary_types_allowed=True)


class Client:
    """
    This class provides an interface to interact with the Fermioniq API.

    It allows users to schedule, manage, and retrieve the results of :py:meth:`fermioniq.emulator_job.EmulatorJob` objects.
    Additionally, it provides polling functionality for subscribing to job events and receiving updates
    about job status changes. The class handles token management, ensuring that a valid token is always used
    when interacting with the API.

    Parameters
    ----------
    access_token_id
        API Key. Can be overwritten with environment variable FERMIONIQ_ACCESS_TOKEN_ID.
    access_token_secret
        API Secret. Can be overwritten with environment variable FERMIONIQ_ACCESS_TOKEN_SECRET.
    polling_interval
        The interval in seconds between polling requests. Defaults to 1 second.
    verbosity_level
        Level of Client verbosity. The higher the number, the more emulator output will
        be sent to the client. This has an impact on runtime performance and costs.

    Raises
    ------
    RuntimeError
        If access_token_id or access_token_secret are not provided and are not found in the environment variables.

    Examples
    --------
    >>> fermioniq = Client()

    >>> # Schedule a new job
    >>> job = EmulatorJob(circuit="some_circuit_definition")
    >>> job_response = fermioniq.schedule_async(job)

    >>> # Retrieve a specific job
    >>> job_response = fermioniq.job(job_id="some_job_id")

    >>> # Retrieve all jobs
    >>> jobs_list = fermioniq.jobs()

    >>> # Subscribe to job events
    >>> fermioniq.subscribe_to_events(job_id="some_job_id", on_msg_callback=my_callback)
    """

    _config: ClientConfig
    _token: str | None = None
    _token_exp: datetime | None = None
    _keep_polling: bool = False
    _api_base_url: str
    _api_key: str | None
    _loop: AbstractEventLoop
    _access_token_secret: str
    _access_token_id: str

    def __init__(
        self,
        access_token_id: Optional[str] = None,
        access_token_secret: Optional[str] = None,
        polling_interval: float = 1.0,
        verbosity_level: int = 0,
    ):
        self._config = ClientConfig(
            access_token_id=access_token_id,
            access_token_secret=access_token_secret,
            polling_interval=polling_interval,
            verbosity_level=verbosity_level,
        )

        if self._config.verbosity_level < 0:
            self._config.verbosity_level = 0
        elif self._config.verbosity_level > 2:
            self._config.verbosity_level = 2

        access_token_id = os.getenv(
            "FERMIONIQ_ACCESS_TOKEN_ID", self._config.access_token_id
        )
        if not access_token_id:
            raise RuntimeError(
                (
                    "Missing access token id. Please provide it by setting the "
                    "environment variable FERMIONIQ_ACCESS_TOKEN_ID, or specify it via "
                    "the argument `access_token_id` when instantiating the Client"
                )
            )

        access_token_secret = os.getenv(
            "FERMIONIQ_ACCESS_TOKEN_SECRET", self._config.access_token_secret
        )
        if not access_token_secret:
            raise RuntimeError(
                (
                    "Missing access token secret. Please provide it by setting the "
                    "environment variable FERMIONIQ_ACCESS_TOKEN_SECRET, or specify it via "
                    "the argument `access_token_secret` when instantiating the Client"
                )
            )

        self._access_token_secret = access_token_secret
        self._access_token_id = access_token_id

        self._api_base_url = os.getenv(
            "FERMIONIQ_API_BASE_URL",
            "https://fermioniq-api-prod.azurewebsites.net",
        )
        self._api_key = os.getenv(
            "FERMIONIQ_API_KEY",
            "ZBwmQS4eR92BDnvz0B0QuSNBdLAydWKOlldLEGZ5sDxSAzFuvQB89A==",
        )

        self._api = Api(self._api_base_url, api_key=self._api_key)
        self._loop = asyncio.get_event_loop()

    def noise_models(self) -> list[NoiseModel]:
        """Retrieve all available noise models.

        Returns
        -------
        noise_models
            A list of NoiseModel objects.
        """
        self._ensure_valid_token()
        if not self._token:
            raise RuntimeError("Error getting token")

        return self._api.get_noise_models(token=self._token)

    def get_results(self, job_id: str) -> JobResult:
        """Retrieve the job results if available.

        Parameters
        ----------
        job_id
            The ID of the job to retrieve the results for.

        Returns
        -------
        job_result
            A JobResult object containing the results of the job.

        Raises
        ------
        NoResultsError
            When results are not available
        ApiError
            When job can't be found or authorization fails
        """
        self._ensure_valid_token()
        if not self._token:
            raise RuntimeError("Error getting token")

        try:
            results = self._api.get_job_results(self._token, job_id)
            job_data = self.job(job_id)
            return JobResult(
                status_code=0,
                label=job_data.job_label,
                job_outputs=results["emulator_output"],
                job_metadata=results["metadata"],
            )
        except ApiError:
            # dont do anything. we handle it below
            pass

        # ApiError indicates that we don't have the results available.
        # It could be because the job is still running or it has finished
        # with error. Retrieve job and do a check on status
        job = self.job(job_id)
        if job.status == "finished":
            raise NoResultsError(
                (
                    f"Error retrieving results for job: {job_id}. The "
                    "job finished with error."
                ),
                reason=NoResultsErrorReason.JOB_FAILED,
            )
        else:
            raise NoResultsError(
                (
                    f"Error retrieving results for job: {job_id}. The "
                    f"status is '{job.status}'. Try again later."
                ),
                reason=NoResultsErrorReason.JOB_NOT_FINISHED,
            )

    def job(self, job_id: str) -> JobResponse:
        """Retrieve the job with the specified job_id.

        Parameters
        ----------
        job_id
            The ID of the job to retrieve.

        Returns
        -------
        job
            A JobResponse object containing the job details.
        """
        self._ensure_valid_token()
        if not self._token:
            raise RuntimeError("Error getting token")

        return self._api.get_job_by_id(self._token, job_id)

    def get_status(self, job_id: str) -> str:
        """Retrieve the status of the job with id job_id.

        Parameters
        ----------
        job_id
            The ID of the job to check the status of.

        Returns
        -------
        status
            Status of the job (as a string).
        """
        job = self.job(job_id)
        return job.status

    def get_projects(self) -> list[Project]:
        """Retrieve all projects.

        Returns
        -------
        projects
            A list of Projects.
        """
        self._ensure_valid_token()
        if not self._token:
            raise RuntimeError("Error getting token")
        return self._api.get_projects(self._token)

    def remote_configs(self) -> list[RemoteConfig]:
        """Retrieve all remote configurations.

        Returns
        -------
        remote_configs
            A list of RemoteConfig objects that are available to use.
        """
        self._ensure_valid_token()
        if not self._token:
            raise RuntimeError("Error getting token")
        return self._api.get_remote_configs(self._token)

    def jobs(self, offset: int = 0, limit: int = 10) -> JobResponseList:
        """Retrieve all jobs.

        Parameters
        ----------
        offset
            The offset to start retrieving jobs from. For example, if offset is 3,
            the first 3 jobs will be skipped.
        limit
            The maximum number of jobs to retrieve.

        Returns
        -------
        jobs
            A JobResponseList object containing the details of all jobs.
        """
        self._ensure_valid_token()
        if not self._token:
            raise RuntimeError("Error getting token")
        return self._api.get_job_response_list(self._token, offset=offset, limit=limit)

    def get_job_data_download_url(self, job_id: str) -> SasUrlResponse:
        """Returns a download url for retrieving the job data package.

        The link is valid for 1 hour, then it must be retrieved again.

        Parameters
        ----------
        job_id
            The ID of the job to retrieve the download link for.

        Returns
        -------
        download_url
            A SasUrlResponse object containing the download link.
        """
        self._ensure_valid_token()
        if not self._token:
            raise RuntimeError("Error getting token")

        return self._api.get_job_data_sas_url(self._token, job_id)

    def delete(self, job_id: str) -> DeleteJobResponse:
        """Deletes job given by id.

        Parameters
        ----------
        job_id
            The ID of the job to delete.

        Returns
        -------
        response
            A DeleteJobResponse object.
        """
        self._ensure_valid_token()
        if not self._token:
            raise RuntimeError("Error getting token")

        return self._api.delete_job(self._token, job_id)

    def cancel(self, job_id: str) -> CancelJobResponse:
        """Cancels a job.

        Parameters
        ----------
        job_id
            The ID of the job to cancel.

        Returns
        -------
        response
            A CancelJobResponse object.
        """
        self._ensure_valid_token()
        if not self._token:
            raise RuntimeError("Error getting token")

        return self._api.cancel_job(self._token, job_id=job_id)

    def schedule_and_wait(
        self,
        job: EmulatorJob,
        logger: Callable[[str], None] | None = None,
        cancel_on_interrupt: bool = True,
    ) -> JobResult:
        """Schedule a new job and wait for it to finish.

        Parameters
        ----------
        job
            The EmulatorJob to be scheduled.
        logger
            An optional callback function for logging status updates.
        cancel_on_interrupt
            If True, the job will be cancelled on Keyboard interrupt signal.

        Returns
        -------
        job_result
            A JobResult object containing the results of the job.

        Raises
        ------
        RuntimeError
            If the job fails or encounters an error during execution.
        """
        if logger is None:
            logger = Printer().pprint

        logger(str(StringMessage("Submitting job.")))
        new_job: JobResponse = self.schedule_async(job)
        logger(str(StringMessage(f"Job scheduled. Id: '{new_job.id}'")))

        def status_callback(message: EmulatorMessage) -> None:
            if message.event_type == "STARTED":
                logger(str(StringMessage(f"Job started. Id: '{new_job.id}'")))
            if message.event_type == "FINISHED":
                logger(str(StringMessage(f"Job finished. Id: '{new_job.id}'")))

        self.subscribe_to_events(
            job_id=new_job.id,
            on_msg_callback=status_callback,
            cancel_on_interrupt=cancel_on_interrupt,
        )

        logger(str(StringMessage("Retrieving results")))
        return self.get_results(new_job.id)

    def _get_project_id(self, job: EmulatorJob) -> str | None:
        projects = self.get_projects()

        available_projects = [project.name for project in projects]
        if job.project:
            project = [project for project in projects if project.name == job.project]
            if not project:
                raise RuntimeError(
                    (
                        f"No project found with name {job.project}. "
                        f"Use one of {available_projects}."
                    )
                )
            return project[0].id

        default_project = [project for project in projects if project.default]
        return default_project[0].id if default_project else None

    def _get_remote_config_id(self, job: EmulatorJob) -> str:
        remote_configs = self.remote_configs()

        if job.remote_config:
            remote_config = [
                rc for rc in remote_configs if rc.name == job.remote_config
            ]
            if not remote_config:
                available_configs = [rc.name for rc in remote_configs]
                raise RuntimeError(
                    (
                        f"Remote config with name {job.remote_config} "
                        f"does not exist. Use one of: {available_configs}"
                    )
                )

            return remote_config[0].id

        default_config = [rc for rc in remote_configs if rc.default]
        if not default_config:
            available_configs = [rc.name for rc in remote_configs]
            raise RuntimeError(
                (
                    f"No config provided and no default config found. Use "
                    f"one of {available_configs}."
                )
            )
        return default_config[0].id

    def schedule_async(self, job: EmulatorJob) -> JobResponse:
        """Schedule a new job asynchronously.

        Parameters
        ----------
        job
            The EmulatorJob to be scheduled.

        Returns
        -------
        job_response
            A JobResponse object containing the details of the scheduled job.
        """

        self._ensure_valid_token()
        if not self._token:
            raise RuntimeError("Error getting token")

        if job.remote_config is None or isinstance(job.remote_config, str):
            remote_config: str | dict[str, Any] = self._get_remote_config_id(job)

        # Internal use: remote config can be a dictionary. If not internal: server will give an error.
        elif isinstance(job.remote_config, dict):
            remote_config = job.remote_config

        project_id = self._get_project_id(job)
        notification_settings = self._get_notification_settings(job)

        json_circuits, json_configs, json_noise_models = jsonify_and_compress_inputs(
            job
        )

        payload: dict[str, Any] = {
            "circuit": json_circuits,
            "config": json_configs,
            "noise_model": json_noise_models,
            "verbosity_level": self._config.verbosity_level,
            "remote_config": remote_config,
            "project_id": project_id,
            "notification_settings": notification_settings,
            "label": job.label,
        }

        remote_job = self._api.schedule_job(self._token, payload)
        job._job_id = remote_job.id

        return remote_job

    def subscribe_to_events(
        self,
        job_id: str,
        on_msg_callback: Callable[[EmulatorMessage], None] | None = None,
        cancel_on_interrupt: bool = False,
    ) -> None | asyncio.Task[None]:
        """Subscribe to job status changes and execute a callback function when status changes.

        Parameters
        ----------
        job_id
            The ID of the job to subscribe to.
        on_msg_callback
            A callback function to be executed when job status changes.
        cancel_on_interrupt
            If True, and return_as_task is False, the job will be cancelled on
            Keyboard interrupt signal.

        Returns
        -------
        task
            None if return_as_task is False, otherwise an asyncio.Task object.
        """
        # First check if the job has already finished
        if self.job(job_id).status == "finished":
            return None

        def on_message(msg: EmulatorMessage) -> None:
            if on_msg_callback:
                on_msg_callback(msg)
            if msg.event_type == "FINISHED":
                self._keep_polling = False

        try:
            # block until _polling_loop is closed
            self._loop.run_until_complete(
                self._polling_loop(
                    job_id=job_id,
                    on_message_callback=on_message,
                )
            )
            return None
        except KeyboardInterrupt:
            self._keep_polling = False
            if cancel_on_interrupt:
                self.cancel(job_id=job_id)
            raise

    def configure_notifications(
        self, slack_id: str | None = None, email_address: str | None = None
    ) -> None:
        """Configure email address and/or Slack ID.

        This stores your details so they can be used everytime you initialize the client with your tokens.
        When calling this method, test messages will be sent using the specified details and return errors if they occur.
        This is useful for identifying any issues with notifications if you are not receiving them.

        Parameters
        ----------
        slack_id
            Your Slack user ID. See https://docs.fermioniq.com/UserGuide/Setup/notifications.html for more information about how to find this ID.
        email_address
            Your email_address.
        """

        self._ensure_valid_token()
        if not self._token:
            raise RuntimeError("Error getting token")
        # lets user configure slack channel ID or email (store in azure). Overwrites previously configured settings.

        notification_configuration = {}
        if slack_id:
            notification_configuration.update({"slack_id": slack_id})
        if email_address:
            notification_configuration.update({"email_address": email_address})
        if slack_id is None and email_address is None:
            raise ValueError(
                "If you want to set up the notification service, please provide a Slack user ID and/or an email address. "
                "For more information on configuring the notification service, see the Fermioniq Documentation (link) "
            )

        print("Sending test messages...")
        response = self._api.post_notification_configuration(
            self._token, notification_configuration
        )

        for mode in ["slack", "email"]:
            if response.get(f"{mode}_msg"):
                mode_msg = response[f"{mode}_msg"]
                if mode_msg["status_code"] == 200:
                    print(
                        f"{mode.capitalize()} configuration successful! Please check that you've received the test message."
                    )
                else:
                    print(
                        f'Error {mode_msg["status_code"]}: '
                        f'{mode_msg["message"]}. '
                        f'{mode_msg["error_details"]}'
                    )

    def _get_notification_settings(self, job: EmulatorJob) -> dict | None:

        self._ensure_valid_token()
        if not self._token:
            raise RuntimeError("Error getting token")

        if not job.notification_mode:
            return None

        elif job.notification_mode in ["slack", "email"]:
            env_var = (
                "SLACK_ID" if job.notification_mode == "slack" else "EMAIL_ADDRESS"
            )

            notification_ID = os.getenv(f"{env_var}")
            if not notification_ID:
                notification_config = self._api.get_notification_configuration(
                    self._token
                )

                if not notification_config:
                    notification_ID = None

                else:
                    notification_ID = notification_config.get(
                        f"{env_var.lower()}", None
                    )

            if not notification_ID:
                raise RuntimeError(
                    (
                        f"Missing variable {env_var}. Please provide via environment variable "
                        "or configure notification service via the client.configure_notification_service() method."
                    )
                )

            # Get local timezone information
            now = datetime.now().astimezone()
            timezone_name, utc_offset = None, None

            if now.tzinfo is not None:  # make mypy happy
                timezone_name = str(now.tzinfo)
                utc_offset_hours = now.astimezone().utcoffset()

                if utc_offset_hours is not None:
                    utc_offset = utc_offset_hours.total_seconds()

            local_tz = {"timezone": timezone_name, "utc_offset": utc_offset}

            notification_settings: dict[str, Any] = {
                "mode": job.notification_mode,
                "id": notification_ID,
                "timezone_info": local_tz,
            }
            return notification_settings

        else:
            raise ValueError(
                f"Notification should be either 'slack', 'email' or None, found: {job.notification_mode}"
            )

    def _ensure_valid_token(self) -> None:
        """Ensure the access token is valid.

        If the token is invalid or expired, it will try to refresh it.
        """
        if self._token is None or self._token_expired():
            token_response = self._api.get_token(
                self._access_token_id, self._access_token_secret
            )
            self._token_exp = token_response.expiration_date
            self._token = token_response.jwt_token

    def _token_expired(self) -> bool:
        """Check if the access token is expired.

        Returns
        -------
        expired
            True if the token is expired, False otherwise.
        """
        if self._token is None or self._token_exp is None:
            return True
        expired_offset = timedelta(days=0, seconds=1)
        return self._token_exp - datetime.now(tz=timezone.utc) < expired_offset

    async def _polling_loop(
        self,
        job_id: str,
        on_message_callback: Callable[[EmulatorMessage], None],
    ):
        """Asynchronous loop for handling polling messages.

        Calls the on_message_callback when job status changes or errors occur.

        Parameters
        ----------
        job_id
            The job_id to subscribe to.
        on_message_callback
            A callback function to be executed when job status changes.
        """
        self._keep_polling = True

        last_status = None
        while self._keep_polling:
            try:
                job = self.job(job_id=job_id)
                current_status = job.status

                if last_status == "scheduled" and current_status == "running":
                    msg = EmulatorMessage(
                        event_type="STARTED",
                        job_status_code=job.status_code,
                        job_id=job.id,
                    )
                    on_message_callback(msg)

                # Status changed or job finished
                elif current_status == "finished":
                    # Job completed - check if it was successful
                    msg = EmulatorMessage(
                        event_type="FINISHED",
                        job_status_code=job.status_code,
                        job_id=job.id,
                    )

                    on_message_callback(msg)
                    self._keep_polling = False

                last_status = current_status
                if self._keep_polling:
                    await asyncio.sleep(self._config.polling_interval)

            except Exception as err:
                # Handle any API errors or other exceptions
                print(f"Error polling job {job_id}: {err}", file=sys.stderr)
                self._keep_polling = False

    def unsubscribe(self):
        """Stop polling for job updates."""
        self._keep_polling = False
