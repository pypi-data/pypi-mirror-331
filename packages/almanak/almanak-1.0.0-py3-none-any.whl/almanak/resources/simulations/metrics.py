import json
import os
import tempfile
from typing import TYPE_CHECKING

import pandas as pd
import requests

from ..._resource import SyncAPIResource

if TYPE_CHECKING:
    from ..._client import Almanak
else:
    from ..._base_client import SyncAPIClient

    Almanak = SyncAPIClient


class Metrics(SyncAPIResource):
    """
    Class to handle the metrics of a Monte Carlo simulation.
    """

    _client: Almanak

    def __init__(self, client: Almanak):
        self._client = client

    def get_raw_monte_carlo_metrics(self, monte_carlo_simulation_id, path_to_folder):
        """Get the results of a simulation."""
        try:
            response = self._client._hasura_client.get_mc_simulations_raw_metrics_gcs_uri(
                # FIXME, Logic for getting metrics shouldnt be on the middleware but should be on the implementor
                monte_carlo_simulation_id
            )

            if (
                response["data"]["getRawSimulationMetricsURL"]["valid"]
                and response["data"]["getRawSimulationMetricsURL"]["data"]
                and path_to_folder is not None
            ):
                data = response["data"]["getRawSimulationMetricsURL"]["data"]
                self.download_data(path_to_folder, data)

            return response["data"]["getRawSimulationMetricsURL"]

        except ValueError as e:
            print(f"Error from HasuraClient: {e}")
            raise e

    def download_data(self, path_to_folder, data):
        """Download the data from the response['data'] payload."""
        # Determine the absolute folder path
        folder_path = os.path.abspath(path_to_folder)

        # Ensure the directory exists
        os.makedirs(folder_path, exist_ok=True)

        total_count = len(data)  # Total number of items in the list

        # Download and save each file in the response data
        for index, item in enumerate(data, start=1):
            print(
                f"Downloading data for simulation {item['simulation_id']}... ({index}/{total_count})"
            )
            url = item.get("url")
            if url:
                try:
                    res = requests.get(url, timeout=30)
                    # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
                    res.raise_for_status()

                    # Save the content to a file
                    file_path = os.path.join(
                        folder_path, f"{item['simulation_id']}_data.json"
                    )
                    with open(file_path, "wb") as file:
                        file.write(res.content)

                except requests.exceptions.RequestException as e:
                    print(
                        f"Error downloading data from {item['simulation_id']} {url}: {e}"
                    )

    def _export(
        self,
        path_to_raw_metrics_folder,
        path_to_result_folder,
        address=None,
        environment_step=None,
        metrics_keys=None,
    ):
        """Filter the metrics by environment_step (<=), address, and specified metric keys.
        If any parameter is None, don't filter_by based on that parameter.
        """
        # Verify that the raw metrics folder exists and is a directory
        if not os.path.isdir(path_to_raw_metrics_folder):
            raise FileNotFoundError(
                f"Raw metrics folder not found: {path_to_raw_metrics_folder}"
            )

        # Determine whether the given path is absolute or relative
        if not os.path.isabs(path_to_raw_metrics_folder):
            path_to_raw_metrics_folder = os.path.join(
                os.getcwd(), path_to_raw_metrics_folder
            )

        # Determine whether the result folder path is absolute or relative
        if not os.path.isabs(path_to_result_folder):
            path_to_result_folder = os.path.join(os.getcwd(), path_to_result_folder)

        # Verify that the result folder is a directory or create it if needed
        if not os.path.isdir(path_to_result_folder):
            try:
                os.makedirs(path_to_result_folder, exist_ok=True)
            except Exception as e:
                raise OSError(
                    f"Failed to create result folder {path_to_result_folder}: {e}"
                )
        # List all JSON files in the raw metrics folder
        json_files = [
            filename
            for filename in os.listdir(path_to_raw_metrics_folder)
            if filename.endswith(".json")
        ]

        # If no JSON files are found, raise an error
        if not json_files:
            raise FileNotFoundError(
                f"No .json files found in the raw metrics folder: {path_to_raw_metrics_folder}"
            )
        # Iterate through all files in the raw metrics folder
        output_files = []
        for filename in json_files:
            filepath = os.path.join(path_to_raw_metrics_folder, filename)
            # Verify that the file is readable and a valid JSON file
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
            except Exception as e:
                print(f"Skipping {filename} due to read error or invalid JSON: {e}")
                continue

            # Filter by environment_step if it's not None
            if environment_step is not None:
                data = [
                    entry
                    for entry in data
                    if entry.get("environment_step", float("inf")) <= environment_step
                ]

            # Filter by address if it's not None
            if address is not None:
                data = [entry for entry in data if entry.get("agent") == address]

            # Filter by metrics_keys if it's not None
            if metrics_keys is not None:
                data = [
                    entry for entry in data if all(key in entry for key in metrics_keys)
                ]

            # Construct the output file name using the original file name with a prefix or suffix
            output_filename = f"{os.path.splitext(filename)[0]}_filtered.json"
            output_filepath = os.path.join(path_to_result_folder, output_filename)

            # Write the filtered data to the result file
            with open(output_filepath, "w") as out_f:
                json.dump(data, out_f, indent=4)

                print(f"Filtered data from {filename} exported to {output_filepath}")
            output_files.append(output_filepath)
        return output_files

    def to_folder(
        self,
        path_to_raw_metrics_folder,
        path_to_result_folder,
        filter_by: dict,
    ):
        """Export and filter_by raw metrics of a simulation.
        Parameters:
        - path_to_raw_metrics_folder (str): Path to the folder containing the raw metrics files.
        - path_to_result_folder (str): Path to the folder where filtered results should be saved.
        - filter_by (dict): A dictionary containing the following filter_by criteria:
            - address (str): The address to filter_by by.
            - environment_step (int): The environment step to filter_by by.
            - metrics_keys (list): List of specific metric keys to include.

        """
        address = filter_by.get("address", None)
        environment_step = filter_by.get("environment_step", None)
        metrics_keys = filter_by.get("metrics_keys", [])
        return self._export(
            path_to_raw_metrics_folder,
            path_to_result_folder,
            address,
            environment_step,
            metrics_keys,
        )

    def to_dataframe(self, filter_by: dict) -> pd.DataFrame:
        address = filter_by.get("address", None)
        environment_step = filter_by.get("environment_step", None)
        metrics_keys = filter_by.get("metrics_keys", [])

        # Create temp folder to export raw metrics and results
        # Using the temp file context manager
        with tempfile.TemporaryDirectory() as temp_metrics:
            with tempfile.TemporaryDirectory() as temp_result_folder:
                # Export raw metrics to temp folder
                raw_metrics_files = self._export(
                    temp_metrics,
                    temp_result_folder,
                    address,
                    environment_step,
                    metrics_keys,
                )

                # Read pandas dataframe from a folder of jsons
                df = pd.concat(
                    [
                        pd.read_json(file, orient="records")
                        for file in raw_metrics_files
                    ],
                    ignore_index=True,
                )

                return df
