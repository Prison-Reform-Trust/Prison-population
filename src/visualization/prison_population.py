#!/usr/bin/env python3
# -*- coding: utf-8 -*-

## Imports
import os
import plotly.graph_objs as go  # Offline plotting
import chart_studio.plotly as py  # Online plotting
import chart_studio.tools
import plotly.io as pio
import pandas as pd
import datetime
import textwrap
from dotenv import load_dotenv, find_dotenv

# Local scripts
import src.data.utilities as utils
import src.visualization.prt_theme as prt_theme

## Load environment variables and config
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
config = utils.read_config()

## Set Plotly credentials
chart_studio.tools.set_credentials_file(
    username=os.getenv("PLOTLY_USERNAME"), api_key=os.getenv("PLOTLY_API_KEY")
)

## Set template
pio.templates.default = "prt_template"
plotly_config = config['plotly']['config']

## Read data
def load_data(filepath):
    """Loads processed data from CSV."""
    return pd.read_csv(filepath, parse_dates=["date"])

## Filter dataset
def filter_data(df):
    """Filters dataset based on predefined conditions."""
    df_filtered = df[
        (df["group"] == "total") &
        (df["type"] == "prison") &
        (df["date"].dt.year >= 2021)
    ].copy() # Filter for total prison population since 2021
    return df_filtered

## Calculate week numbers & month ticks
def calculate_week_and_ticks(df):
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

## Generate traces for Plotly
def generate_traces(df):
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

## Generate annotations dynamically
def generate_annotations(traces, colorway):
    """Generates trace labels and source annotation."""
    annotations = [
        dict(
            xref="x",
            yref="y",
            x=53 if i < 4 else trace.x[-1],  # First 4 use fixed x, others use last x position
            y=trace.y[-1],
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
            text="People in prison",
            font_size=12,
        )
    )

    return annotations

## Main function to create chart
def create_chart(df, xaxis_tickvals, xaxis_ticktext, traces):
    """Creates the Plotly chart with all elements."""
    fig = go.Figure(traces)

    title = textwrap.wrap("<b>Prison population in England and Wales</b>", width=65)

    # Get colorway from template
    colorway = pio.templates[pio.templates.default].layout.colorway

    fig.update_layout(
        margin=dict(l=64, b=75, r=64, pad=10),
        title="<br>".join(title),
        yaxis_dtick=2000,
        xaxis_tickvals=xaxis_tickvals,
        xaxis_ticktext=xaxis_ticktext,
        hovermode='x',
        annotations=generate_annotations(traces, colorway),  # Pass colorway
    )

    fig.update_yaxes(range=[75900, 90100], nticks=6)
    fig.update_xaxes(range=[1, 53])

    return fig

## Save chart (offline and online)
def save_chart(fig):
    """Saves the chart as an image and uploads it online."""
    fig.write_image(os.path.join(config['viz']['outPath'], 'prison_population.svg'))

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

    py.plot(fig, filename="Weekly prison population E&W")

## Run script
if __name__ == "__main__":
    df = load_data(f"{config['data']['clnFilePath']}processed_data.csv")
    df_filtered = filter_data(df)
    df_final, xaxis_tickvals, xaxis_ticktext = calculate_week_and_ticks(df_filtered)
    traces = generate_traces(df_final)
    fig = create_chart(df_final, xaxis_tickvals, xaxis_ticktext, traces)

    fig.show(config=plotly_config, renderer='browser')
    save_chart(fig)