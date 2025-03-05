def refine_analysis_result(analysis_result, temperature, thresh_filename):
    """
    Augment analysis_result with metadata and remove keys that are not needed.

    Args:
        analysis_result (dict): The original analysis dictionary.
        temperature (float): The temperature associated with the image.
        image_path (str): Path to the source image.
        thresh_filename (str): The filename of the thresholded image.

    Returns:
        dict: The refined analysis dictionary.
    """
    # Augment the dictionary with additional metadata.
    analysis_result["Temperature"] = temperature
    analysis_result["ImagePath"] = thresh_filename

    # Remove keys that are not needed in the paruqet, easier to just rerun imageanalyzer on thresh image.
    keys_to_delete = ["thresh", "sample_area_contour", "contour_coordinates"]
    for key in keys_to_delete:
        analysis_result.pop(key, None)

    return analysis_result