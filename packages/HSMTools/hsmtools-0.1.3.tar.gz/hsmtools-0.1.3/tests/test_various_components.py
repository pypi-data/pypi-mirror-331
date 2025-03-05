import os
import unittest
import numpy as np
import polars as pl
from HSMTools.data_preparation.image_pre_processor import ImagePreProcessor
from HSMTools.data_preparation.image_analyzer import ImageAnalyzer
from HSMTools.data_preparation.temperature_image_extractor import TemperatureImageExtractor


class TestImagePreProcessor(unittest.TestCase):
    def test_process_returns_valid_threshold(self):
        # Create a dummy grayscale image (e.g., a constant image)
        img = np.full((100, 100), 128, dtype=np.uint8)
        processor = ImagePreProcessor(gaussian_filter_size=(5, 5))
        # Assuming that your process() function takes an image path,
        # you could modify your preprocessor for testing purpose 
        # or use a helper that processes an image array.
        # For this test, we assume a helper exists:
        processed = processor.process(img)
        self.assertIsNotNone(processed)
        # The processed image should be binary (0 or 255)
        self.assertIn(processed.max(), [0, 255])
        self.assertIn(processed.min(), [0, 255])


class TestTemperatureImageExtractor(unittest.TestCase):
    def test_extract_returns_valid_dataframe(self):
        # Create a dummy trial_data dictionary.
        # For instance, you might have a .dat file in your sample_data folder.
        # Here we mimic the expected keys.
        trial_data = {
            "data_file": os.path.join(os.path.dirname(__file__), "sample_data", "M2412180801", "M2412180801.dat"),
            "images_folder": os.path.join(os.path.dirname(__file__), "sample_data", "M2412180801")
        }
        extractor = TemperatureImageExtractor()
        # The extract function should return a Polars DataFrame with "ImagePath" and "Temperature" columns.
        df = extractor.extract(trial_data)
        self.assertIsInstance(df, pl.DataFrame)
        self.assertIn("ImagePath", df.columns)
        self.assertIn("Temperature", df.columns)


class TestImageAnalyzer(unittest.TestCase):
    def test_analyzer_process(self):
        # For a quick unit test, use one of your sample images.
        image_path = os.path.join(os.path.dirname(__file__), "images", "test_image_1.Tif")
        processor = ImagePreProcessor(gaussian_filter_size=(5,5))
        analyzer = ImageAnalyzer(chunk_size=7, threshold_soft=0.05, threshold_hard=1, preprocessor=processor)
        result = analyzer.process(image_path)
        self.assertIsNotNone(result)
        # Check for required keys.
        self.assertIn("sample_area_px", result)
        self.assertIn("sample_height_px", result)
        self.assertIn("sample_perimeter_px", result)
        self.assertIn("center_x_sample", result)
        self.assertIn("center_y_sample", result)


if __name__ == '__main__':
    unittest.main()