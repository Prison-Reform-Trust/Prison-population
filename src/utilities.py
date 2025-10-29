#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script provides useful funcs to all other scripts
"""
import logging
import os
import textwrap

import chart_studio.plotly as py  # Online plotting
import pandas as pd
import plotly.graph_objs as go  # Offline plotting
import plotly.io as pio
import yaml

import src.visualization.prt_theme as prt_theme


def read_config():
    """Read in config file"""
    config = {k: v for d in yaml.load(
        open('config.yaml', encoding='utf-8'),
        Loader=yaml.SafeLoader) for k, v in d.items()}
    return config


CONFIG = read_config()


def ensure_directory(path: str) -> None:
    """Ensure a directory path exists."""
    os.makedirs(path, exist_ok=True)


def setup_logging(
        to_file=None,
        filename="download_log.log",
        log_path=CONFIG['data']['logsPath']
        ) -> None:
    """Sets up logging configuration."""
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Remove all handlers if they exist (to avoid duplicate logs)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Always add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)

    # Add file handler if requested
    if to_file:
        ensure_directory(log_path)
        file_handler = logging.FileHandler(os.path.join(log_path, filename), mode="a")
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)


def load_data(filepath: str) -> pd.DataFrame:
    """Loads processed data from CSV."""
    return pd.read_csv(filepath, parse_dates=["date"])


def _validate_required_columns(df: pd.DataFrame) -> None:
    """Private helper function to validate required columns exist in dataframe.

    Parameters:
        df (pd.DataFrame): The input dataframe to validate.

    Raises:
        KeyError: If required columns are missing from the dataframe.
    """
    required_columns = ["group", "type", "date"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise KeyError(f"Missing required columns: {missing_columns}")


def get_filter_options(df: pd.DataFrame) -> dict:
    """Returns available filter options for the dataset.
    Parameters:
        df (pd.DataFrame): The input dataframe.
    Returns:
        dict: Dictionary containing valid groups, categories, and date range.
    Raises:
        KeyError: If required columns are missing from the dataframe.
    """
    _validate_required_columns(df)

    return {
        "groups": sorted(df["group"].unique().tolist()),
        "categories": sorted(df["type"].unique().tolist()),
        "date_range": (df["date"].dt.year.min(), df["date"].dt.year.max())
    }


def filter_data(df: pd.DataFrame, group: str, category: str, date: int) -> pd.DataFrame:
    """Filters dataset based on predefined conditions.
    Parameters:
        df (pd.DataFrame): The input dataframe.
        group (str): The group to filter by (e.g., 'total', 'female').
        category (str): The category to filter by (e.g., 'prison', 'hdc').
        date (int): The year threshold to filter from (e.g., 2021). Only data from this year onwards will be included.
    Returns:
        pd.DataFrame: The filtered dataframe.
    Raises:
        ValueError: If invalid parameters are provided or if no data matches the criteria.
        KeyError: If required columns are missing from the dataframe.
    """
    # Validate required columns exist (this also validates columns for get_filter_options)
    _validate_required_columns(df)

    # Get valid options using helper function (no need to validate columns again)
    options = get_filter_options(df)

    # Validate group parameter
    if group not in options["groups"]:
        raise ValueError(f"Invalid group '{group}'. Valid options: {options['groups']}")

    # Validate category parameter
    if category not in options["categories"]:
        raise ValueError(f"Invalid category '{category}'. Valid options: {options['categories']}")

    # Validate date parameter
    min_year, max_year = options["date_range"]
    if not isinstance(date, int) or date < min_year or date > max_year:
        raise ValueError(f"Invalid date '{date}'. Must be an integer between {min_year} and {max_year}")

    # Apply filters
    df_filtered = df[
        (df["group"] == group) &
        (df["type"] == category) &
        (df["date"].dt.year >= date)
    ].copy()

    # Check if filtering resulted in empty dataframe
    if df_filtered.empty:
        logging.warning("No data found for group='%s', category='%s', date>=%s", group, category, date)
        logging.info("Available combinations:")
        combinations = df.groupby(["group", "type"])["date"].agg(["min", "max"]).reset_index()
        combinations["min_year"] = pd.to_datetime(combinations["min"]).dt.year
        combinations["max_year"] = pd.to_datetime(combinations["max"]).dt.year
        for _, row in combinations.iterrows():
            logging.info(
                "  group='%s', type='%s', years=%s-%s",
                row['group'], row['type'], row['min_year'], row['max_year']
            )

    return df_filtered


def calculate_week_and_ticks(df: pd.DataFrame) -> tuple:
    """Calculates relative week numbers and month tick positions."""

    # Ensure we are working with datetime
    df["date"] = pd.to_datetime(df["date"])

    # Calculate week number relative to each year's January 1
    df["week"] = (df["date"] - df["date"].dt.year.astype(str).apply(lambda y: pd.Timestamp(f"{y}-01-01"))).dt.days // 7 + 1

    df["month"] = df["date"].dt.month
    df["year"] = df["date"].dt.year  # Add year column for grouping

    # Get first week number for each month
    month_weeks = df.groupby("month")["week"].first().tolist()

    # Get unique month names
    month_labels = df["date"].dt.strftime("%b").unique().tolist()

    return df, month_weeks, month_labels


def load_and_process_data(group: str, category: str, date: int) -> tuple[pd.DataFrame, list[int], list[str]]:
    """Loads data and applies filtering and week calculations, ready for plotting.
    Parameters:
        group (str): The group to filter by (e.g., 'total', 'female').
        category (str): The category to filter by (e.g., 'prison', 'hdc').
        date (int): The year threshold to filter from (e.g., 2021). Only data from this year onwards will be included.
    Returns:
        tuple: (df_with_weeks, month_tick_positions, month_tick_labels)
            - df_with_weeks (pd.DataFrame): Filtered dataframe with week numbers.
            - month_tick_positions (list): List of week numbers for month ticks.
            - month_tick_labels (list): List of month labels corresponding to tick positions.
    """
    data_path = os.path.join(CONFIG['data']['clnFilePath'], 'processed_data.csv')
    df_raw = load_data(data_path)

    # Filter by group, category, and date
    df_filtered_by_criteria = filter_data(df_raw, group, category, date)

    # Calculate week numbers and tick positions
    df_with_weeks, month_tick_positions, month_tick_labels = calculate_week_and_ticks(df_filtered_by_criteria)

    return df_with_weeks, month_tick_positions, month_tick_labels


def generate_traces(df: pd.DataFrame) -> list:
    """Generates Plotly traces for each year in dataset."""
    traces = [
        go.Scatter(
            x=df_year["week"],
            y=df_year["value"],
            mode="lines",
            connectgaps=True,
            hovertext=df_year["date"].dt.strftime("%d %b"),
            hovertemplate="<b>%{hovertext}</b><br>%{y:,.0f}",
            name=str(year),
        )
        for year, df_year in df.groupby(df["date"].dt.year)
    ]
    return traces


def generate_annotations(traces, colorway, y_label, y_offset_dict=None):
    """
    Generates trace labels and source annotation, allowing individual y-value adjustments.

    Parameters:
        traces (list): Plotly trace objects.
        colorway (list): Color scheme from Plotly template.
        y_label (str): Y-axis label text.
        y_offset_dict (dict, optional): A dictionary mapping trace names (years) to y-offsets.
    """
    if y_offset_dict is None:
        y_offset_dict = {}

    annotations = [
        dict(
            xref="x",
            yref="y",
            x=53 if i < 4 else trace.x[-1],  # First 4 use fixed x, others use last x position
            y=trace.y[-1] + y_offset_dict.get(trace.name, 0),  # Apply y-offset if available
            text=trace.name,
            xanchor="left",
            align="left",
            showarrow=False,
            font_color=colorway[i],
            font_size=10,
        )
        for i, trace in enumerate(traces)
    ]

    # Add source label
    annotations.append(
        dict(
            xref="paper",
            yref="paper",
            x=-0.08,
            y=-0.19,
            align="left",
            showarrow=False,
            text="<b>Source: Ministry of Justice Prison Population Bulletin</b>",
            font_size=12,
        )
    )

    # Add y-axis label
    annotations.append(
        dict(
            xref="x",
            yref="paper",
            x=1,
            y=1.04,
            align="left",
            xanchor="left",
            showarrow=False,
            text=y_label,
            font_size=12,
        )
    )

    return annotations


def create_chart_figure(
    xaxis_tickvals,
    xaxis_ticktext,
    traces,
    title: str,
    y_label: str,
    yaxis_range: tuple,
    margin=None,
    yaxis_dtick=None,
    xaxis_range_vals=(1, 53),
    xaxis_nticks=None,
    yaxis_nticks=6,
    y_offset_dict=None,
) -> go.Figure:
    """
    Creates a Plotly figure from processed data components.

    This function handles only the chart creation - it takes already
    processed data (traces, tick values) and creates the visual chart.

    Parameters:
        xaxis_tickvals: X-axis tick positions
        xaxis_ticktext: X-axis tick labels
        traces: Plotly trace objects
        title (str): Chart title
        y_label (str): Y-axis label
        yaxis_range (tuple): Y-axis range (min, max)
        margin (dict, optional): Chart margins
        yaxis_dtick (int, optional): Y-axis tick interval
        xaxis_range_vals (tuple, optional): X-axis range, defaults to (1, 53)
        xaxis_nticks (int, optional): Number of x-axis ticks
        yaxis_nticks (int, optional): Number of y-axis ticks, defaults to 6
        y_offset_dict (dict, optional): Year-specific y-offset adjustments for labels

    Returns:
        go.Figure: The created Plotly figure
    """

    fig = go.Figure(traces)

    # Wrap title for better formatting
    chart_title = textwrap.wrap(title, width=65)

    # Get colorway from template
    colorway = pio.templates[pio.templates.default].layout.colorway

    # Generate annotations with optional y_offset_dict
    annotations = generate_annotations(traces, colorway, y_label, y_offset_dict)

    fig.update_layout(
        margin=margin if margin else dict(l=64, b=75, r=64, pad=10),
        title="<br>".join(chart_title),
        yaxis_dtick=yaxis_dtick if yaxis_dtick else 2000,
        xaxis_tickvals=xaxis_tickvals,
        xaxis_ticktext=xaxis_ticktext,
        hovermode='x',
        annotations=annotations,
    )

    # Apply axis settings
    fig.update_yaxes(range=yaxis_range, nticks=yaxis_nticks)
    fig.update_xaxes(range=xaxis_range_vals, nticks=xaxis_nticks)

    return fig


def save_chart(fig, filename):
    """Saves the chart as an image and uploads it online."""

    fig.write_image(os.path.join(CONFIG['viz']['outPath'], f'{filename}.svg'))

    fig.layout.images = [
        dict(
            source="https://i.ibb.co/jhfYbyc/PRTlogo-RGB.png",
            xref="paper",
            yref="paper",
            x=-0.08,
            y=1.25,
            sizex=0.15,
            sizey=0.15,
            xanchor="left",
            yanchor="top",
        )
    ]

    layout_atr = prt_theme.pio.templates["prt_template"].layout
    fig.update_layout(
        width=layout_atr.width,
        height=layout_atr.height,
    )

    py.plot(fig, filename=filename)