"""Job configs for VAST staging or executing a custom script"""

from datetime import datetime, time
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Literal, Optional
import os
import yaml
import json

from aind_data_schema_models import modalities, platforms
from aind_data_schema_models.data_name_patterns import build_data_name
from aind_data_transfer_models.core import (
    BucketType,
    SubmitJobRequest,
    ModalityConfigs,
    BasicUploadJobConfigs,
)
from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    SerializeAsAny,
    field_serializer,
    field_validator,
    model_validator,
    computed_field,
    PlainSerializer,
)
from typing_extensions import Annotated, Self

# This is a really bad idea, but until we can figure out a better solution
# from aind-data-schema we will settle for this.
# A relevant issue has been opened in the aind-data-schemas repo:
# https://github.com/AllenNeuralDynamics/aind-data-schema/issues/960

Platform = Literal[tuple(set(platforms.Platform.abbreviation_map.keys()))]
Modality = Annotated[
    Literal[tuple(set(modalities.Modality.abbreviation_map.keys()))],
    BeforeValidator(lambda x: "pophys" if x == "ophys" else x),
]


class ManifestConfig(BaseModel):
    """Job configs for data transfer to VAST"""

    model_config = ConfigDict(extra="forbid")
    name: Optional[str] = Field(
        None,
        description="If not provided, gets generated to match CO asset",
        title="Manifest name",
    )
    processor_full_name: str = Field(
        ..., description="User who processed the data", title="Processor name"
    )
    subject_id: int = Field(..., description="Subject ID", title="Subject ID")
    acquisition_datetime: datetime = Field(
        description="Acquisition datetime",
        title="Acquisition datetime",
    )
    schedule_time: Optional[time] = Field(
        default=None,
        description="Transfer time to schedule copy and upload. If None defaults to trigger the transfer immediately",  # noqa
        title="APScheduler transfer time",
    )
    force_cloud_sync: bool = Field(
        default=False,
        description="Overwrite data in AWS",
        title="Force cloud sync",
    )
    transfer_endpoint: Optional[str] = Field(
        default="http://aind-data-transfer-service/api/v1/submit_jobs",
        description="Transfer endpoint for data transfer",
        title="Transfer endpoint",
    )
    platform: Platform = Field(description="Platform type", title="Platform type")
    capsule_id: Optional[str] = Field(
        default=None, description="Capsule ID of pipeline to run", title="Capsule"
    )
    mount: Optional[str] = Field(
        default=None, description="Mount point for pipeline run", title="Mount point"
    )
    s3_bucket: BucketType = Field(
        default=BucketType.PRIVATE, description="s3 endpoint", title="S3 endpoint"
    )
    project_name: str = Field(..., description="Project name", title="Project name")
    destination: str = Field(
        ...,
        description="Remote directory on VAST where to copy the data to.",
        title="Destination directory",
        examples=[r"\\allen\aind\scratch\test"],
    )
    modalities: Dict[Modality, List[str]] = Field(
        default={},
        description="list of ModalityFile objects containing modality names and associated files or directories",  # noqa
        title="modality files",
    )
    schemas: List[str] = Field(
        default=[],
        description="Where schema files to be uploaded are saved",
        title="Schema directory",
    )
    script: Dict[str, List[str]] = Field(
        default={},
        description="Set of commands to run in subprocess. - DEPRECATED - NONFUNCTIONAL",
        title="Commands",
    )
    transfer_service_args: Optional[SerializeAsAny[SubmitJobRequest]] = Field(
        default=None,
        description="Arguments to pass to data-transfer-service",
        title="Transfer service args",
    )

    @property
    def data_transfer_service_modality_configs(self):
        modality_configs = []
        for modality in self.modalities.keys():
            m = ModalityConfigs(
                source=PurePosixPath(self.destination) / self.name / modality,
                modality=modality,
            )
            modality_configs.append(m)
        return modality_configs

    @model_validator(mode="after")
    def set_name(self) -> Self:
        """Construct name"""
        if self.name is None:
            self.name = build_data_name(
                f"{self.platform}_{self.subject_id}",
                self.acquisition_datetime,
            )
        return self

    @field_validator("destination", mode="after")
    @classmethod
    def validate_destination_path(cls, value: str) -> str:
        """Converts path string to posix"""
        return cls._path_to_posix(value)

    @field_validator("schemas", mode="after")
    @classmethod
    def validate_schema_paths(cls, value: List[str]) -> List[str]:
        """Converts path strings to posix"""
        return [cls._path_to_posix(path) for path in value]

    @field_validator("modalities", mode="after")
    @classmethod
    def validate_modality_paths(cls, value: Dict[Any, List[str]]) -> Dict[Any, List[str]]:
        """Converts modality path strings to posix and check for existence"""

        output: dict[str, list[str]] = {}
        for modality, paths in value.items():
            output[modality] = []
            for path in paths:
                output[modality].append(cls._path_to_posix(path))

        return output

    @staticmethod
    def _path_to_posix(path: str) -> str:
        """Converts path string to posix"""
        return str(Path(path).as_posix())

    @field_serializer("s3_bucket")
    def serialize_enum(self, s3_bucket: BucketType):
        return s3_bucket.value

    @field_validator("schedule_time", mode="before")
    @classmethod
    def normalized_scheduled_time(cls, value) -> Optional[time]:
        """Normalize scheduled time"""
        if value is None:
            return value
        else:
            if isinstance(value, datetime):
                return value.time()
            elif isinstance(value, str):
                return datetime.strptime(value, "%H:%M:%S").time()
            elif isinstance(value, time):
                return value
            else:
                raise ValueError("Invalid time format")

    @model_validator(mode="after")
    def validate_capsule(self) -> Self:
        """Validate capsule and mount"""
        if (self.capsule_id is None) ^ (self.mount is None):
            raise ValueError(
                "Both capsule and mount must be provided, or must both be None"
            )
        return self

    @field_validator("modalities", mode="before")
    @classmethod
    def normalize_modalities(cls, value) -> Dict[Modality, List[str]]:
        """Normalize modalities"""
        if isinstance(value, dict):
            _ret: Dict[str, Any] = {}
            for modality, v in value.items():
                if isinstance(modality, getattr(modalities.Modality, "ALL")):
                    key = getattr(modality, "abbreviation", None)
                    if key is None:
                        _ret[modality] = v
                    else:
                        _ret[key] = v
                else:
                    _ret[modality] = v
            return _ret
        else:
            return value

    @field_validator("platform", mode="before")
    @classmethod
    def normalize_platform(cls, value) -> Platform:
        """Normalize modalities"""
        if isinstance(value, getattr(platforms.Platform, "ALL")):
            ret = getattr(value, "abbreviation", None)
            return ret if ret else value
        else:
            return value

    def write_standard_file(self, manifest_directory: Path) -> Path:
        path = Path(manifest_directory) / f"manifest_{self.name}.yml"
        json_str = self.model_dump_json()
        data = json.loads(json_str)
        with open(path, "w") as file:
            yaml.safe_dump(
                data,
                file,
                default_flow_style=False,
                sort_keys=False,
                width=float("inf"),
                allow_unicode=True,
            )
        return path


class IngestedManifest(ManifestConfig):

    name: str

    transfer_service_args: Optional[dict] = Field(
        default=None,
        description="Dump of aind_data_transfer_models.SubmitJobRequestUpload to pass to data-transfer-service",
        title="Transfer service args",
    )

    ## TODO: Decouple watchdog service from data-schema

    # platform: str = Field(description="Platform type", title="Platform type")

    # modalities: Dict[str, List[str]] = Field(
    #     default={},
    #     description="list of ModalityFile objects containing modality names and associated files or directories",  # noqa
    #     title="modality files",
    # )

    @staticmethod
    def _get_tree_size(path: str) -> int:
        """Return total size of files in given path and subdirs."""
        total = 0
        for entry in os.scandir(path):
            if entry.is_dir(follow_symlinks=False):
                total += IngestedManifest._get_tree_size(entry.path)
            else:
                total += entry.stat(follow_symlinks=False).st_size
        return total

    @property
    def total_data_size(self) -> float:
        """Calculate the total size of the data in megabytes."""
        total_size = 0
        for files in self.modalities.values():
            for file in files:
                try:
                    total_size += self._get_tree_size(file)
                except:
                    return None
        total_size_mb = total_size / 1024**2  # convert to MB
        return round(total_size_mb, 2)

    @property
    def log_tags(self) -> dict:
        return {
            "name": self.name,
            "subject_id": self.subject_id,
            "project_name": self.project_name,
            "modalities": list(self.modalities.keys()),
            "data_size_mb": self.total_data_size,
        }


def make_standard_transfer_args(manifest: IngestedManifest) -> SubmitJobRequest:
    """Helper method to create a SubmitJobRequest based on a watchdog manifest"""

    upload_job_configs = BasicUploadJobConfigs(
        s3_bucket=manifest.s3_bucket,
        platform=manifest.platform,
        subject_id=str(manifest.subject_id),
        acq_datetime=manifest.acquisition_datetime.strftime("%Y-%m-%d %H:%M:%S"),
        modalities=manifest.data_transfer_service_modality_configs,
        metadata_dir=PurePosixPath(manifest.destination) / manifest.name,
        process_capsule_id=manifest.capsule_id,
        project_name=manifest.project_name,
        input_data_mount=manifest.mount,
        force_cloud_sync=manifest.force_cloud_sync,
    )
    submit_request = SubmitJobRequest(upload_jobs=[upload_job_configs])

    return submit_request


def check_for_missing_data(manifest: ManifestConfig) -> tuple[list[str], list[str]]:
    """Check for missing files in manifest"""
    missing_files = []
    for modality, paths in manifest.modalities.items():
        for path in paths:
            if not Path(path).exists():
                missing_files.append(path)

    missing_schema = [path for path in manifest.schemas if not Path(path).exists()]
    return missing_files, missing_schema
