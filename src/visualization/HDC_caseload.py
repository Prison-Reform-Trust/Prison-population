#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##Imports 

#Libraries
import os
import plotly.graph_objs as go  # Offline plotting
import chart_studio.plotly as py  # Online plotting
import chart_studio
import plotly.io as pio
import pandas as pd
import datetime
import textwrap
from dotenv import load_dotenv, find_dotenv

#Local scripts
import src.data.utilities as utils
import src.visualization.prt_theme as prt_theme

##Loading environment variables and config
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
config = utils.read_config()

##Adding plot.ly credentials
chart_studio.tools.set_credentials_file(
    username=os.getenv("PLOTLY_USERNAME"), api_key=os.getenv("PLOTLY_API_KEY")
)

##Setting template
pio.templates.default = "prt_template"
plotly_config = config['plotly']['config']

##Reading in data
df = pd.read_csv(
    f"{config['data']['clnFilePath']}/HDC.csv", 
    usecols=["date", "hdc_pop"], 
    parse_dates=["date"], 
    thousands=","
)

##Filtering year range
df_include = df.query('date.dt.year >= 2020 & date.dt.year <= 2024')

##Calculating xaxis_tickvals
start = datetime.datetime(2018, 1, 1)
end = datetime.datetime(2018, 12, 31)

xtick_vals = pd.date_range(start, end)
filt = xtick_vals.is_month_start

month_weeks = xtick_vals[filt].isocalendar().week

## Chart title
title = textwrap.wrap("<b>HDC population in England and Wales</b>", width=65)

##Plotting

fig = go.Figure()

trace_list = []
for year in df_include["date"].dt.year.unique():
    df_year = df_include[df_include["date"].dt.year == year]

    trace = go.Scatter(
        x=df_year["date"].dt.isocalendar().week,
        y=df_year["hdc_pop"],
        mode="lines",
        connectgaps=True,
        hovertext=df_year["date"].dt.strftime("%d %b"),
        hovertemplate="<b>%{hovertext}</b><br>" + "%{y:,.0f}",
        name=str(year),
    )

    trace_list.append(trace)

fig.add_traces(trace_list)

##Automatically adjust the colours used from the template based on the length of the trace list
fig.layout.template.layout.colorway = fig.layout.template.layout.colorway[-len(trace_list):]


##Edit the layout

fig.update_layout(
    margin=dict(l=64, b=75, r=64, pad=10),
    title="<br>".join(title),
    xaxis_tickvals=month_weeks,
    xaxis_ticktext=xtick_vals[filt].strftime("%b"),
    hovermode='x'
)

## Chart annotations
annotations = []

y_list = [0, -130, 0, 0, 0]

# Adding trace annotations
for i in range(0, len(trace_list)):
    if i < 4:
        # For the first four traces, use a fixed x position
        x_position = 52
    else:
        # For the current year's trace, use the last x value position
        x_position = trace_list[i].x[-1]

    annotations.append(
        dict(
            xref="x",
            yref="y",
            x=x_position,
            y=trace_list[i].y[-1] + y_list[i],
            text=str(trace_list[i].name),
            xanchor="left",
            align="left",
            showarrow=False,
            font_color=fig.layout.template.layout.colorway[i],
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
        x=1,
        y=1.04,
        align="left",
        xanchor="left",
        showarrow=False,
        text="Number of people on HDC",
        font_size=12,
    )
)

# Adding annotations to layout
fig.update_layout(annotations=annotations)

fig.update_yaxes(range=[0, 4050])
fig.update_xaxes(range=[1, 52])

##Plot file offline
fig.show(config=plotly_config, renderer='browser')

"""
Outputting image and online charts
"""

##Image
# fig.write_image(os.path.join(config['viz']['outPath'], 'HDC_population.eps'))
fig.write_image(os.path.join(config['viz']['outPath'], 'HDC_population.svg'))

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

# Restating explicit width and height values from the template to prevent responsive
# resizing of chart on upload to Chart Studio. This only affects CS uploads.

layout_atr = prt_theme.pio.templates["prt_template"].layout

fig.update_layout(
    width=layout_atr.width,
    height=layout_atr.height,
)

# py.plot(fig, filename="HDC population E&W")