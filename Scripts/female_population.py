#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 12:16:25 2022

@author: alex
"""

##Importing libaries
import os
import plotly.graph_objs as go  # Offline plotting
import chart_studio.plotly as py  # Online plotting
import chart_studio
import plotly.io as pio
import pandas as pd
import datetime
import textwrap

##Importing environment variables with dotenv
from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

##Adding plot.ly credentials
chart_studio.tools.set_credentials_file(
    username=os.getenv("PLOTLY_USERNAME"), api_key=os.getenv("PLOTLY_API_KEY")
)

##Loading and setting templates
pio.templates
prt_template = go.layout.Template(
    layout=go.Layout(
        title_font=dict(family="Helvetica Neue, Arial", size=17),
        font_color="#54565B",
        font_family="Helvetica Neue, Arial",
        font_size=12,
        paper_bgcolor="#FBFAF7",
        plot_bgcolor="#FBFAF7",
        colorway=("#A01D28", "#499CC9", "#F9A237", "#6FBA3A", "#573D6B"),
    )
)

config = dict(
    {
        "scrollZoom": False,
        "displayModeBar": False,
        "editable": False,
        "displaylogo": False,
        "showAxisDragHandles": False,
    }
)

##Reading in data
df = pd.read_csv(
    "../Data/female_population.csv",
    usecols=["date", "population"],
    parse_dates=["date"],
)

##Filtering year range
year = "2018"
mask = df["date"].dt.year >= int(year)
df_include = df[mask]

##Calculating xaxis_tickvals
start = datetime.datetime(2021, 1, 1)
end = datetime.datetime(2021, 12, 31)

xtick_vals = pd.date_range(start, end)
filt = xtick_vals.is_month_start

month_weeks = xtick_vals[filt].isocalendar().week
month_weeks[0] = 1  # preventing week 1 from starting at the end of previous year

## Chart title
title = textwrap.wrap("<b>Female prison population in England and Wales</b>", width=65)

##Plotting

fig = go.Figure()

trace_list = []
for year in df_include["date"].dt.year.unique():
    df_year = df_include[df_include["date"].dt.year == year]

    trace = go.Scatter(
        #         x=df_year["date"].dt.isocalendar().week,
        x=df_year["date"].dt.strftime("Week %U"),
        #         x=df_year["date"],
        y=df_year["population"],
        mode="lines",
        connectgaps=True,
        hovertext=df["date"].dt.strftime(" "),
        hovertemplate="<b>%{hovertext}</b><br>" + "%{y:,.0f}",
        name=str(year),
    )

    trace_list.append(trace)

fig.add_traces(trace_list)


##Edit the layout

fig.update_layout(
    margin=dict(l=60, b=75),
    title="<br>".join(title),
    title_y=0.94,
    title_yanchor="bottom",
    yaxis_title="",
    yaxis_tickformat=",.0f",
    xaxis_showgrid=False,
    xaxis_tickvals=month_weeks,
    xaxis_ticktext=xtick_vals[filt].strftime("%b"),
    xaxis_tickcolor="#54565B",
    template=prt_template,
    showlegend=False,
    hovermode="x unified",
    modebar_activecolor="#A12833",
    width=655,
    height=500,
)

## Chart annotations
annotations = []

y_list = [0, -25, -45, 0, -80]

# Adding trace annotations
for i in range(0, len(trace_list)):
    annotations.append(
        dict(
            xref="x",
            yref="y",
            x=trace_list[i].x[-1],
            y=trace_list[i].y[-2] + y_list[i],
            text=str(trace_list[i].name),
            xanchor="left",
            align="left",
            showarrow=False,
            font_color=prt_template.layout.colorway[i],
            font_size=10,
        )
    )

# Adding source label
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

# Adding y-axis label
annotations.append(
    dict(
        xref="x",
        yref="paper",
        x="Week 00",
        y=1.04,
        align="left",
        xanchor="left",
        showarrow=False,
        text="Women in prison",
        font_size=12,
    )
)

# Adding annotations to layout
fig.update_layout(annotations=annotations)

fig.update_yaxes(range=[2990, 4210], nticks=10)
fig.update_xaxes(range=[-1, 52])

##Plot file offline
fig.show(config=config)

"""
Outputting image and online charts
"""

##Image
fig.write_image(
    "../images/female_prison_population.png", width=655, height=500, scale=2
)

##Online

# PRT logo
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

py.plot(fig, filename="Female prison population E&W", auto_open=True)
