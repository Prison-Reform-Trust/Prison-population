#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''# This script generates a chart visualizing the Home Detention Curfew (HDC) population in England and Wales.'''

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
        chart_title="<b>HDC population in England and Wales</b>",
        y_label="People on Home Detention Curfew",
        filename="HDC_population"
        ):
    df = utils.load_data(f"{config['data']['clnFilePath']}processed_data.csv")
    df_filtered = utils.filter_data(df, "total", "hdc", 2021)
    df_final, xaxis_tickvals, xaxis_ticktext = utils.calculate_week_and_ticks(df_filtered)
    traces = utils.generate_traces(df_final)

    y_offset_dict = {
        "2021": 200,
    }

    fig = utils.create_chart(df_final, xaxis_tickvals, xaxis_ticktext, traces, chart_title, y_label, yaxis_dtick=500, xaxis_range=(1490, 4510), y_offset_dict=y_offset_dict)
    utils.save_chart(fig, filename)

    return None


# Run script
if __name__ == "__main__":
    main()
