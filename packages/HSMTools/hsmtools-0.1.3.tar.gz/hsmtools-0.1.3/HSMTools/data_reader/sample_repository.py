import os
from typing import List, Optional

from HSMTools.data_reader.sample import Sample


class SampleRepository:
    """
    Repository for HSM samples.

    This repository scans a base folder for sample subdirectories. Each valid sample folder must contain
    a parquet file named "<folder_name>_results.parquet" and is represented by a Sample object.
    Filtering and selection is solely based on sample ids, where the id is defined by the folder name.

    Available methods include:
      • select_single(sample_id)
      • select_multiple(sample_ids)
      • hide_single(sample_id)
      • hide_multiple(sample_ids)
      • reset_filter() – to restore all samples as active.
    """

    def __init__(self, base_path: str, thresholded_subfolder: str = "thresholded_images"):
        """
        Initializes the repository.

        Args:
            base_path (str): Absolute path to the folder that contains sample subfolders.
            thresholded_subfolder (str): Name of the image subfolder inside each sample folder.
        """
        self.base_path = base_path
        self.thresholded_subfolder = thresholded_subfolder
        self._all_samples: List[Sample] = []  # List of all Sample objects loaded.
        self._active_samples: List[Sample] = []  # Subset of Sample objects after filtering/hiding.
        self._load_samples()

    def _load_samples(self) -> None:
        """
        Scans the base directory for sample subfolders.
        A valid sample folder must contain a parquet file following the naming convention "<folder_name>_results.parquet".
        """
        for entry in os.listdir(self.base_path):
            sample_folder = os.path.join(self.base_path, entry)
            if os.path.isdir(sample_folder):
                # Expect a parquet file with the naming convention: "<entry>_results.parquet"
                parquet_file = os.path.join(sample_folder, f"{entry}_results.parquet")
                if os.path.exists(parquet_file):
                    sample = Sample(self.base_path, entry, self.thresholded_subfolder)
                    self._all_samples.append(sample)
        # Initially, all samples are active.
        self._active_samples = list(self._all_samples)

    def select_single(self, sample_id: str) -> Optional[Sample]:
        """
        Returns a single Sample object matching the provided sample id from the active samples.

        Args:
            sample_id (str): The sample identifier (i.e. the folder name).

        Returns:
            Sample or None: The matching Sample object if found; otherwise None.
        """
        for sample in self._active_samples:
            if sample.sample_name == sample_id:
                return sample
        return None

    def select_multiple(self, sample_ids: List[str]) -> List[Sample]:
        """
        Returns a list of Sample objects matching the provided list of sample ids (folder names).

        Args:
            sample_ids (List[str]): List of sample identifiers.

        Returns:
            List[Sample]: List of matching Sample objects.
        """
        return [sample for sample in self._active_samples if sample.sample_name in sample_ids]

    def hide_single(self, sample_id: str) -> "SampleRepository":
        """
        Hides a single sample from further processing by removing it from the active samples list.

        Args:
            sample_id (str): The sample identifier to hide.

        Returns:
            SampleRepository: self to allow method chaining.
        """
        self._active_samples = [
            sample for sample in self._active_samples if sample.sample_name != sample_id
        ]
        return self

    def hide_multiple(self, sample_ids: List[str]) -> "SampleRepository":
        """
        Hides multiple samples from further processing by removing them from the active samples list.

        Args:
            sample_ids (List[str]): List of sample identifiers to hide.

        Returns:
            SampleRepository: self to allow method chaining.
        """
        self._active_samples = [
            sample for sample in self._active_samples if sample.sample_name not in sample_ids
        ]
        return self

    def reset_filter(self) -> "SampleRepository":
        """
        Resets any hiding/filtering settings so that all samples become active.

        Returns:
            SampleRepository: self for method chaining.
        """
        self._active_samples = list(self._all_samples)
        return self

    def select(self) -> List[Sample]:
        """
        Returns all currently active Sample objects.

        Returns:
            List[Sample]: The list of active samples.
        """
        return self._active_samples


# === Example usage ===
if __name__ == "__main__":
    # Adjust the folder path to point to your samples directory.
    repo = SampleRepository("/path/to/samples")

    # Example: select a single sample.
    sample_obj = repo.select_single("sample1")
    if sample_obj:
        print(f"Sample '{sample_obj.sample_name}' selected.")
    else:
        print("Sample 'sample1' not found.")

    # Example: select multiple samples.
    multiple_samples = repo.select_multiple(["sample1", "sample2"])
    print("Multiple samples selected:")
    for s in multiple_samples:
        print(s.sample_name)

    # Example: hide a sample.
    repo.hide_single("sample1")
    print("After hiding 'sample1', active samples:")
    for s in repo.select():
        print(s.sample_name)

    # Reset the active samples.
    repo.reset_filter()
    print("After resetting, all samples available:")
    for s in repo.select():
        print(s.sample_name)