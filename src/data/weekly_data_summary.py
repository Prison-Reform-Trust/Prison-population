#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A script to process and filter weekly data for prison population, operational capacity,
and HDC caseload, ready for inclusion in weekly reports.
This script loads the data from a CSV file, filters it to include only the most recent two weeks.
"""

import pandas as pd


def load_data():
    """
    Load the dataset from a CSV file and return it as a pandas DataFrame.
    """
    # Load the dataset
    df = pd.read_csv("data/processed/processed_data.csv")

    return df


def filter_n_weeks(df, n_weeks=2):
    """
    Filters the input DataFrame to include only the rows corresponding to the most recent `n_weeks` unique dates.

    :param df: Input DataFrame containing a 'date' column.
    :type df: pandas.DataFrame

    :param n_weeks: Number of most recent unique weeks (dates) to retain.
    :type n_weeks: int

    :return: Filtered DataFrame containing only rows from the most recent `n_weeks` unique dates.
    :rtype: pandas.DataFrame
    """

    filt = df['date'].unique()[-n_weeks:]
    return df[df['date'].isin(filt)]


def drop_na(df):
    """
    Drop rows with NaN values from the DataFrame.

    :param df: Input DataFrame.
    :type df: pandas.DataFrame

    :return: DataFrame with NaN values dropped.
    :rtype: pandas.DataFrame
    """
    return df.dropna()


def float_to_int(df, column_name: str = 'value'):
    """
    Convert the 'value' column of the DataFrame to integers.

    :param df: Input DataFrame.
    :type df: pandas.DataFrame

    :return: DataFrame with 'value' column converted to integers.
    :rtype: pandas.DataFrame
    """
    df[column_name] = df[column_name].astype(int)
    return df


def pivot_data(df, data_type: str):
    """
    Pivot the DataFrame for a specific type.

    :param df: Input DataFrame.
    :type df: pandas.DataFrame

    :param data_type: Type of data to pivot (e.g., 'prison', 'operational_capacity', 'hdc').
    :type data_type: str

    :return: Pivoted DataFrame.
    :rtype: pandas.DataFrame
    """
    # Pivot the DataFrame
    df_query = (
        df
        .query(f"type == '{data_type}'")
        .pivot(index=['group'], columns=['date'], values='value')
        .sort_index(ascending=False, axis=1)
        )
    return df_query.sort_values(by=df_query.columns[0], ascending=False)


def main():
    """
    Main function to load, filter, and process the data.
    """
    # Load the data
    df = (
        load_data()
        .pipe(filter_n_weeks, n_weeks=2)
        .pipe(drop_na)
        .pipe(float_to_int)
        )

    # Pivot the DataFrame for each type
    prison_df = pivot_data(df, 'prison')
    operational_capacity_df = pivot_data(df, 'operational_capacity')
    hdc_df = pivot_data(df, 'hdc')

    return prison_df, operational_capacity_df, hdc_df


if __name__ == "__main__":
    # Run the main function
    prison, operational_capacity, hdc = main()

    # Print the results
    print("Prison population:")
    print(prison)
    print("\nOperational Capacity:")
    print(operational_capacity)
    print("\nHDC caseload:")
    print(hdc)
