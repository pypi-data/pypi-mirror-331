import os
import shutil
import tempfile
import unittest
import subprocess


class TestCLIIntegration(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for output
        self.temp_output = tempfile.mkdtemp()
        # Define the path for your sample data folder (adjust relative to this file)
        self.sample_data = os.path.join(os.path.dirname(__file__), "sample_data")
        # For this example, assume sample_data has subfolders for the experiments.

    def tearDown(self):
        shutil.rmtree(self.temp_output)

    def test_cli_runs_and_creates_output(self):
        # Construct the command line.
        # Assuming your CLI is defined in a module called cli.py at the project root.
        cli_path = os.path.join(os.path.dirname(__file__), "../HSMTools/data_preparation", "cli.py")
        cmd = [
            "python", cli_path,
            self.sample_data,  # input_folder containing trial subfolders
            self.temp_output,
            "--chunk_size", "7",
            "--threshold_soft", "0.05",
            "--threshold_hard", "1"
        ]
        # Run the CLI as a subprocess.
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, msg=f"CLI failed: {result.stderr}")

        # Check that at least one trial folder was created with results.
        trial_folders = [name for name in os.listdir(self.temp_output) if
                         os.path.isdir(os.path.join(self.temp_output, name))]
        self.assertGreater(len(trial_folders), 0, "No trial folders created by the CLI.")

        # Optionally, check for specific files in the first trial folder.
        first_trial = os.path.join(self.temp_output, trial_folders[0])
        parquet_files = [f for f in os.listdir(first_trial) if f.endswith(".parquet")]
        self.assertGreater(len(parquet_files), 0, "Parquet result file not found in the trial folder.")


if __name__ == '__main__':
    unittest.main()