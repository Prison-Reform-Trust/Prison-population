#Custom plotly template for all charts in this project

import plotly.io as pio
import plotly.graph_objs as go

#PRT standard template
pio.templates["prt_template"] = go.layout.Template(
    layout=go.Layout(
        # Default parameters
        title_font=dict(family="Helvetica Neue, Arial", size=17),
        title_y=0.94,
        title_yanchor="bottom",
        font_color="#54565B",
        font_family="Helvetica Neue, Arial",
        font_size=12,
        paper_bgcolor="#F7F2F2",
        plot_bgcolor="#F7F2F2",
        colorway=("#A01D28", "#499CC9", "#F9A237", "#6FBA3A", "#573D6B"),
        modebar_activecolor="#A01D28",
        showlegend=False,
        yaxis_title="",
        xaxis_showgrid=False,
        xaxis_tickcolor="#54565B",
        width=655,
        height=500,
        autosize=False,
        margin=dict(l=60, b=75),
        hovermode="x unified",
        yaxis_tickformat=",.0f",
    )
)
## Chart annotations
def sourceAnnotation(source, annotations_list):
    annotations_list.append(
        dict(
            xref="paper",
            yref="paper",
            xanchor="left",
            yanchor="top",
            x=-0.08,
            y=-0.19,
            showarrow=False,
            text=f"Source: {source}",
            font_size=12,
        )
    )