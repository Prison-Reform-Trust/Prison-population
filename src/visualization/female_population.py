#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Imports
import plotly.io as pio

import src.utilities as utils

# Set template
pio.templates.default = "prt_template"


def main():
    """Creates chart showing the female prison population in England and Wales."""
    utils.generate_and_save_chart(
        group="female",
        category="prison",
        start_year=2021,
        chart_title="<b>Female prison population in England and Wales</b>",
        y_label="Women in prison",
        filename="female_prison_population",
        yaxis_range=(2795, 4010),
        yaxis_dtick=200
    )
    return None


if __name__ == "__main__":
    main()
