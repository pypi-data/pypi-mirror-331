import os
import cv2
import polars as pl
from matplotlib import pyplot as plt

# --- Single Responsibility: Loading Parquet Data ---
class ParquetDataLoader:
    def __init__(self, parquet_path: str):
        """
        Loads Parquet data from the given path.
        """
        if not os.path.exists(parquet_path):
            raise FileNotFoundError(f"Parquet file not found: {parquet_path}")
        self.parquet_path = parquet_path
        self.data = None

    def load(self) -> pl.DataFrame:
        """
        Loads the Parquet file into a Polars DataFrame.
        """
        try:
            self.data = pl.read_parquet(self.parquet_path)
            return self.data
        except Exception as e:
            raise RuntimeError(
                f"Could not load data from path: {self.parquet_path}"
            ) from e


# --- Single Responsibility: Querying Temperature Data ---
class TemperatureDataQuery:
    def __init__(self, data: pl.DataFrame):
        """
        Handles queries on a Polars DataFrame containing temperature data.
        """
        self.data = data

    def get_contour(self, temperature: float):
        """
        Returns the contour coordinates for temperatures greater than the given threshold.
        The method expects that the column 'sample_perimeter_coordinates' holds
        a list of (x, y) tuples for each record.
        """
        df = self.data.filter(pl.col("Temperature") > temperature)
        if not df or df.is_empty():
            return None

        # Get the first available contour coordinate list.
        contour_xy = df["sample_perimeter_coordinates"].first()
        if contour_xy is None:
            return None

        try:
            x, y = zip(*contour_xy)
            return x, y
        except Exception:
            return None

    def get_image_path(self, temperature: float):
        """
        Returns the image path corresponding to the first record with Temperature > threshold.
        """
        df = self.data.filter(pl.col("Temperature") > temperature)
        if not df or df.is_empty():
            return None
        return df["ImagePath"].first()


# --- Single Responsibility: Loading an Image ---
class ImageLoader:
    def __init__(self, base_directory: str, image_subfolder: str = "thresholded_images"):
        """
        Loads images based on the base directory and an image subfolder.
        """
        self.base_directory = base_directory
        self.image_subfolder = image_subfolder

    def load(self, image_filename: str):
        """
        Loads an image in grayscale for the provided filename.
        """
        full_path = os.path.join(self.base_directory, self.image_subfolder, image_filename)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Image file not found: {full_path}")
        return cv2.imread(full_path, cv2.IMREAD_GRAYSCALE)


# --- Facade: DataReader that combines components ---
class DataReader:
    def __init__(self, parquet_path: str, image_subfolder: str = "thresholded_images"):
        """
        The facade that brings together data loading, querying, and image loading.
        """
        self.parquet_path = parquet_path
        self.base_directory = os.path.dirname(parquet_path)
        self.data_loader = ParquetDataLoader(parquet_path)
        self.data = None
        self.query = None
        self.image_loader = ImageLoader(self.base_directory, image_subfolder)

    def load_data(self):
        """
        Loads the Parquet data and initializes the TemperatureDataQuery.
        """
        self.data = self.data_loader.load()
        self.query = TemperatureDataQuery(self.data)

    def contour_for_temperature(self, temperature: float):
        """
        Returns the contour (x, y) for records with Temperature > threshold.
        """
        if self.query is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        return self.query.get_contour(temperature)

    def image_path_for_temperature(self, temperature: float):
        """
        Returns the image path for records with Temperature > threshold.
        """
        if self.query is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        return self.query.get_image_path(temperature)

    def picture_at_temperature(self, temperature: float):
        """
        Loads and returns an image corresponding to the first record
        with Temperature > threshold.
        """
        image_filename = self.image_path_for_temperature(temperature)
        if image_filename is None:
            raise ValueError(f"No image path found for temperature > {temperature}")
        return self.image_loader.load(image_filename)

    def get_data(self) -> pl.DataFrame:
        """
        Returns the loaded data.
        """
        return self.data


# --- Example usage ---
if __name__ == '__main__':
    # Instantiate and use the DataReader facade.
    parquet_file_path = os.path.join("../..", "tests", "output_data", "RT14", "RT14_results.parquet")
    reader = DataReader(parquet_file_path)
    reader.load_data()

    # Example of plotting the temperature vs. sample_height_px
    plt.plot(reader.data["Temperature"], reader.data["sample_height_px"], marker='o', linestyle='-')
    plt.xlabel("Temperature")
    plt.ylabel("Sample Height (px)")
    plt.title("Temperature vs. Sample Height")
    plt.show()

    # Uncomment to load an image and its contour.
    # img = reader.picture_at_temperature(1280)
    # contour = reader.contour_for_temperature(1280)
    # if img is not None and contour is not None:
    #     plt.imshow(img, cmap='gray')
    #     plt.plot(*contour, color="red", linewidth=3)
    #     plt.show()