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


# Configure logging
def setup_logging(filename="download_log.log", log_path=read_config()['data']['logsPath']):
    """Sets up logging configuration."""
    os.makedirs(log_path, exist_ok=True)  # Ensure the directory exists

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=os.path.join(log_path, filename),  # Saves logs to a file
        filemode="a"  # Appends to existing log file
    )


## Read data
def load_data(filepath: str) -> pd.DataFrame:
    """Loads processed data from CSV."""
    return pd.read_csv(filepath, parse_dates=["date"])


def filter_data(df: pd.DataFrame, group: str, category: str, date: int) -> pd.DataFrame:
    """Filters dataset based on predefined conditions."""
    df_filtered = df[
        (df["group"] == group) &
        (df["type"] == category) &
        (df["date"].dt.year >= date)
    ].copy()
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


def create_chart(
    df,
    xaxis_tickvals,
    xaxis_ticktext,
    traces,
    title: str,
    y_label: str,
    xaxis_range:tuple,
    margin=None,
    yaxis_dtick=None,
    xaxis_range_vals=(1, 53),
    xaxis_nticks=None,
    yaxis_nticks=6,
    y_offset_dict=None,
) -> go.Figure:
    """Creates the Plotly chart with adjustable parameters."""

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
    fig.update_yaxes(range=xaxis_range, nticks=yaxis_nticks)
    fig.update_xaxes(range=xaxis_range_vals, nticks=xaxis_nticks)

    return fig


def save_chart(fig, filename):
    """Saves the chart as an image and uploads it online."""
    config = read_config() # Read in config file
    fig.write_image(os.path.join(config['viz']['outPath'], f'{filename}.svg'))

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