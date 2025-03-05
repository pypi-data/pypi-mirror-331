import cv2
import numpy as np


class ImagePreProcessor:
    """
    Simple processor that loads an image, applies Gaussian blur and thresholding,
    then removes unwanted areas using connected component analysis.
    """
    def __init__(self, gaussian_filter_size: tuple = (19, 19), threshold_type: int = cv2.THRESH_BINARY + cv2.THRESH_OTSU):
        self.gaussian_filter_size = gaussian_filter_size
        self.threshold_type = threshold_type

    def process(self, image: np.ndarray) -> np.ndarray:
        blurred = cv2.GaussianBlur(image, self.gaussian_filter_size, 0)
        # For binary inverse thresholding
        _, thresh = cv2.threshold(blurred, 0, 255, self.threshold_type)
        # Invert so that components become white
        inverted = 255 - thresh
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(inverted, connectivity=8)
        if num_labels <= 1:
            return thresh
        largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        processed = thresh.copy()
        for label in range(1, num_labels):
            if label != largest_label:
                processed[labels == label] = 255
        return processed