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


def main():
    """Creates chart showing the HDC population in England and Wales."""

    y_offset_dict = {
        "2021": 200,
    }

    utils.generate_and_save_chart(
        group="total",
        category="hdc",
        start_year=2021,
        chart_title="<b>HDC population in England and Wales</b>",
        y_label="People on Home Detention Curfew",
        filename="HDC_population",
        yaxis_range=(1490, 4510),
        yaxis_dtick=500,
        y_offset_dict=y_offset_dict
    )
    return None


if __name__ == "__main__":
    main()
