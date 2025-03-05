"""The fermioniq.emulator_message module handles messages from the EmulatorJob.

The module contains the :py:meth:`EmulatorMessage` class, which represents a message
containing information about an EmulatorJob's events and status.
"""

from typing import Literal, Optional

from pydantic import BaseModel


class EmulatorMessage(BaseModel):
    """Message received from the emulator.

    Attributes
    ----------
    event_type
        Type of the event. Can be either "FINISHED" or "ERROR".
    job_status_code
        Status code of the job. 0 means success.
    job_id
        ID of the job this message belongs to.
    error_message
        Error message if job_status_code is not 0.
    """

    event_type: Literal["STARTED", "FINISHED"]
    job_status_code: int
    job_id: str
    error_message: Optional[str] = None
