#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This script generates a chart visualizing the operational capacity of prisons in England and Wales.
'''
# Imports
import plotly.io as pio

import src.utilities as utils

# Set template
pio.templates.default = "prt_template"

# Constants
TITLE = "Operational capacity in England and Wales"
FILENAME = "operational_capacity"


def main():
    """Creates chart showing the operational capacity of prisons in England and Wales."""

    y_offset_dict = {
        "2023": 400,
        "2025": 600,
    }

    fig = utils.generate_chart(
        group="total",
        category="operational_capacity",
        start_year=2022,
        chart_title=f"<b>{TITLE}</b>",
        y_label="Prison places",
        yaxis_range=(75900, 92100),
        y_offset_dict=y_offset_dict
    )

    utils.save_chart(
        fig,
        filename=FILENAME,
    )

    utils.save_plotly_chart_as_html(
        fig,
        filename=FILENAME,
    )
    return None


if __name__ == "__main__":
    main()
