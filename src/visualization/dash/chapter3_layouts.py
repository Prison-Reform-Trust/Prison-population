#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Hello world for testing Plotly Dash"""


from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

# Initialise the App 
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Create app components
title = dcc.Markdown(children='Dash layouts', style={'textAlign': 'center', 'font-weight': 'bold'})
sub_title = dcc.Markdown(children='Please select some options', style={'textAlign': 'left'})
button = html.Button(children="Button")
checklist = dcc.Checklist(options=['New York City', 'Montréal', 'San Francisco'])
radio = dcc.RadioItems(options=['New York City', 'Montréal', 'San Francisco'])
dropdown = dcc.Dropdown(options=['NYC', 'MTL', 'SF'], value='MTL')
slider = dcc.Slider(min=0, max=10, step=1)

# App Layout
app.layout = dbc.Container([
    dbc.Row([dbc.Col([title], width=12)]),  # Never assign more than 12 columns within each Row.
    dbc.Row([dbc.Col([sub_title], width=12)]),
    dbc.Row(
        [
            dbc.Col([dropdown], width=4),
            dbc.Col([slider], width=8)
        ]
    ),
    dbc.Row(
        [
            dbc.Col([checklist], width=5),
            dbc.Col([radio], width=5),
            dbc.Col([button], width=2)
        ]
    ),
    # dbc.Row([dbc.Col([button], width=11)]),
])


if __name__ == '__main__':
    app.run(debug=True)
