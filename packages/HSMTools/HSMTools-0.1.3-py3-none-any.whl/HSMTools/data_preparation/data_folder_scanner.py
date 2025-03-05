import os
import re


class DataFolderScanner:
    """
    Responsible for scanning the base directory for experiment folders.
    Experiment folder names must match the pattern M[0-9]{10}.
    """

    def __init__(self, base_path: str):
        self.base_path = base_path
        self.folder_regex = re.compile(r"M[0-9]{10}")

    def find_experiment_folders(self) -> list[str]:
        """
        Returns a list of folder names within the base directory that match the pattern.

        Returns:
            list[str]: List of experiment folder names.
        """
        folders = [
            item for item in os.listdir(self.base_path)
            if os.path.isdir(os.path.join(self.base_path, item)) and self.folder_regex.fullmatch(item)
        ]
        return folders