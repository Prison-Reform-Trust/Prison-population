#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import argparse
from concurrent.futures import ThreadPoolExecutor
import requests
from datetime import datetime

def extract_year_from_title(title):
    """Extracts the first 4-digit year found in the title."""
    match = re.search(r'\b(20\d{2})\b', title)
    return match.group(1) if match else None

def get_api_urls(years=None):
    """Fetch all API URLs and filter by year if specified."""
    url = 'https://www.gov.uk/api/content/government/collections/prison-population-statistics'
    response = requests.get(url)
    documents = response.json()['links']['documents']

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

def download_files(url, year, path='data/raw/'):
    """Downloads spreadsheet attachments from a given API URL."""
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
    ]

    # Define the full directory path with the year subfolder
    year_path = os.path.join(path, year)
    os.makedirs(year_path, exist_ok=True)  # Ensure the directory exists

    for spreadsheet_url in spreadsheet_attachments:
        # Make a GET request to download the spreadsheet file
        spreadsheet_response = requests.get(spreadsheet_url)
        
        # Extract the filename from the URL
        filename = os.path.join(year_path, spreadsheet_url.split('/')[-1])
        
        # Save the spreadsheet content to a local file
        with open(filename, 'wb') as file:
            file.write(spreadsheet_response.content)
        
        print(f"Downloaded file {os.path.basename(filename)} to {year_path}/")
    print(f"Download complete for {year}!")

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
    parser = argparse.ArgumentParser(description="Download prison population statistics for specific years.")
    parser.add_argument(
        "years",
        nargs="*",
        type=int,
        help="Specify one or more years to download (e.g., 2024 2025). Leave empty to download all years.",
    )

    args = parser.parse_args()
    download_prison_population_data(years=args.years if args.years else None)