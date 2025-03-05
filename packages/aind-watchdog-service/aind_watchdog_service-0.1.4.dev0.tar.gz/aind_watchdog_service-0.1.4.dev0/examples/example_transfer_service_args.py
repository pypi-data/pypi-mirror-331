from aind_data_transfer_models.core import (
    BasicUploadJobConfigs,
    ModalityConfigs,
)
from aind_metadata_mapper.models import (
    SessionSettings,
    JobSettings as GatherMetadataJobSettings,
)
from aind_metadata_mapper.mesoscope.models import JobSettings as MesoscopeSessionSettings
from pathlib import Path, PurePosixPath
from aind_watchdog_service.models import (
    ManifestConfig,
    make_standard_transfer_args,
)


# Create manifest (with transfer_service_args = None)
manifest = ManifestConfig(
    name="multiplane-ophys_726087_2024-06-21_16-16-26",
    subject_id="726087",
    acquisition_datetime="2024-06-18 10:34:32.749880",
    schedule_time="03:00:00",
    transfer_endpoint="http://aind-data-transfer-service-dev/api/v1/submit_jobs",
    platform="multiplane-ophys",
    mount="ophys",
    s3_bucket="private",
    project_name="Learning mFISH-V1omFISH",
    modalities={
        "behavior": [
            r"\\W10SV109650002\mvr\data\1374103167_Behavior_20240618T103420.mp4"
        ],
        "ophys": [r"D:\scanimage_ophys\data\1374103167\1374103167_averaged_depth.tiff"],
    },
    schemas=[
        "C:/ProgramData/aind/rig.json",
        r"D:\scanimage_ophys\data\1374103167\session.json",
        r"D:\scanimage_ophys\data\1374103167\data_description.json",
    ],
    processor_full_name="Chris P. Bacon",
    destination=r"//allen/aind/scratch/2p-working-group/data-uploads",
    capsule_id="private",
)


# Make an extra metadata config to pass to aind-data-transfer-service
metadata_configs = GatherMetadataJobSettings(
    directory_to_write_to="stage",
    session_settings=SessionSettings(
        job_settings=MesoscopeSessionSettings(
            behavior_source=r"//allen/aind/scratch/mesoscope/mesoscope_726087_2024-06"
            r"-21_16-16-26/behavior",
            session_start_time="2024-06-21 21:16:16",
            session_end_time="2024-06-22 03:00:00",
            subject_id="726087",
            experimenter_full_name=["Chris p. Bacon"],
            project="mesoscope",
        )
    ),
)

# Make a basic data_transfer_service post out of the data in the manifest
submit_request = make_standard_transfer_args(manifest)

# Add the new metadata_configs to the submit_request
submit_request.upload_jobs[0].metadata_configs = metadata_configs

# Add submit args back into manifest
manifest.transfer_service_args = submit_request


manifest.write_standard_file(".")
