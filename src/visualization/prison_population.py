#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Imports
import plotly.io as pio

import src.utilities as utils

# Set template
pio.templates.default = "prt_template"

# Constants
TITLE = "Prison population in England & Wales"
FILENAME = "prison_population"


def main():
    """Creates chart showing the prison population in England and Wales."""
    fig = utils.generate_chart(
        group="total",
        category="prison",
        start_year=2022,
        chart_title=f"<b>{TITLE}</b>",
        y_label="People in prison",
        yaxis_range=(75900, 90100)
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
