# -*- coding: utf-8 -*-
import glob
import logging
import os
import re
from datetime import datetime
from pathlib import Path

import click
import pandas as pd
from dotenv import find_dotenv, load_dotenv

from src.utilities import read_config

# Load config.yaml
config = read_config()

# Load logger
logger = logging.getLogger(__name__)

def extract_date_from_string(date_string: str) -> datetime | None:
    """Extracts a date from a string using regex and converts it to a datetime object.
    
    Args:
        date_string (str): A string containing a date in the format '19 July 2024' or with ordinal suffixes.
    
    Returns:
        datetime.date | None: Extracted date or None if no match is found.
    """
    match = re.search(r"(\d{1,2})(?:st|nd|rd|th)? ([A-Za-z]+) (\d{4})", date_string)  
    if match:
        day, month, year = match.groups()
        extracted_date = datetime.strptime(f"{day} {month} {year}", "%d %B %Y").date()
        return extracted_date
    else:
        logger.warning(f"Failed to extract date from '{date_string}'")
        return None

def process_historic_file(df: pd.DataFrame, file_path: str) -> pd.DataFrame:
    """Processes historic format spreadsheets to match new format structure.
    
    Args:
        df (pd.DataFrame): DataFrame containing raw data.
        file_path (str): Path to the file being processed.
    
    Returns:
        pd.DataFrame: Processed DataFrame with structured format.
    """
    try:
        # Select relevant rows and columns
        selected_rows = list(range(7))  # First 7 rows contain relevant data

        # If the dataframe has shape (17, 9), copy the HDC value from column 1 to the last column
        if df.shape == (17, 9):
            selected_cols = [2, 3, 5]
            df = df.iloc[selected_rows, selected_cols]

            hdc_value = df.iloc[-1, 1]  # Extract HDC value
            df.iloc[-1, -1] = hdc_value  # Copy to last column
            
            df.drop(columns=[df.columns[1]], inplace=True)  # Drop the original HDC column
            
        else:
            selected_cols = [2, 5]  # Adjust based on actual needed columns
            df = df.iloc[selected_rows, selected_cols]

        # Extract date
        date = extract_date_from_string(df.iloc[0, 0])
        if date is None:
            raise ValueError(f"Could not extract date from {file_path}")
        
        # Rename columns for clarity
        df.columns = ["type", "group_value"]
        
        # Step 1: Assign 'total' to group for original 'prison' type
        df.loc[df["type"] == "Population", "group"] = "total"
        df.loc[df["type"] == "Population", "type"] = "prison"

        # Step 2: Assign correct group values for male and female estate, handling variations
        df.loc[df["type"].isin(["Population in male estate", "Male population"]), "group"] = "male"
        df.loc[df["type"].isin(["Population in female estate", "Female population"]), "group"] = "female"

        # Step 3: Change type for male and female estate to 'prison'
        df.loc[df["type"].isin(["Population in male estate", "Population in female estate", "Male population", "Female population"]), "type"] = "prison"
        
        # Step 4: Map other types to their new format
        type_mapping = {
            "Useable Operational Capacity": "operational_capacity",
            "Home Detention Curfew caseload": "hdc"
        }
        df["type"] = df["type"].replace(type_mapping)

        # Step 5: Ensure 'total' is assigned to operational capacity and HDC
        df.loc[df["type"].isin(["operational_capacity", "hdc"]), "group"] = "total"
        
        # Assign extracted date and cleanup
        df = (
            df.assign(date=date)  # Assign extracted date
            .rename(columns={"group_value": "value"})  # Rename column for consistency
            .assign(value=lambda x: pd.to_numeric(x["value"], errors="coerce").astype("Int64"))  # Convert values to numeric
            .loc[:, ["date", "group", "type", "value"]]  # Reorder columns (keep all rows)
            .loc[4:]  # Keep rows from index 4 onwards (after dropping unwanted metadata)
        )
        logger.info(f"Successfully processed file: {file_path}") # Log success
        return df

    except Exception as e:
        logger.exception(f"Error processing historic file {file_path}: {e}")
        return pd.DataFrame()  # Return empty DataFrame to avoid breaking concat

def process_new_file(df: pd.DataFrame, file_path: str) -> pd.DataFrame:
    """Processes new format spreadsheets into structured format.

    Args:
        df (pd.DataFrame): Raw data as DataFrame.
        file_path (str): Path to the file being processed.

    Returns:
        pd.DataFrame: Processed DataFrame.
    """
    try:
        selected_rows = list(range(6))  # First 6 rows contain relevant data
        selected_cols = [2, 4, 6, 7, 8]  # Adjust for new format
        df = df.iloc[selected_rows, selected_cols]

        # Extract date
        date = extract_date_from_string(df.iloc[0, 0])
        if date is None:
            raise ValueError(f"Could not extract date from {file_path}")

        df = (
            df.assign(date=date)
            .loc[[4, 5, 6, 8], :]
            .rename(columns=dict(zip(df.columns, ["type", "total", "male", "female", "youth", "date"])))
            .melt(id_vars=["date", "type"], var_name="group", value_name="value")
            .replace({
                "type": {
                    "Population": "prison",
                    "Useable Operational Capacity": "operational_capacity",
                    "Headroom": "headroom",
                    "Home Detention Curfew caseload": "hdc"
                }
            })
            .assign(value=lambda df: pd.to_numeric(df["value"], errors="coerce").astype("Int64"))
            .loc[:, ["date", "group", "type", "value"]]
        )
        logger.info(f"Successfully processed file: {file_path}")  # Log success
        return df

    except Exception as e:
        logger.exception(f"Error processing historic file {file_path}: {e}")
        return pd.DataFrame()  # Return empty DataFrame

def process_file(file_path: str) -> pd.DataFrame:
    """Processes a file based on its shape and format.
    
    Args:
        file_path (str): Path to the raw data file.

    Returns:
        pd.DataFrame: Processed DataFrame.
    """
    try:
        df = pd.read_excel(file_path, engine="odf").dropna(how="all")

        if df.shape in [(18, 8), (17, 8), (17, 9)]:  # Historic formats
            return process_historic_file(df, file_path)
        elif df.shape == (25, 9):
            return process_new_file(df, file_path)
        else:
            logging.warning(f"Skipping {file_path}: Unrecognized format {df.shape}")
            return pd.DataFrame()

    except Exception as e:
        logging.exception(f"Error processing {file_path}: {e}")
        return pd.DataFrame()

# Extract paths from config
DEFAULT_INPUT_DIR = config["data"]["rawFilePath"]
DEFAULT_OUTPUT_DIR = config["data"]["clnFilePath"]

"""
Temporarily removing CLI options for direct function call.
@click.command()
@click.option('--input_dir', default=DEFAULT_INPUT_DIR, type=click.Path(exists=True),
            help="Directory containing raw data files.")
@click.option('--output_dir', default=DEFAULT_OUTPUT_DIR, type=click.Path(),
            help="Directory to save processed data.")
@click.option("--file-pattern", default="*.ods", help="File pattern to match.")
"""

def main(input_dir=DEFAULT_INPUT_DIR, output_dir=DEFAULT_OUTPUT_DIR, file_pattern="*.ods") -> None:
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger.info('Making final data set from raw data')

    file_paths = glob.glob(f"{input_dir}/**/{file_pattern}", recursive=True)

    df = (
        pd.concat([process_file(file) for file in file_paths], ignore_index=True)
        .sort_values(["date", "group", "type"])
        .reset_index(drop=True)
    )

    # Extract date range
    if not df.empty and "date" in df.columns:
        min_date = df["date"].min().strftime("%Y-%m-%d")
        max_date = df["date"].max().strftime("%Y-%m-%d")
        date_range = f"{min_date}_to_{max_date}"
    else:
        date_range = datetime.today().strftime("%Y-%m-%d")  # Fallback if no valid dates

    save_filename = "processed_data.csv"
    save_path = Path(output_dir) / save_filename

    df.to_csv(save_path, index=False)
    logger.info("Processed data saved to %s", save_path)

    # Save date range in a separate log file
    metadata_file = Path(output_dir) / "processed_dates.log"
    with open(metadata_file, "a", encoding="utf-8") as log_file:
        log_file.write(f"{datetime.now().isoformat()} - Processed date range: {date_range}\n")

    logger.info("Date range recorded in %s", {metadata_file})


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
    logging.basicConfig(level=log_level, format=log_fmt)

    main()
