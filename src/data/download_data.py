#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor
import requests
from datetime import datetime

from src.utilities import read_config

config = read_config()

# Configure logging
def setup_logging(filename="download_log.log", log_path=config['data']['logsPath']):
    """Sets up logging configuration."""
    os.makedirs(log_path, exist_ok=True)  # Ensure the directory exists

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=os.path.join(log_path, filename),  # Saves logs to a file
        filemode="a"  # Appends to existing log file
    )

def extract_year_from_title(title):
    """Extracts the first 4-digit year found in the title."""
    match = re.search(r'\b(20\d{2})\b', title)
    return match.group(1) if match else None

def get_api_urls(years=None):
    """Fetch all API URLs and filter by year if specified."""
    url = 'https://www.gov.uk/api/content/government/collections/prison-population-statistics'
    response = requests.get(url)
    documents = response.json().get('links', {}).get('documents', [])

    api_urls = []
    for document in documents:
        title = document.get('title', '')
        year = extract_year_from_title(title)

        if not year:
            # Fallback to public_updated_at if year not in title
            public_updated_at = document.get('public_updated_at')
            if public_updated_at:
                year = str(datetime.strptime(public_updated_at, "%Y-%m-%dT%H:%M:%SZ").year)

        if year and (years is None or year in years):
            api_urls.append((document['api_url'], year))

    return api_urls

def download_files(url, year, path=config['data']['rawFilePath']):
    """Downloads spreadsheet attachments from a given API URL if not already downloaded."""
    response = requests.get(url)
    data = response.json()
    attachments = data['details']['attachments']

    # Exclude Word document content types
    spreadsheet_attachments = [
        attachment['url'] for attachment in attachments
        if attachment.get('content_type') not in {
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        and "monthly" not in attachment.get('title', '').lower()  # Exclude "monthly" files
    ]

    # Define the full directory path with the year subfolder
    year_path = os.path.join(path, year)
    os.makedirs(year_path, exist_ok=True)  # Ensure the directory exists

    files_downloaded = False  # Track if any files were downloaded
    files_skipped = 0  # Track skipped files

    for spreadsheet_url in spreadsheet_attachments:
        filename = os.path.join(year_path, os.path.basename(spreadsheet_url))

        if os.path.exists(filename):
            logging.info(f"Skipping {os.path.basename(filename)} (already downloaded).")
            files_skipped += 1
            continue  # Skip downloading this file

        # Make a GET request to download the spreadsheet file
        spreadsheet_response = requests.get(spreadsheet_url)

        # Save the spreadsheet content to a local file
        with open(filename, 'wb') as file:
            file.write(spreadsheet_response.content)

        logging.info(f"Downloaded file {os.path.basename(filename)} to {year_path}/")
        files_downloaded = True  # Mark that at least one file was downloaded

    # Log completion message only once per year
    if files_downloaded:
        logging.info(f"Download complete for {year}!")
    elif files_skipped == len(spreadsheet_attachments):  
        # Only log this message once if all files were skipped
        logging.info(f"All files for {year} were already downloaded. No new downloads.")

def download_prison_population_data(years=None):
    """Fetches and downloads prison population statistics for specified years."""
    # Convert years to strings if given as integers
    if years:
        years = [str(year) for year in years]

    # Get filtered API URLs
    api_urls_with_years = get_api_urls(years=years)

    # Run downloads concurrently
    with ThreadPoolExecutor() as executor:
        for api_url, year in api_urls_with_years:
            executor.submit(download_files, api_url, year)

if __name__ == "__main__":
    setup_logging()
    parser = argparse.ArgumentParser(description="Download prison population statistics for specific years.")
    parser.add_argument(
        "years",
        nargs="*",
        type=int,
        help="Specify one or more years to download (e.g., 2024 2025). Leave empty to download all years.",
    )

    args = parser.parse_args()
    download_prison_population_data(years=args.years if args.years else None)