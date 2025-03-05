""" Configuration for watchdog service"""

from typing import Optional, Union, Literal

from pydantic import BaseModel, Field


class WatchConfig(BaseModel, extra="ignore"):
    """Configuration for rig"""

    flag_dir: str = Field(
        ..., description="Directory for watchdog to poll", title="Poll directory"
    )
    manifest_complete: str = Field(
        ...,
        description="Manifest directory for triggered data",
        title="Manifest complete directory",
    )
    misfire_grace_time_s: Union[int, None] = Field(
        default=3 * 3600,
        description="If the job scheduler is busy, wait this long before skipping a job."
        + " If None, allow the job to run no matter how late it is",
        title="Scheduler grace time",
    )

    robocopy_args: list[str] = [
        "/e",
        "/z",
        "/j",
        "/r:5",
        "/np",
        "/log+:C:\\ProgramData\\AIBS_MPE\\aind_watchdog_service\\logs\\robocopy.log",
    ]

    windows_copy_utility: Literal["shutil", "robocopy"] = "robocopy"
