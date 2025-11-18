# scatter_plot.py
"""
Altair-based scatter plot:
    - x-axis: observed disease cases
    - y-axis: predicted disease cases
    - points: forecasts
    - dashed line: 45-degree reference (perfect prediction)

Implemented as a Plotter subclass so it fits into a modular design.
"""

import os
from typing import Final

import pandas as pd
import altair as alt

from plotter import Plotter

# Disable default 5000-row limit (not needed here, but good practice for larger data)
alt.data_transformers.disable_max_rows()

# Centralized colors – easy to tweak if you want a different style
POINT_COLOR: Final[str] = "#ff7f0e"   # orange
LINE_COLOR: Final[str] = "#000000"    # black


class ScatterPlotter(Plotter):
    """
    Truth vs Prediction scatter plot with a 45° reference line.

    This class implements the Plotter interface and can be plugged into
    any driver that expects Plotter instances (e.g. isolated_run.py).
    """

    name: str = "scatter"

    def plot(
        self,
        forecasts: pd.DataFrame,
        observations: pd.DataFrame,
        out_path: str,
    ) -> str:
        """
        Create the scatter plot and save it as a PNG.

        Parameters
        ----------
        forecasts : pd.DataFrame
            Forecasts with columns at least: location, time_period, forecast.
        observations : pd.DataFrame
            Observations with columns at least: location, time_period, disease_cases.
        out_path : str
            Path to PNG file to write.

        Returns
        -------
        str
            The path to the written PNG.
        """

        # Merge forecasts and observations on location + time_period
        # so that each row has both predicted and observed values.
        merged = forecasts.merge(
            observations, on=["location", "time_period"], how="left"
        )

        # Make sure output directory exists
        outdir = os.path.dirname(out_path)
        if outdir:
            os.makedirs(outdir, exist_ok=True)

        # We want the 45-degree line to run from (0, 0) to (max, max)
        min_val = 0
        max_val = float(
            max(merged["disease_cases"].max(), merged["forecast"].max())
        )
        line_df = pd.DataFrame({"x": [min_val, max_val], "y": [min_val, max_val]})

        # --- Points layer (predictions) ---
        points = (
            alt.Chart(merged)
            # Add a constant 'kind' field so we can use it in the shared legend
            .transform_calculate(kind='"Prediction"')
            .mark_circle(size=120, opacity=0.9, stroke="black")
            .encode(
                x=alt.X("disease_cases:Q", title="Observed cases"),
                y=alt.Y("forecast:Q", title="Predicted cases"),
                # Use 'kind' as color dimension, but with a fixed domain and colors.
                color=alt.Color(
                    "kind:N",
                    title="Legend",
                    scale=alt.Scale(
                        domain=["Prediction", "45° reference"],
                        range=[POINT_COLOR, LINE_COLOR],
                    ),
                ),
                tooltip=["location", "time_period", "disease_cases", "forecast"],
            )
            .properties(width=600, height=450)
        )

        # --- Diagonal 45° reference line layer ---
        diagonal = (
            alt.Chart(line_df)
            .transform_calculate(kind='"45° reference"')
            .mark_line(strokeDash=[4, 3], strokeWidth=2)
            .encode(
                x="x:Q",
                y="y:Q",
                color=alt.Color(
                    "kind:N",
                    title="Legend",
                    scale=alt.Scale(
                        domain=["Prediction", "45° reference"],
                        range=[POINT_COLOR, LINE_COLOR],
                    ),
                ),
            )
        )

        # Combine both layers + configure title, legend, axes
        chart = (points + diagonal).properties(
            title="ALTIR SCATTER – Truth vs Prediction",
        ).configure_title(
            fontSize=20,
            font="Arial",
            anchor="middle",
            color="black",
        ).configure_legend(
            # Place legend on the right side of the plot
            orient="right",
            padding=20,
            cornerRadius=8,
            labelFontSize=12,
            titleFontSize=13,
        ).configure_axis(
            # Subtle grid for readability
            grid=True,
            gridOpacity=0.3,
        )

        # Save as PNG via vl-convert
        chart.save(out_path, scale_factor=2)
        print(f"[ScatterPlotter] Saved plot to: {out_path}")
        return out_path


# Optional helper: still allow the "simple function" style
def scatter_plot_from_csv(forecasts_path: str, observations_path: str, output_path: str):
    """
    Convenience wrapper around ScatterPlotter for quick testing.

    Reads the CSV files, constructs DataFrames, and runs the plotter.
    """
    forecasts = pd.read_csv(forecasts_path)
    observations = pd.read_csv(observations_path)
    ScatterPlotter().plot(forecasts, observations, output_path)



