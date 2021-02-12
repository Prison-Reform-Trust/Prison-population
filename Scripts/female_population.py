#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 17:41:55 2020

@author: Alex
"""

##Importing libaries
import os
import plotly.graph_objs as go  # Offline plotting
import chart_studio.plotly as py  # Online plotting
import chart_studio
import plotly.io as pio
import pandas as pd
import datetime
import calendar

##Importing environment variables with dotenv
from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

##Adding plot.ly credentials
chart_studio.tools.set_credentials_file(
    username=os.getenv("PLOTLY_USERNAME"), api_key=os.getenv("PLOTLY_API_KEY")
)

##Setting plotly renderer
pio.renderers.default = "browser"

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
        colorway=("#A01D28", "#499CC9", "#F9A237", "#6FBA3A"),
    )
)

##Reading in data
df = pd.read_csv(
    "../Data/female_population.csv",
    usecols=["date", "population"],
    index_col=["date"],
    parse_dates=["date"],
)

df["year"] = df.index.year
df["week"] = df.index.isocalendar().week
df["month"] = df.index.month

df["month"] = df["month"].apply(lambda x: calendar.month_abbr[x])

weeks = 52 / 12.0
months = [datetime.date(2021, m, 1).strftime("%b") for m in range(1, 13)]


##Plotting

fig = go.Figure()

for year in df["year"]["2018":"2021"].unique():
    df_year = df[df["year"] == year]

    fig.add_trace(
        go.Scatter(
            x=df_year["week"],
            y=df_year["population"],
            mode="lines",
            connectgaps=True,
            hovertext=df["month"],
            hovertemplate="<b>%{hovertext}</b><br>" + "%{y:,.0f}",
            name=str(year),
        )
    )


##Edit the layout

fig.update_layout(
    title="<b>Female prison population in England and Wales</b>",
    yaxis_title="Women in prison",
    yaxis_tickformat=",.0f",
    xaxis_showgrid=False,
    xaxis_tickmode="array",
    xaxis_tickvals=[(2 * k - 1) * weeks / 2 for k in range(1, 13)],
    xaxis_ticktext=months,
    xaxis_ticks="inside",
    xaxis_tickcolor="#54565B",
    template=prt_template,
    showlegend=True,
    legend=dict(yanchor="top", y=0.915),
    hovermode="x",
    modebar_activecolor="#A12833",
    width=655,
    height=500,
    annotations=[
        go.layout.Annotation(
            x=-0.08,
            y=-0.19,
            showarrow=False,
            text="<b>Source: Ministry of Justice Prison Population Bulletin\n</b>",
            font_size=12,
            xref="paper",
            yref="paper",
        )
    ],
)

fig.update_yaxes(range=[3000, 4200], nticks=10)


"""
This section outputs the final chart, with static; interactive offline; and interactive online versions.
"""

##Plot static image
fig.write_image(
    "../images/female_prison_population.png", width=655, height=500, scale=2
)

##Plot file offline
# fig.show(config={'displayModeBar': False})


##Plot file online with PRT logo

# Removing the legend

fig.update_layout(showlegend=False)

##PRT logo
fig.layout.images = [
    dict(
        source="https://i.ibb.co/jhfYbyc/PRTlogo-RGB.png",
        xref="paper",
        yref="paper",
        x=0.04,
        y=1.25,
        sizex=0.15,
        sizey=0.15,
        xanchor="right",
        yanchor="top",
    )
]

py.plot(fig, filename="Female prison population E&W", auto_open=True)
