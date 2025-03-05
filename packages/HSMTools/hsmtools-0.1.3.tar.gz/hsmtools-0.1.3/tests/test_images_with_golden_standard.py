import os
import json
import unittest
from data_preparation.image_pre_processor import ImagePreProcessor
from data_preparation.image_analyzer import ImageAnalyzer

class TestImageAnalyzerAgainstGolden(unittest.TestCase):

    def setUp(self):
        # Initialize the analyzer with the desired settings.
        self.preprocessor = ImagePreProcessor()
        self.analyzer = ImageAnalyzer(
            chunk_size=7,
            threshold_soft=0.05,
            threshold_hard=1,
            preprocessor=self.preprocessor
        )
        self.test_images_dir = os.path.join(os.path.dirname(__file__), 'images')
        self.golden_dir = os.path.join(os.path.dirname(__file__), 'golden_results')

    def _load_golden(self, file_name):
        path = os.path.join(self.golden_dir, file_name)
        with open(path, 'r') as f:
            return json.load(f)

    def _extract_metrics(self, image_result):
        return {
            "sample_area_px": image_result.get("sample_area_px"),
            "sample_height_px": image_result.get("sample_height_px"),
            "sample_perimeter_px": image_result.get("sample_perimeter_px"),
            "center_x_sample": image_result.get("center_x_sample"),
            "center_y_sample": image_result.get("center_y_sample")
        }

    def _run_test_for_image(self, image_file):
        image_path = os.path.join(self.test_images_dir, image_file)
        result = self.analyzer.process(image_path)
        self.assertIsNotNone(result, f"Processing failed for {image_file}")
        extracted = self._extract_metrics(result)
        golden = self._load_golden(os.path.splitext(image_file)[0] + ".json")
        # Compare integer metric directly.
        self.assertEqual(extracted["sample_area_px"], golden["sample_area_px"],
                         f"Mismatch in sample_area_px for {image_file}")
        # Compare float metrics with tolerance.
        self.assertAlmostEqual(extracted["sample_height_px"], golden["sample_height_px"], places=2,
                               msg=f"Mismatch in sample_height_px for {image_file}")
        self.assertAlmostEqual(extracted["sample_perimeter_px"], golden["sample_perimeter_px"], places=2,
                               msg=f"Mismatch in sample_perimeter_px for {image_file}")
        self.assertAlmostEqual(extracted["center_x_sample"], golden["center_x_sample"], places=2,
                               msg=f"Mismatch in center_x_sample for {image_file}")
        self.assertAlmostEqual(extracted["center_y_sample"], golden["center_y_sample"], places=2,
                               msg=f"Mismatch in center_y_sample for {image_file}")

    def test_image_1(self):
        self._run_test_for_image('test_image_1.Tif')

    def test_image_2(self):
        self._run_test_for_image('test_image_2.Tif')

    def test_image_3(self):
        self._run_test_for_image('test_image_3.Tif')

if __name__ == '__main__':
    unittest.main()