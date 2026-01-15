#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Imports
import plotly.io as pio

import src.utilities as utils

# Set template
pio.templates.default = "prt_template"

# Constants
TITLE = "Female prison population in England and Wales"
FILENAME = "female_prison_population"


def main():
    """Creates chart showing the female prison population in England and Wales."""

    y_offset_dict = {
        "2025": -40,
    }

    fig = utils.generate_chart(
        group="female",
        category="prison",
        start_year=2022,
        chart_title=f"<b>{TITLE}</b>",
        y_label="Women in prison",
        yaxis_range=(2795, 4010),
        yaxis_dtick=200,
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
