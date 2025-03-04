import json
import os
import shutil
from typing import TYPE_CHECKING
import zipfile
from .metrics import Metrics
from ..._compat import cached_property
from ..._resource import SyncAPIResource

if TYPE_CHECKING:
    from ..._client import Almanak
else:
    from ..._base_client import SyncAPIClient

    Almanak = SyncAPIClient


class MonteCarlo(SyncAPIResource):
    """
    A class for creating and managing Monte Carlo simulations.
    """

    _client: Almanak
    metrics: Metrics

    @cached_property
    def metrics(self) -> Metrics:
        return Metrics(self._client)

    def _load_json_file(self, path):
        """Read and parse a JSON file, raising appropriate errors."""
        try:
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error reading JSON file '{path}': {e}")
            raise e

    def generate(self, folder):
        """Generate a new boilerplate project in the specified folder path or folder name."""
        # Determine whether the given path is absolute or relative
        if os.path.isabs(folder):
            folder_path = folder
        else:
            folder_path = os.path.join(os.getcwd(), folder)

        # Check if the directory already exists
        if os.path.exists(folder_path):
            print(f"The directory {folder_path} already exists.")
        else:
            # Create the directory
            os.makedirs(folder_path)
            print(f"Directory {folder_path} created.")

        # Get the absolute path of the new folder
        folder_path = os.path.abspath(folder_path)

        # Assume that the config folder (boiler-template) is in the same directory as the current file
        parent_dir = os.path.dirname(os.path.abspath(__file__))
        config_folder_path = os.path.join(parent_dir, "boiler-template")

        # Check if the config folder exists and then copy its contents to the new folder
        if os.path.exists(config_folder_path):
            self.copy_directory_contents(config_folder_path, folder_path)
        else:
            print(f"The config folder at {config_folder_path} does not exist.")

    def zip_config_folder(self, path_to_folder):
        # Check if the folder name is 'config'
        folder_name = os.path.basename(path_to_folder)
        if folder_name != "config":
            raise ValueError("Folder name must be 'config'")

        # Define the zip file path
        zip_file_path = os.path.join(
            os.path.dirname(path_to_folder), folder_name + ".zip"
        )

        # Create a zip file
        with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(path_to_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(
                        file_path,
                        os.path.relpath(file_path, os.path.dirname(path_to_folder)),
                    )

        return zip_file_path

    def create_mc_upload_config(self, path_to_folder=None):
        """Create a new monte_carlo simulation.
        Parameters:
        - path_to_folder: The path to config folder containing the necessary configurations.
        """
        try:
            # # Default to current working directory
            path_to_check = path_to_folder if path_to_folder else os.getcwd()
            # Verify if directory exists
            if not os.path.isdir(path_to_check):
                raise ValueError(f"Directory '{path_to_check}' not found.")
                # Check for required files

            # basic file validation
            required_files = ["configuration.yaml"]
            for file in required_files:
                if not os.path.exists(os.path.join(path_to_folder, file)):
                    raise ValueError(f"Error: '{file}' not found.")

            # zip up the folder
            path_to_zip_folder = self.zip_config_folder(path_to_folder)
            print(f"Zip file created at: {path_to_zip_folder}")
            # check if file path is valid and file exist
            if not os.path.exists(path_to_zip_folder):
                raise ValueError(f"Error: '{path_to_zip_folder}' not found.")
            response = (
                self._client._hasura_client.create_mc_simulation_get_upload_link()
            )
            # print(response)

            # function path_to_folder expects file to be pass basic validation
            monte_carlo_id = response["monte_carlo_id"]
            print(f"monte carlo simulation created with id: {monte_carlo_id}")

            upload_success = self._client._hasura_client.upload_zip_to_gcs(
                response["upload_link"], path_to_zip_folder
            )
            return {"monte_carlo_id": monte_carlo_id, "upload_success": upload_success}

        except json.JSONDecodeError as e:
            print(f"Error reading JSON file: {e}")
            raise e  # re-raise the exception
        except ValueError as e:
            print(f"Error from HasuraClient: {e}")
            raise e  # re-raise the exception

    def validate_mc_config(self, monte_carlo_id):
        """Validate the configuration of a monte carlo simulation."""

        response = self._client._hasura_client.validate_mc(monte_carlo_id)
        return response

    def start(self, monte_carlo_id):
        """Start a monte carlo simulation."""
        response = self._client._hasura_client.start_mc_simulation(monte_carlo_id)
        return response

    def get_status(self, monte_carlo_id):
        """Get the status of a simulation."""
        try:
            response = self._client._hasura_client.get_simulation_status(monte_carlo_id)
            return response["data"]["group_simulations_by_pk"]["status"]
        except ValueError as e:
            print(f"Error from HasuraClient: {e}")
            raise e  # re-raise the exception

    def get_metrics(self, monte_carlo_id, path_to_folder=None):
        """Get the metrics of a monte carlo simulation."""
        # check if the monte_carlo_id belongs to user and is status is completed
        response = self._client._hasura_client.get_simulation_status(monte_carlo_id)
        # check if data array return is empty
        if not response["data"]:
            raise ValueError("Invalid monte carlo id")
        # check if status is completed
        if response["data"]["group_simulations_by_pk"]["status"] != "completed":
            raise ValueError("Monte Carlo simulation is not completed")

        return self.metrics.get_raw_monte_carlo_metrics(monte_carlo_id, path_to_folder)

    def copy_directory_contents(self, src, dest):
        """Copy the contents of a directory to another directory."""
        for root, dirs, files in os.walk(src):  # Correctly unpack all three values here
            dest_dir = os.path.join(dest, os.path.relpath(root, src))
            os.makedirs(dest_dir, exist_ok=True)
            for file_ in files:
                src_file = os.path.join(root, file_)
                dest_file = os.path.join(dest_dir, file_)
                shutil.copy2(src_file, dest_file)
