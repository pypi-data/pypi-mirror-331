import os

import numpy as np
import polars as pl


class Sample:
    """
    Represents a single sample folder that contains results (a Parquet file)
    and a folder of thresholded images.
    """

    def __init__(self, base_path: str, sample_name: str, thresholded_subfolder: str = "thresholded_images"):
        """
        :param base_path: Absolute path to the folder that contains all sample folders.
        :param sample_name: The name of the sample folder.
        :param thresholded_subfolder: Name of the subfolder where images are stored.
        """
        self.sample_name = sample_name
        self.sample_folder = os.path.join(base_path, sample_name)
        self.result_file = os.path.join(self.sample_folder, f"{sample_name}_results.parquet")
        self.thresholded_subfolder = os.path.join(self.sample_folder, thresholded_subfolder)
        self._data = None  # Lazy load the data

    def load_data(self) -> pl.DataFrame:
        """
        Loads and caches the parquet data as a Polars DataFrame.
        """
        if self._data is None:
            if not os.path.exists(self.result_file):
                raise FileNotFoundError(f"Parquet file not found: {self.result_file}")
            self._data = pl.read_parquet(self.result_file)
        return self._data

    def get_contour_for_temperature(self, temperature: float, centered=True):
        """
        Returns the contour coordinates from the parquet data
        for records with Temperature > given threshold.

        Assumes that the column 'sample_perimeter_coordinates'
        contains a list of (x, y) tuples.

        :param temperature: Temperature threshold.
        :return: The first available contour (as a tuple of x and y arrays), or None.
        """
        # Filter using Polars (assuming self.load_data returns a Polars DataFrame)
        df = self.load_data().filter(pl.col("Temperature") > temperature)
        if df.is_empty():
            return None, None

        # Get the first record's data for the contour and center:
        contour_coords = df["sample_perimeter_coordinates"].first()
        center_x = df["center_x_sample"].first()

        # Convert list of tuples directly into a NumPy array
        coords = np.array(contour_coords)  # shape: (n_points, 2)
        x = coords[:, 0]
        y = coords[:, 1]

        if centered:
            x = x - center_x  # center x by subtracting the center_x_sample value
            y = y - np.max(y)  # shift y so its maximum becomes 0

        return x, y

    def get_dataframe(self) -> pl.DataFrame:
        """
        Returns the loaded DataFrame.
        """
        return self.load_data()