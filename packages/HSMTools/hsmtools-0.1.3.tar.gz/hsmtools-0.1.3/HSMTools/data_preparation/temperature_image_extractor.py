from typing import Dict, Any
import polars as pl

class TemperatureImageExtractor:
    """
    Extracts a Polars DataFrame mapping Temperature to ImagePath from trial data.
    """

    def extract(self, sample_data: Dict[str, Any]) -> pl.DataFrame:
        """
        Constructs a DataFrame with 'Temperature' and 'ImagePath' columns.
        The ImagePath is formed by combining the trial's directory and a zero‑padded ImageNr.

        Parameters:
            sample_data (Dict[str, Any]): Trial data containing the 'MeasuredValues' table and 'directory'.

        Returns:
            pl.DataFrame: DataFrame with 'Temperature' and 'ImagePath' columns.
        """
        if "MeasuredValues" not in sample_data or "directory" not in sample_data:
            raise ValueError("Trial data must contain both 'MeasuredValues' and 'directory'.")

        measured_values = sample_data["MeasuredValues"]
        directory = sample_data["directory"]

        # Filter to keep rows where ImageNr > 0.
        df = measured_values.filter(pl.col("ImageNr") > 0)
        df = df.with_columns(
            pl.format("{}/m_{}.Tif", pl.lit(directory), pl.col("ImageNr").cast(pl.Utf8).str.zfill(5)).alias("ImagePath")
        ).select(["Temperature", "ImagePath"])
        return df