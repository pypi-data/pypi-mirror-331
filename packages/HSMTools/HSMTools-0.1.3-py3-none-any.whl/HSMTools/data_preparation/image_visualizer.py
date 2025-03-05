#!/usr/bin/env python3
"""
ImageVisualizer module

This module provides the ImageVisualizer class which encapsulates all
plotting/visualization responsibilities. This allows you to reuse and
extend your visualization functionality without affecting the main
processing code.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt

class ImageVisualizer:
    def __init__(self):
        pass

    def plot_image(self, ax, image, title="Image", cmap="gray"):
        """
        Plot an image on the given Axes.
        """
        ax.imshow(image, cmap=cmap)
        ax.set_title(title)
        ax.axis("off")

    def plot_sample_area_mask(self, ax, contour, center_x, center_y, height_line,
                                fill_color="green", edge_color="green"):
        """
        Plot the sample area mask with filled contours, the height line,
        and highlight the sample centroid.
        """

        # Unzip contour points
        x, y = zip(*contour)
        # Plot filled contour (offset x by center_x)
        ax.fill(np.array(x) - center_x, y, color=fill_color, alpha=0.3,
                edgecolor=edge_color)
        # Re-plot the contour edge
        ax.plot(np.array(x) - center_x, y, color=edge_color)
        # Plot the height line (assumes height_line is a tuple of two (x,y) points)
        height_line_x, height_line_y = zip(*height_line)
        ax.plot(height_line_x, height_line_y, color="blue", linewidth=2,
                label="Height Line")
        # Mark the centroid on the plot (x already shifted; use 0 for center)
        ax.plot(0, center_y, "ro", markersize=5, label="Sample Center")
        ax.set_title("Summary")
        ax.legend()
        ax.axis("equal")
        ax.axis("off")

    def plot_lines_from_coordinates(self, ax, x_coords, y_coords, **kwargs):
        """
        Plot a line from given x and y coordinates on the provided Axes.
        """
        ax.plot(x_coords, y_coords, **kwargs)
        ax.set_xlabel("Shifted X (0 = sample center)")
        ax.set_ylabel("Y (pixels)")
        ax.axis("equal")
        ax.legend()

    def plot_x_selection(self, ax, xmin_shifted, xmax_shifted, color="red", alpha=0.5):
        """
        Plot vertical lines for the x selection boundaries.
        """
        ax.axvline(x=xmin_shifted, color=color, linestyle="--", alpha=alpha, label="Xmin")
        ax.axvline(x=xmax_shifted, color=color, linestyle="--", alpha=alpha, label="Xmax")

    def display_results(self, image_result, original_image_path):
        """
        Create a figure showing the thresholded image, the original image, and
        the sample area mask with contours. Expects `image_result` as produced
        by your processing routine.
        """
        # Load original image from disk
        original = cv2.imread(original_image_path)
        if original is None:
            raise ValueError(f"Could not load original image {original_image_path}")
        # Decode the threshold image from bytes
        thresh_bytes = image_result["thresh"]
        thresh = cv2.imdecode(np.frombuffer(thresh_bytes, np.uint8), cv2.IMREAD_UNCHANGED)

        # Extract values from the analysis result
        center_x = image_result["center_x_sample"]
        center_y = image_result["center_y_sample"]
        height_line = image_result["height_line"]
        shifted_contour_x, shifted_contour_y = image_result["contour_coordinates"]
        contours = image_result["sample_area_contour"]
        xmin_shifted = image_result["shifted_xmin"]
        xmax_shifted = image_result["shifted_xmax"]

        # Also get sample perimeter contour (for demonstration)
        sample_perimeter = image_result.get("sample_perimeter_coordinates", None)
        if sample_perimeter:
            sample_contour_x, sample_contour_y = zip(*sample_perimeter)
        else:
            sample_contour_x, sample_contour_y = ([], [])

        # Create subplots
        fig, axes = plt.subplots(3, 1, figsize=(5, 15))

        # Plot original image
        self.plot_image(axes[0], original, title="Original", cmap=None)
        # Plot thresholded image
        self.plot_image(axes[1], thresh, title="Thresholded & Inverted")
        # Plot sample area mask with contours
        self.plot_sample_area_mask(axes[2], contours, center_x, center_y, height_line)
        self.plot_x_selection(axes[2], xmin_shifted, xmax_shifted, color="red", alpha=0.5)
        self.plot_lines_from_coordinates(axes[2], shifted_contour_x, shifted_contour_y,
                                         color="grey", label="Threshold Boundary")
        if sample_contour_x and sample_contour_y:
            self.plot_lines_from_coordinates(
                axes[2],
                np.array(sample_contour_x) - center_x,
                sample_contour_y,
                color="red",
                label="Sample Contour"
            )
        plt.tight_layout()
        plt.show()