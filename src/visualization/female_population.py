#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Imports
import os

import chart_studio.tools
import plotly.io as pio
from dotenv import find_dotenv, load_dotenv

# Local scripts
import src.utilities as utils

# Load environment variables and config
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
config = utils.read_config()

# Set Plotly credentials
chart_studio.tools.set_credentials_file(
    username=os.getenv("PLOTLY_USERNAME"), api_key=os.getenv("PLOTLY_API_KEY")
)

# Set template
pio.templates.default = "prt_template"


def main(
        chart_title="<b>Female prison population in England and Wales</b>",
        y_label="Women in prison",
        filename="female_prison_population"
        ):
    df = utils.load_data(f"{config['data']['clnFilePath']}processed_data.csv")
    df_filtered = utils.filter_data(df, "female", "prison", 2021)
    df_final, xaxis_tickvals, xaxis_ticktext = utils.calculate_week_and_ticks(df_filtered)
    traces = utils.generate_traces(df_final)
    fig = utils.create_chart(df_final, xaxis_tickvals, xaxis_ticktext, traces, chart_title, y_label, yaxis_dtick=200, xaxis_range=(2795, 4010))
    utils.save_chart(fig, filename)

    return None


# Run script
if __name__ == "__main__":
    main()
