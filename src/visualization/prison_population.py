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

##Adding plotly credentials
chart_studio.tools.set_credentials_file(
    username=os.getenv("PLOTLY_USERNAME"), api_key=os.getenv("PLOTLY_API_KEY")
)

##Setting template
pio.templates.default = "prt_template"
plotly_config = config['plotly']['config']

##Reading in data
df = pd.read_csv(
    f"{config['data']['clnFilePath']}prison_population.csv",
    usecols=["date", "population"],
    parse_dates=["date"],
)

##Filtering year range
year = "2019"
mask = df["date"].dt.year >= int(year)
df_include = df[mask]

##Calculating xaxis_tickvals
start = datetime.datetime(2021, 1, 1)
end = datetime.datetime(2021, 12, 31)

xtick_vals = pd.date_range(start, end)
filt = xtick_vals.is_month_start

month_weeks = xtick_vals[filt].isocalendar().week
month_weeks.iloc[0] = 1  # preventing week 1 from starting at the end of previous year

## Chart title
title = textwrap.wrap("<b>Prison population in England and Wales</b>", width=65)

##Plotting

fig = go.Figure()

trace_list = []
for year in df_include["date"].dt.year.unique():
    df_year = df_include[df_include["date"].dt.year == year]

    trace = go.Scatter(
        x=df_year["date"].dt.strftime("Week %U"),
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
    title="<br>".join(title),
    yaxis_dtick=2000,
    xaxis_tickvals=month_weeks,
    xaxis_ticktext=xtick_vals[filt].strftime("%b"),
)

## Chart annotations
annotations = []

y_list = [0, 0, 0, 0, 0]

# Adding trace annotations
for i in range(0, len(trace_list)):
    annotations.append(
        dict(
            xref="x",
            yref="y",
            x=trace_list[i].x[-1],
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
        x="Week 00",
        y=1.04,
        align="left",
        xanchor="left",
        showarrow=False,
        text="People in prison",
        font_size=12,
    )
)

# Adding annotations to layout
fig.update_layout(annotations=annotations)

fig.update_yaxes(range=[75900, 90100], nticks=6)
fig.update_xaxes(range=[-1, 52])

##Plot file offline
fig.show(config=plotly_config, renderer='browser')

"""
Outputting image and online charts
"""

##Image
# fig.write_image(os.path.join(config['viz']['outPath'], 'prison_population.eps'))
fig.write_image(os.path.join(config['viz']['outPath'], 'prison_population.svg'))

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

py.plot(fig, filename="Weekly prison population E&W")