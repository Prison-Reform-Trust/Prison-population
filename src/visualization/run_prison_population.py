#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
This script downloads weekly prison population data from the Ministry of Justice website,
processes it, and generates charts visualizing various aspects of the prison population
in England and Wales.
'''

from src import utilities as utils
from src.data import download_data, make_dataset, weekly_data_summary
from src.visualization import (HDC_caseload, female_population,
                               operational_capacity, prison_population)


def download_data_and_make_dataset():
    download_data.download_prison_population_data(years=2025)
    make_dataset.main()
    weekly_data_summary.main()


def make_charts():
    prison_population.main()
    female_population.main()
    HDC_caseload.main()
    operational_capacity.main()


def main():
    utils.setup_logging(to_file=True)
    download_data_and_make_dataset()
    make_charts()


if __name__ == "__main__":
    main()

# Highest prison population 88,521 6 September 2024
