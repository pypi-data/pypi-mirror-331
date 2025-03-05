import os
from typing import Dict, Any

from HSMTools.data_preparation.data_folder_scanner import DataFolderScanner
from HSMTools.data_preparation.sqlite_data_loader import SQLiteDataLoader
import re

class SampleRepository:
    """
    Responsible for loading all trial data from experiment folders.
    Each trial is represented by a .dat SQLite file inside an experiment folder.
    """

    def __init__(self, base_path: str):
        self.base_path = base_path
        self.folder_scanner = DataFolderScanner(base_path)
        self.data_loader = SQLiteDataLoader()
        self.trial_regex = re.compile(r"RT[0-9]+")
        # todo make this regex adjustable

    def load_all_trials(self) -> Dict[str, Dict[str, Any]]:
        """
        Loads trial data from all experiment folders.

        Returns:
            Dict[str, Dict[str, Any]]: A mapping from trial name to trial data dictionary.
        """
        trials = {}
        folders = self.folder_scanner.find_experiment_folders()
        for folder in folders:
            # Construct the .dat file path: <base_path>/<folder>/<folder>.dat
            dat_file = os.path.join(self.base_path, folder, f"{folder}.dat")
            trial_data = self.data_loader.load_tables_from_file(dat_file)
            if not trial_data:
                continue

            # Extract trial name from the 'MeasurementSeriesMetaInfo' table, if available.
            trial_name = folder
            if "MeasurementSeriesMetaInfo" in trial_data:
                meta_info = trial_data["MeasurementSeriesMetaInfo"]
                if meta_info.shape[0] > 0:
                    trial_name_field = meta_info["Samplename"][0]
                    match = self.trial_regex.search(trial_name_field)
                    trial_name = match.group(0) if match else trial_name_field
                else:
                    print(f"Warning: 'MeasurementSeriesMetaInfo' is empty for folder {folder}.")
            else:
                print(f"Warning: 'MeasurementSeriesMetaInfo' not found in {dat_file}.")

            # Save the directory path in the trial data for later use.
            trial_data["directory"] = os.path.join(self.base_path, folder)
            trials[trial_name] = trial_data
        return trials