# -------------------------------------------------------------------
# 3. Command Line Orchestration
# -------------------------------------------------------------------
import argparse
import os
import shutil

import cv2

from HSMTools.data_preparation.image_pre_processor import ImagePreProcessor
from HSMTools.data_preparation.image_analyzer import ImageAnalyzer
from HSMTools.data_preparation.result_processor import refine_analysis_result
from HSMTools.data_preparation.temperature_image_extractor import TemperatureImageExtractor
from HSMTools.data_preparation.sample_repository import SampleRepository
import polars as pl

_global_skip_existing = None

def process_trial_images(trial_name: str, trial_data: dict, output_base: str,
                         img_processor: ImagePreProcessor,
                         extractor: TemperatureImageExtractor,
                         chunk_size: int,
                         threshold_soft: float,
                         threshold_hard: float) -> None:
    """
    For one trial:
      - Use TemperatureImageExtractor to get mapping DataFrame.
      - For each image, process with ImageProcessor and then process_image.
      - Save the thresholded image and collected data in the trial's output subfolder.
    """
    # Create trial-specific output folder
    global _global_skip_existing

    trial_out_folder = os.path.join(output_base, trial_name)
    # check if trial_out_folder exists
    if os.path.exists(trial_out_folder):
        if _global_skip_existing is None:
            choice = input(f"Output folder {trial_out_folder} already exists.\n"
                           f"Choose an option:\n"
                           f"1. Skip this trial\n"
                           f"2. Overwrite this trial\n"
                           f"3. Skip all existing trials\n"
                           f"4. Overwrite all existing trials\n"
                           f"Enter choice (1-4): ").strip()

            if choice == "3":
                _global_skip_existing = True
                print("Will skip all existing trials.")
                return
            elif choice == "4":
                _global_skip_existing = False
                print("Will overwrite all existing trials.")
            elif choice == "1":
                print(f"Skipping trial {trial_name}.")
                return
            elif choice == "2":
                shutil.rmtree(trial_out_folder)
            else:
                print("Invalid choice. Skipping this trial.")
                return

        if _global_skip_existing:
            print(f"Skipping existing trial {trial_name}.")
            return
        elif _global_skip_existing is False:
            print(f"Overwriting existing trial {trial_name}.")
            shutil.rmtree(trial_out_folder)

    os.makedirs(trial_out_folder, exist_ok=True)
    thresh_folder = os.path.join(trial_out_folder, "thresholded_images")
    os.makedirs(thresh_folder, exist_ok=True)

    # Extract mapping DataFrame (Temperature <-> ImagePath)
    temp_img_df = extractor.extract(trial_data)
    image_paths = temp_img_df["ImagePath"].to_list()
    temperatures = temp_img_df["Temperature"].to_list()

    collected_results = []

    for i, (image_path, temperature) in enumerate(zip(image_paths, temperatures)):
        # Ensure the image exists
        if not os.path.exists(image_path):
            print(f"Image not found: {image_path}")
            continue

        # Load image
        original = cv2.imread(image_path)
        if original is None:
            print(f"Could not open image: {image_path}")
            continue

        # if i can be divided by 100, print the progress
        if (i+1) % 100 == 0:
            print(f"Processing image {i + 1} of {len(image_paths)}")

        # Save the thresholded image to output folder (use temperature as filename)
        thresh_filename = f"thresh_{temperature:.2f}.png"
        thresh_out_path = os.path.join(thresh_folder, thresh_filename)
        base_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        thresh_image = img_processor.process(base_image)
        cv2.imwrite(thresh_out_path, thresh_image)


        # Apply further analysis using the provided process_image function.
        # (process_image reads from disk – here we use the original image path)

        image_processor = ImageAnalyzer(
            chunk_size=chunk_size,
            threshold_soft=threshold_soft,
            threshold_hard=threshold_hard,
            preprocessor=img_processor
        )

        analysis_result = image_processor.process(
            image_path
        )
        if analysis_result is None:
            continue

        refined_result = refine_analysis_result(
            analysis_result,
            temperature=temperature,
            thresh_filename=thresh_filename,
        )
        collected_results.append(refined_result)

        collected_results.append(analysis_result)

    if collected_results:
        # Convert list of dicts to a Polars DataFrame
        result_df = pl.DataFrame(collected_results)
        # Save as Parquet with zstd compression (the file name uses the trial name)
        parquet_filename = f"{trial_name}_results.parquet"
        parquet_path = os.path.join(trial_out_folder, parquet_filename)
        result_df.write_parquet(parquet_path, compression="zstd")
        print(f"Results saved for trial {trial_name} at {parquet_path}")
    else:
        print(f"No valid results for trial {trial_name}.")


def main():
    parser = argparse.ArgumentParser(
        description="Process microscope experiments: load trial data, map Temperature to image paths, "
                    "process images with thresholding and advanced analysis, and save results."
    )
    parser.add_argument("input_folder", help="Path to the input folder containing trial subfolders.")
    parser.add_argument("output_folder", help="Path to the output folder where results will be stored.")
    parser.add_argument("--gaussian_filter_size", type=int, nargs=2, default=[19, 19],
                        help="Gaussian filter kernel size (e.g., --gaussian_filter_size 19 19)")
    parser.add_argument("--chunk_size", type=int, default=10, help="Chunk size for process_image")
    parser.add_argument("--threshold_soft", type=float, default=0.1, help="Threshold soft value for process_image")
    parser.add_argument("--threshold_hard", type=float, default=3.0, help="Threshold hard value for process_image")
    args = parser.parse_args()

    input_folder = args.input_folder
    output_folder = args.output_folder

    # Load trial repository from input folder.
    trial_repo = SampleRepository(input_folder)
    trials = trial_repo.load_all_trials()
    if not trials:
        print("No valid trials found.")
        return

    # Instantiate the TemperatureImageExtractor and ImageProcessor.
    extractor = TemperatureImageExtractor()
    img_processor = ImagePreProcessor(gaussian_filter_size=tuple(args.gaussian_filter_size))

    # For each trial, process its images.
    for trial_name, trial_data in trials.items():
        print(f"\nProcessing trial: {trial_name}")
        process_trial_images(
            trial_name=trial_name,
            trial_data=trial_data,
            output_base=output_folder,
            img_processor=img_processor,
            extractor=extractor,
            chunk_size=args.chunk_size,
            threshold_soft=args.threshold_soft,
            threshold_hard=args.threshold_hard
        )

def easycli():
    """
    An interactive command-line interface that prompts the user for each parameter one by one.
    Pressing Enter without input will select the default value.
    """
    print("Welcome to the Easy CLI for Microscope Experiment Processing!")
    print("You'll be prompted for each parameter one at a time.\n")

    # Get input folder.
    input_folder = input("Enter the path to the input folder containing trial subfolders: ").strip()
    while not input_folder or not os.path.exists(input_folder):
        input_folder = input("Invalid input folder. Please re-enter a valid input folder path: ").strip()

    # Get output folder.
    output_folder_input = input("Enter the path to the output folder where results will be stored: ").strip()
    if not output_folder_input:
        # Default: create an output folder as a sibling to the input folder with an _output suffix.
        input_abs = os.path.abspath(input_folder)
        input_parent = os.path.dirname(input_abs)
        input_basename = os.path.basename(input_abs)
        output_folder = os.path.join(input_parent, f"{input_basename}_output")
        print(f"No output folder provided. Using default: {output_folder}")
    elif ("/" not in output_folder_input) and (os.sep not in output_folder_input):
        # If only a simple folder name is given, create it at the same level as the input folder.
        input_abs = os.path.abspath(input_folder)
        input_parent = os.path.dirname(input_abs)
        output_folder = os.path.join(input_parent, output_folder_input)
        print(f"Using output folder at the same level as input folder: {output_folder}")
    else:
        output_folder = output_folder_input
    os.makedirs(output_folder, exist_ok=True)

    # Gaussian filter size (expects two integers)
    default_gaussian = "19 19"
    gaussian_input = input(f"Enter Gaussian filter kernel size (two integers) [default: {default_gaussian}]: ").strip()
    if gaussian_input:
        try:
            gaussian_filter_size = tuple(map(int, gaussian_input.split()))
            if len(gaussian_filter_size) != 2:
                print("Invalid input. Using default values.")
                gaussian_filter_size = (19, 19)
        except Exception:
            print("Invalid input. Using default values.")
            gaussian_filter_size = (19, 19)
    else:
        gaussian_filter_size = (19, 19)

    # Chunk size
    default_chunk = "10"
    chunk_size_input = input(f"Enter chunk size for process_image [default: {default_chunk}]: ").strip()
    chunk_size = int(chunk_size_input) if chunk_size_input.isdigit() else 10

    # Threshold soft
    default_threshold_soft = "0.1"
    threshold_soft_input = input(f"Enter threshold soft value for process_image [default: {default_threshold_soft}]: ").strip()
    try:
        threshold_soft = float(threshold_soft_input) if threshold_soft_input else 0.1
    except Exception:
        print("Invalid input. Using default value.")
        threshold_soft = 0.1

    # Threshold hard
    default_threshold_hard = "3.0"
    threshold_hard_input = input(f"Enter threshold hard value for process_image [default: {default_threshold_hard}]: ").strip()
    try:
        threshold_hard = float(threshold_hard_input) if threshold_hard_input else 3.0
    except Exception:
        print("Invalid input. Using default value.")
        threshold_hard = 3.0

    # Instantiate TemperatureImageExtractor and ImagePreProcessor.
    extractor = TemperatureImageExtractor()
    img_processor = ImagePreProcessor(gaussian_filter_size=gaussian_filter_size)

    # Load trial repository from input folder.
    trial_repo = SampleRepository(input_folder)
    trials = trial_repo.load_all_trials()
    if not trials:
        print("No valid trials found. Exiting.")
        return

    # Process each trial.
    for trial_name, trial_data in trials.items():
        print(f"\nProcessing trial: {trial_name}")
        process_trial_images(
            trial_name=trial_name,
            trial_data=trial_data,
            output_base=output_folder,
            img_processor=img_processor,
            extractor=extractor,
            chunk_size=chunk_size,
            threshold_soft=threshold_soft,
            threshold_hard=threshold_hard
        )

    print("\nProcessing complete. Check the output folder for results.")

def main():
    easycli()

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    easycli()
