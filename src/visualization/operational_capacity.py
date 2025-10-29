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


def main():
    """Creates chart showing the operational capacity of prisons in England and Wales."""

    y_offset_dict = {
        "2023": 400,
    }

    utils.generate_and_save_chart(
        group="total",
        category="operational_capacity",
        start_year=2021,
        chart_title="<b>Operational capacity in England and Wales</b>",
        y_label="Prison places",
        filename="operational_capacity",
        yaxis_range=(75900, 90100),
        y_offset_dict=y_offset_dict
    )
    return None


if __name__ == "__main__":
    main()
