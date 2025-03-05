""" Module to run jobs on file modification"""

import json
import logging
import os
import platform
import subprocess
from pathlib import Path, PurePosixPath
import shutil
from typing import Optional
import time
import re

import requests
from aind_data_transfer_models.core import (
    BasicUploadJobConfigs,
    ModalityConfigs,
    SubmitJobRequest,
)

from aind_watchdog_service.alert_bot import AlertBot
from aind_watchdog_service.models.manifest_config import (
    IngestedManifest,
    make_standard_transfer_args,
    check_for_missing_data,
)
from aind_watchdog_service.models.watch_config import WatchConfig

if platform.system() == "Windows":
    PLATFORM = "windows"
else:
    PLATFORM = "linux"


class RunJob:
    """Run job class to stage files on VAST or run a custom script
    and trigger aind-data-transfer-service
    """

    def __init__(
        self,
        src_path: str,
        config: IngestedManifest,
        watch_config: WatchConfig,
    ):
        """initialize RunJob class"""
        self.src_path = src_path
        self.config = config
        self.watch_config = watch_config

    def copy_to_vast(self) -> bool:
        """Determine platform and copy files to VAST

        Returns
        -------
        bool
            status of the copy operation
        """
        parent_directory = self.config.name
        destination = self.config.destination
        modalities = self.config.modalities
        for modality in modalities.keys():
            destination_directory = Path(destination) / parent_directory / modality
            if not destination_directory.is_dir():
                destination_directory.mkdir(parents=True)
            for file in modalities[modality]:
                if PLATFORM == "windows":
                    transfer = self.execute_windows_command(file, destination_directory)
                else:
                    transfer = self.execute_linux_command(file, destination_directory)
                if not transfer:
                    logging.error("Error copying files %s", file)
                    return False
        for schema in self.config.schemas:
            destination_directory = os.path.join(destination, parent_directory)
            if PLATFORM == "windows":
                transfer = self.execute_windows_command(schema, destination_directory)
            else:
                transfer = self.execute_linux_command(schema, destination_directory)
            if not transfer:
                logging.error("Error copying schema %s", schema)
                return False
        return True

    def run_subprocess(self, cmd: list) -> subprocess.CompletedProcess:
        """subprocess run command

        Parameters
        ----------
        cmd : list
            command to execute

        Returns
        -------
        subprocess.CompletedProcess
            subprocess completed process
        """
        logging.debug("Executing command: %s", cmd)
        subproc = subprocess.run(
            cmd, check=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE
        )
        return subproc

    def get_robocopy_log_path(self) -> Optional[str]:
        """Get the robocopy log file path from watch_config.robocopy_args.

        Returns
        -------
        Optional[str]
            Path to the robocopy log file if specified, otherwise None.
        """
        args = self.watch_config.robocopy_args
        log_pattern = re.compile(r"/log\+?:(.+)")
        for arg in args:
            match = log_pattern.match(arg)
            if match:
                return match.group(1)
        return None

    def parse_robocopy_log(self, log_file_path: str) -> list:
        """Parse the robocopy log file to fetch error details for the latest run.

        Parameters
        ----------
        log_file_path : str
            Path to the robocopy log file.

        Returns
        -------
        list
            A list containing error details.
        """
        error_details = []
        error_pattern = re.compile(r"(ERROR)\s+\d+\s+\(0x[0-9A-F]+\)\s+(.+)\s+(.+)")
        start_pattern = re.compile(r"^ *Started : ")

        with open(log_file_path, "r") as log_file:
            lines = log_file.readlines()

        # Read the log file in reverse to find the latest run
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i]
            if start_pattern.match(line):
                break
            match = error_pattern.search(line)
            if match:
                error_message = " ".join(match.groups())
                additional_message = (
                    lines[i + 1].strip()
                    if i + 1 < len(lines)
                    else "No additional error message"
                )
                error_message = f"{error_message} - {additional_message}"
                # Avoid duplicate error messages for the same file when retrying
                if error_message not in error_details:
                    error_details.append(error_message)

        return error_details

    def execute_windows_command(self, src: str, dest: str) -> bool:
        """copy files using windows robocopy command or shutil

        Parameters
        ----------
        src : str
            source file or directory
        dest : str
            destination directory

        Returns
        -------
        bool
            True if copy was successful, False otherwise
        """
        if not Path(src).exists():
            logging.error(
                {
                    "Error": "Source file does not exist",
                    "File": src,
                    "Destination": dest,
                }
                | self.config.log_tags
            )
            return False
        if self.watch_config.windows_copy_utility == "shutil":
            return self.execute_shutil(src, dest)
        else:
            if Path(src).is_dir():
                run = self.run_subprocess(
                    ["robocopy", src, dest] + self.watch_config.robocopy_args,
                )
            else:
                # Robocopy used over xcopy for better performance
                # /j: unbuffered I/O (to speed up copy)
                # /e: copy subdirectories (includes empty subdirs), /r:5: retry 5 times
                run = self.run_subprocess(
                    [
                        "robocopy",
                        str(Path(src).parent),
                        dest,
                        Path(src).name,
                    ]
                    + self.watch_config.robocopy_args,
                )
            # Robocopy return code documenttion:
            # https://learn.microsoft.com/en-us/troubleshoot/windows-server/backup-and-storage/return-codes-used-robocopy-utility # noqa
            if run.returncode > 7:
                error_details = {
                    "Error": "Could not copy file",
                    "File": src,
                    "Destination": dest,
                    "Robocopy Return Code": run.returncode,
                }

                log_file_path = self.get_robocopy_log_path()
                if log_file_path:
                    robocopy_error_details = self.parse_robocopy_log(log_file_path)
                    logging.error(
                        error_details
                        | {"Robocopy Error Details": robocopy_error_details}
                        | self.config.log_tags
                    )
                else:
                    logging.error(error_details | self.config.log_tags)
                return False
            return True

    def execute_shutil(self, src: str, dest: str) -> bool:
        """copy files using shutil

        Parameters
        ----------
        src : str
            source file or directory
        dest : str
            destination directory

        Returns
        -------
        bool
            True if copy was successful, False otherwise
        """

        try:
            if Path(src).is_dir():
                dest = Path(dest) / Path(src).name
                shutil.copytree(src, dest, dirs_exist_ok=True)
            else:
                shutil.copy(src, dest)
            return True
        except:
            logging.exception(
                {
                    "Error": "Could not copy file",
                    "File": src,
                    "Destination": dest,
                }
                | self.config.log_tags,
                extra={"emit_exc": True},
            )
            return False

    def execute_linux_command(self, src: str, dest: str) -> bool:
        """copy files using linux cp command

        Parameters
        ----------
        src : str
            source file or directory
        dest : str
            destination directory

        Returns
        -------
        bool
            True if copy was successful, False otherwise
        """
        # Rsync used over cp for better performance
        # -r: recursive, -t: preserve modification times
        if not Path(src).exists():
            logging.error(
                {
                    "Error": "Source file does not exist",
                    "File": src,
                    "Destination": dest,
                }
                | self.config.log_tags
            )
            return False
        if Path(src).is_dir():
            run = self.run_subprocess(["rsync", "-r", "-t", src, dest])
        else:
            run = self.run_subprocess(["rsync", "-t", src, dest])
        if run.returncode != 0:
            logging.error(
                {
                    "Error": "Could not copy file",
                    "File": src,
                    "Destination": dest,
                    "Rsync Return Code": run.returncode,
                }
                | self.config.log_tags
            )
            return False
        return True

    def trigger_transfer_service(self) -> requests.Response:
        """Triggers aind-data-transfer-service"""
        if self.config.transfer_service_args is None:
            submit_request = make_standard_transfer_args(self.config)
            post_request_content = json.loads(
                submit_request.model_dump_json(round_trip=True)
            )
        else:
            post_request_content = self.config.transfer_service_args

        logging.info("Submitting job to aind-data-transfer-service")
        submit_job_response = requests.post(
            url=self.config.transfer_endpoint, json=post_request_content, timeout=5
        )
        return submit_job_response

    def move_manifest_to_archive(self) -> None:
        """Move manifest file to archive"""
        archive = self.watch_config.manifest_complete
        if PLATFORM == "windows":
            copy_file = self.execute_windows_command(self.src_path, archive)
            if not copy_file:
                logging.error("Error copying manifest file %s", self.src_path)
                return
            os.remove(self.src_path)
        else:
            self.run_subprocess(["mv", self.src_path, archive])

    def run_job(self) -> None:
        """Triggers the vast transfer service

        Parameters
        ----------
        event : FileCreatedEvent
            modified event file
        """
        try:
            start_time = time.time()
            logging.info(
                {"Action": "Running job"} | self.config.log_tags,
                extra={"weblog": True},
            )

            # Check for missing data
            missing_files, missing_schema = check_for_missing_data(self.config)

            if missing_files or missing_schema:
                logging.error(
                    {
                        "Error": "Missing files when executing manifest",
                        "Missing data": missing_files,
                        "Missing schema": missing_schema,
                    }
                    | self.config.log_tags
                )
                return

            transfer = self.copy_to_vast()
            if not transfer:
                logging.error({"Error": "Could not copy to VAST"} | self.config.log_tags)
                return
            after_copy_time = time.time()
            logging.info(
                {
                    "Action": "Data copied to VAST",
                    "Duration_s": int(after_copy_time - start_time),
                }
                | self.config.log_tags
            )

            if self.config.transfer_endpoint is not None:
                response = self.trigger_transfer_service()
                if not response.status_code == 200:
                    logging.error(
                        {
                            "Error": "Could not trigger aind-data-transfer-service",
                            "Response": response.status_code,
                            "Message": response.text,
                        }
                        | self.config.log_tags
                    )
                    return
                after_post_time = time.time()
                logging.info(
                    {
                        "Action": "AIND Data Transfer Service notified",
                        "Duration_s": int(after_post_time - after_copy_time),
                    }
                    | self.config.log_tags
                )

            end_time = time.time()

            logging.info(
                {"Action": "Job complete", "Duration_s": int(end_time - start_time)}
                | self.config.log_tags,
                extra={"weblog": True},
            )
            self.move_manifest_to_archive()
        except:
            logging.exception(
                {"Error": "Job failed"} | self.config.log_tags,
                extra={"emit_exc": True},
            )
