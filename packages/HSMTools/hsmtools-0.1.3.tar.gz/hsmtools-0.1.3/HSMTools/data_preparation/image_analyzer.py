import cv2
import matplotlib.pyplot as plt
import numpy as np
import polars as pl


def find_top_boundary(thresh: np.ndarray) -> np.ndarray:
    """
    Vectorized approach: for each column, find the first row where thresh == 255.
    If there's no such row, store NaN.
    """
    col_mask = (thresh == 255)
    top_y = col_mask.argmax(axis=0).astype(float)
    has_white = col_mask.any(axis=0)
    top_y[~has_white] = np.nan
    return top_y

def chunk_and_average(boundary: np.ndarray, chunk_size=10) -> np.ndarray:
    """
    Given a 1D array 'boundary' (length = image width),
    split into chunks of size 'chunk_size'. For each chunk,
    compute average x (column index) and average y (ignoring NaN).
    Returns an array of shape (N, 2): (x_avg, y_avg).
    """
    length = len(boundary)
    x_means = []
    y_means = []
    for start in range(0, length, chunk_size):
        end = min(start + chunk_size, length)
        cols = np.arange(start, end)
        chunk_slice = boundary[start:end]
        valid_mask = ~np.isnan(chunk_slice)
        if np.any(valid_mask):
            x_means.append(cols[valid_mask].mean())
            y_means.append(chunk_slice[valid_mask].mean())
    return np.column_stack((x_means, y_means))


def find_sample_boundary_from_left(
    chunked_points: np.ndarray,
    slope_base=0.0,
    threshold_soft=0.1,
    threshold_hard=0.2
):
    """
    Traverse 'chunked_points' from left to right.
    For consecutive chunks i, i+1:
       slope = (y2 - y1)/(x2 - x1)
       slope_offset = slope - slope_base

    If slope_offset < -threshold_hard => return x1 immediately
    If slope_offset < -threshold_soft for >=3 consecutive => return that x
    """
    consecutive_count = 0
    start_ix = None

    for i in range(len(chunked_points) - 1):
        x1, y1 = chunked_points[i]
        x2, y2 = chunked_points[i + 1]
        dx = x2 - x1
        dy = y2 - y1

        if abs(dx) < 1e-9:
            continue

        slope = dy / dx
        slope_offset = slope - slope_base

        # Hard threshold
        if slope_offset < -threshold_hard:
            return x1
        # Soft threshold
        if slope_offset < -threshold_soft:
            if consecutive_count == 0:
                start_ix = i + 1
            consecutive_count += 1
            if consecutive_count >= 5:
                return chunked_points[start_ix][0]
        else:
            consecutive_count = 0
            start_ix = None

    return None


def filter_contour_excluding_line(contour_points, start_point, end_point):
    """
    Given a closed contour (list of (x, y) points) and a straight line defined by
    start_point and end_point, this function splits the contour into two segments
    (using the points closest to start_point and end_point) and returns the segment
    whose points have a higher average lateral deviation from the straight line.

    Args:
        contour_points (list): List of (x, y) coordinates (e.g., from _find_and_flatten_contours).
        start_point (tuple): (x_start, yA)
        end_point (tuple): (x_end, yB)

    Returns:
        list: A list of (x, y) coordinates representing the filtered perimeter.
    """
    contour = np.array(contour_points, dtype=np.float32)

    # Find indices closest to start_point and end_point.
    dists_to_start = np.linalg.norm(contour - np.array(start_point, dtype=np.float32), axis=1)
    dists_to_end = np.linalg.norm(contour - np.array(end_point, dtype=np.float32), axis=1)
    idx_start = np.argmin(dists_to_start)
    idx_end = np.argmin(dists_to_end)

    # Split the closed contour into two segments.
    if idx_start <= idx_end:
        seg1 = contour[idx_start:idx_end + 1]
        seg2 = np.concatenate((contour[idx_end:], contour[:idx_start + 1]), axis=0)
    else:
        seg1 = np.concatenate((contour[idx_start:], contour[:idx_end + 1]), axis=0)
        seg2 = contour[idx_end:idx_start + 1]

    def avg_line_deviation(points, sp, ep):
        """
        Compute the average perpendicular distance of the points to the line defined by sp and ep.
        """
        sp = np.array(sp, dtype=np.float32)
        ep = np.array(ep, dtype=np.float32)
        line_vec = ep - sp
        line_len = np.linalg.norm(line_vec)
        if line_len < 1e-6:
            return np.inf
        diffs = points - sp
        # 2D cross product magnitude divided by line length.
        devs = np.abs(diffs[:, 0] * line_vec[1] - diffs[:, 1] * line_vec[0]) / line_len
        return np.mean(devs)

    deviation1 = avg_line_deviation(seg1, start_point, end_point)
    deviation2 = avg_line_deviation(seg2, start_point, end_point)

    # The segment with lower deviation is considered the straight line. Return the other.
    filtered_contour = seg2 if deviation1 < deviation2 else seg1

    return filtered_contour.tolist()

def find_sample_boundary_from_right(
    chunked_points: np.ndarray,
    slope_base=0.0,
    threshold_soft=0.1,
    threshold_hard=0.2
):
    """
    Traverse 'chunked_points' from right to left.
    For consecutive chunks i-1, i:
       slope = (y_i - y_{i-1})/(x_i - x_{i-1})
       slope_offset = slope - slope_base

    If slope_offset > threshold_hard => return x2 immediately
    If slope_offset > threshold_soft for >=3 consecutive => return that x
    """
    consecutive_count = 0
    start_ix = None

    for i in range(len(chunked_points) - 1, 0, -1):
        x1, y1 = chunked_points[i - 1]
        x2, y2 = chunked_points[i]
        dx = x2 - x1
        dy = y2 - y1

        if abs(dx) < 1e-9:
            continue

        slope = dy / dx
        slope_offset = slope - slope_base

        # Hard threshold
        if slope_offset > threshold_hard:
            return x2
        # Soft threshold
        if slope_offset > threshold_soft:
            if consecutive_count == 0:
                start_ix = i
            consecutive_count += 1
            if consecutive_count >= 5:
                return chunked_points[start_ix][0]
        else:
            consecutive_count = 0
            start_ix = None

    return None


def get_y_for_column(x_val: float, boundary_array: np.ndarray) -> float:
    """
    If x_val is fractional, do linear interpolation between floor and ceil.
    Return None if out-of-bounds or interpolation is invalid.
    """
    width = len(boundary_array)
    if x_val < 0 or x_val >= width:
        return None
    x0 = int(np.floor(x_val))
    x1 = int(np.ceil(x_val))
    if x0 == x1:
        val = boundary_array[x0]
        return val if not np.isnan(val) else None
    else:
        y0 = boundary_array[x0]
        y1 = boundary_array[x1]
        if np.isnan(y0) or np.isnan(y1):
            return None
        alpha = x_val - x0
        return (1 - alpha) * y0 + alpha * y1


def contour_to_bw_image(
    x_array: np.ndarray,
    y_array: np.ndarray,
    width: int,
    height: int
) -> np.ndarray:
    """
    Optional: Create a black/white image (2D ndarray) from a given contour.
    White (255) for pixels above the contour (assuming the contour is 'top boundary').
    """
    bw_image = np.zeros((height, width), dtype=np.uint8)
    x_int = x_array.astype(int)

    for i in range(len(x_array)):
        x = x_int[i]
        y = int(np.floor(y_array[i]))
        if 0 <= x < width and y >= 0:
            bw_image[: y + 1, x] = 255
    return bw_image

def arrays_to_polars(x_array: np.ndarray, y_array: np.ndarray) -> pl.DataFrame:
    """
    Optional: store x,y arrays in Polars for easy usage.
    """
    df = pl.DataFrame({"x": x_array, "y": y_array})
    return df

class ImageAnalyzer:
    def __init__(self, chunk_size=10, threshold_soft=0.1, threshold_hard=20, preprocessor=None):
        self.chunk_size = chunk_size
        self.threshold_soft = threshold_soft
        self.threshold_hard = threshold_hard
        self.preprocessor = preprocessor

    def process(self, image_path: str) -> dict:
        """
        Process the image at image_path: load image, threshold, extract boundaries,
        calculate sample area, height, perimeter, centroid, and contour arrays.
        Returns a dictionary of analysis results or None if processing fails.
        """
        original, gray, thresh = self._load_and_threshold(image_path)

        plt.show()
        if original is None:
            print(f"Could not open image: {image_path}")
            return None
        height, width = thresh.shape

        # 1) Get top boundary from thresholded image.
        top_y = find_top_boundary(thresh)

        # 2) Chunk and average the top boundary.
        chunked = chunk_and_average(top_y, chunk_size=self.chunk_size)
        if len(chunked) < 2:
            print("Not enough chunk points for slope analysis.")
            return None

        # 3) Compute the slope base (approximate tilt) using first and last chunk point.
        x_left, y_left = chunked[0]
        x_right, y_right = chunked[-1]
        dx = x_right - x_left
        slope_base = 0.0 if abs(dx) < 1e-9 else (y_right - y_left) / dx

        # 4) Find sample boundaries from left and right.
        x_start = find_sample_boundary_from_left(
            chunked_points=chunked,
            slope_base=slope_base,
            threshold_soft=self.threshold_soft,
            threshold_hard=self.threshold_hard
        )
        x_end = find_sample_boundary_from_right(
            chunked_points=chunked,
            slope_base=slope_base,
            threshold_soft=self.threshold_soft,
            threshold_hard=self.threshold_hard
        )
        if x_start is None or x_end is None:
            print(f"Could not locate sample boundaries reliably for {image_path}.")
            return None

        # 5) Interpolate y-values at x_start and x_end.
        yA = get_y_for_column(x_start, top_y)
        yB = get_y_for_column(x_end, top_y)
        # Override with averaging first and last three points.
        yA = np.mean(top_y[0:3])
        yB = np.mean(top_y[-3:])
        if (yA is None) or (yB is None):
            print("Could not interpolate top boundary at x_start/x_end.")
            return None

        # 6) Calculate the line slope from boundaries.
        dx_line = x_end - x_start
        slope_line = 0.0 if abs(dx_line) < 1e-9 else (yB - yA) / dx_line

        # 7) Fill area above the line and extract the line and contour arrays.
        area_mask, y_line_arr, contour_y_arr, (x_min, x_max) = self._fill_area(
            thresh, height, width, x_start, x_end, yA, yB, slope_line, top_y
        )

        # 8) Calculate valid x values where to determine sample height.
        valid_contour_x = np.arange(x_min, x_max + 1)
        valid_contour_x = np.hstack(([x_min], valid_contour_x, [x_max]))

        # 9) Compute sample height and identify the maximum height.
        sample_height_arr = y_line_arr - contour_y_arr
        if np.all(np.isnan(sample_height_arr)):
            print("No valid sample height found.")
            return None
        max_sample_height = np.nanmax(sample_height_arr)
        idx_max_height = np.nanargmax(sample_height_arr)
        x_for_h_max = valid_contour_x[idx_max_height]
        y_min_for_h_max = contour_y_arr[idx_max_height]  # top boundary
        y_max_for_h_max = y_line_arr[idx_max_height]       # line above it
        sample_area_px = np.count_nonzero(area_mask)

        # 10) Compute the centroid of the sample area.
        sample_pixels = np.argwhere(area_mask == 255)  # rows, cols
        if len(sample_pixels) == 0:
            print("No valid sample pixels found.")
            return None
        center_y_sample = sample_pixels[:, 0].mean()
        center_x_sample = sample_pixels[:, 1].mean()

        # 11) Build final (shifted) contour arrays.
        final_contour_mask = ~np.isnan(top_y)
        unshifted_x = np.arange(width)[final_contour_mask]
        unshifted_y = top_y[final_contour_mask]
        shifted_x = unshifted_x - center_x_sample
        shifted_y = unshifted_y  # no shift in y

        # Also shift the x-positions of the height line.
        x_for_h_max_shifted = x_for_h_max - center_x_sample
        max_height_line = (
            (x_for_h_max_shifted, y_min_for_h_max),
            (x_for_h_max_shifted, y_max_for_h_max),
        )
        xmin_shifted = x_min - center_x_sample
        xmax_shifted = x_max - center_x_sample

        # 12) Find and flatten sample area contours.
        sample_area_contour = self._find_and_flatten_contours(area_mask)

        # 13) Encode the thresholded image.
        encoded_thresh = self._encode_image(thresh)

        # 14 new way to determine and calculate perimeter
        start_point = (x_start, yA)
        end_point = (x_end, yB)
        perimeter_coords = filter_contour_excluding_line(sample_area_contour, start_point, end_point)
        perimeter = self._compute_perimeter_length(perimeter_coords)

        results = {
            "shifted_xmin": xmin_shifted,
            "shifted_xmax": xmax_shifted,
            "sample_area_px": sample_area_px,
            "sample_height_px": max_sample_height,
            "sample_perimeter_px": perimeter,
            "sample_perimeter_coordinates": perimeter_coords,
            "contour_coordinates": (shifted_x.tolist(), shifted_y.tolist()),
            "height_line": max_height_line,
            "center_x_sample": center_x_sample,
            "center_y_sample": center_y_sample,
            "sample_area_contour": sample_area_contour,
            "thresh": encoded_thresh,
        }

        return results

    # ----- Private helper methods -----

    def _load_and_threshold(self, image_path: str):
        """Load the image, convert to grayscale and apply binary inverse threshold."""
        original = cv2.imread(image_path)
        if original is None:
            return None, None, None

        gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        if self.preprocessor:
            gray = self.preprocessor.process(gray)

        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

        return original, gray, thresh

    def _fill_area(self, thresh: np.ndarray, height: int, width: int,
                   x_start: float, x_end: float, yA: float, yB: float, slope_line: float,
                   top_y: np.ndarray):
        """
        For x in [x_min, x_max], computes the y-values along the line defined by (x_start, yA) and (x_end, yB)
        and fills the area above the line with 255 in area_mask.
        Returns the area_mask, y_line_arr, contour_y_arr and the (x_min,x_max) used.
        """
        x_min = int(np.floor(min(x_start, x_end)))
        x_max = int(np.ceil(max(x_start, x_end)))
        x_min = max(0, x_min)
        x_max = min(width - 1, x_max)

        y_line_list = [yA]
        contour_y_list = [yA]
        area_mask = np.zeros((height, width), dtype=np.uint8)

        for x in range(x_min, x_max + 1):
            x_float = float(x)
            y_line = slope_line * (x_float - x_start) + yA
            if y_line is None:
                y_line_list.append(np.nan)
                contour_y_list.append(np.nan)
                continue
            y_line_floor = int(np.floor(y_line))
            if y_line_floor < 0:
                y_line_floor = -1
            if y_line_floor >= height:
                y_line_floor = height - 1
            valid_pixels = np.where(thresh[: y_line_floor + 1, x] == 255)[0]
            area_mask[valid_pixels, x] = 255
            y_line_list.append(y_line)
            contour_y_list.append(top_y[x])
        y_line_list.append(yB)
        contour_y_list.append(yB)

        y_line_arr = np.array(y_line_list)
        contour_y_arr = np.array(contour_y_list)
        return area_mask, y_line_arr, contour_y_arr, (x_min, x_max)

    def _compute_perimeter_length(self, perimeter_coords:list):
        """
        Compute the perimeter_length of the top boundary defined by the valid contour x positions and corresponding y values.
        """

        # Convert the input list to a NumPy array for easier slicing
        coords = np.array(perimeter_coords)

        perimeter_length = 0.0
        if coords.shape[0] > 1:
            # Compute Euclidean distances between successive points
            dx = np.diff(coords[:, 0])
            dy = np.diff(coords[:, 1])
            segment_lengths = np.sqrt(dx ** 2 + dy ** 2)
            perimeter_length = np.sum(segment_lengths)

        return perimeter_length

    def _find_and_flatten_contours(self, area_mask: np.ndarray):
        """
        Uses OpenCV to find contours and returns them as a list of flat lists.
        """
        contours, _ = cv2.findContours(area_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        flat_contours = []
        for cnt in contours:
            flat_cnt = cnt.reshape(-1, 2)
            flat_contours.extend(flat_cnt.tolist())
        largest_contour = max(contours, key=cv2.contourArea)
        flat_contour = largest_contour.reshape(-1, 2)
        return flat_contour if flat_contour.any() else []

    def _encode_image(self, image: np.ndarray) -> bytes:
        """
        Encodes the given image as PNG bytes.
        """
        success, encoded_image = cv2.imencode(".png", image)
        if not success:
            raise ValueError("Failed to encode image")
        return encoded_image.tobytes()


