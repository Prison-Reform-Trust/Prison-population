#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Hello world for testing Plotly Dash"""


from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

# Initialise the App 
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Create app components
markdown = dcc.Markdown(children='New title', style={'textAlign': 'left', 'color': 'red'})
button = html.Button(children="Button")
checklist = dcc.Checklist(options=['New York City', 'Montréal', 'San Francisco'])
radio = dcc.RadioItems(options=['New York City', 'Montréal', 'San Francisco'])
dropdown = dcc.Dropdown(options=['NYC', 'MTL', 'SF'], value='MTL')
slider = dcc.Slider(min=0, max=10, step=1)

# App Layout 
app.layout = dbc.Container([
    markdown,
    button,
    checklist,
    radio,
    dropdown,
    slider
])


if __name__ == '__main__':
    app.run(debug=True)
