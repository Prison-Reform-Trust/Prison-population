#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Imports
import plotly.io as pio

import src.utilities as utils

# Set template
pio.templates.default = "prt_template"


def main():
    """Creates chart showing the prison population in England and Wales."""
    utils.generate_and_save_chart(
        group="total",
        category="prison",
        start_year=2021,
        chart_title="<b>Prison population in England and Wales</b>",
        y_label="People in prison",
        filename="prison_population",
        yaxis_range=(75900, 90100)
    )
    return None


if __name__ == "__main__":
    main()
