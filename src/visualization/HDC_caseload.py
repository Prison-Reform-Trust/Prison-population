#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This script generates a chart visualizing the Home Detention Curfew (HDC) population in England and Wales.
'''

# Imports
import plotly.io as pio

import src.utilities as utils

# Set template
pio.templates.default = "prt_template"

# Constants
TITLE = "HDC population in England and Wales"
FILENAME = "HDC_population"


def main():
    """Creates chart showing the HDC population in England and Wales."""

    y_offset_dict = {
        "2021": 200,
    }

    fig = utils.generate_chart(
        group="total",
        category="hdc",
        start_year=2021,
        chart_title=f"<b>{TITLE}</b>",
        y_label="People on Home Detention Curfew",
        yaxis_range=(1490, 4510),
        yaxis_dtick=500,
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
