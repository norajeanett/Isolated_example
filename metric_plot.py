# metric_plot.py
"""
MetricPlotter:
    Visualizes the example metric (absolute error per location/time_period)
    as a simple bar plot.

Bars:
    - x-axis: time_period
    - y-axis: metric (absolute error)
    - color: location
"""

import os
from typing import Final

import pandas as pd
import altair as alt

from plotter import Plotter

alt.data_transformers.disable_max_rows()

LOC1_COLOR: Final[str] = "#1f77b4"
LOC2_COLOR: Final[str] = "#ff7f0e"


class MetricPlotter(Plotter):
    """Bar chart of absolute error per location and time_period."""

    name: str = "metric_abs_error"

    @staticmethod
    def _compute_metric(
        forecasts: pd.DataFrame, observations: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Same logic as in isolated_asses.py:

            metric = | forecast - disease_cases |
        """
        merged = forecasts.merge(
            observations, on=["location", "time_period"], how="left"
        )
        merged["metric"] = (merged["forecast"] - merged["disease_cases"]).abs()
        return merged[["location", "time_period", "metric"]]

    def plot(
        self,
        forecasts: pd.DataFrame,
        observations: pd.DataFrame,
        out_path: str,
    ) -> str:
        """
        Create a bar chart and save to out_path.
        """
        df = self._compute_metric(forecasts, observations)

        outdir = os.path.dirname(out_path)
        if outdir:
            os.makedirs(outdir, exist_ok=True)

        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x=alt.X("time_period:N", title="Time period"),
                y=alt.Y("metric:Q", title="Absolute error"),
                color=alt.Color(
                    "location:N",
                    title="Location",
                    scale=alt.Scale(
                        domain=["loc1", "loc2"],
                        range=[LOC1_COLOR, LOC2_COLOR],
                    ),
                ),
                tooltip=["location", "time_period", "metric"],
            )
            .properties(
                title="Example Metric – Absolute Error per Location & Time",
                width=400,
                height=300,
            )
            .configure_axis(gridOpacity=0.3)
            .configure_title(anchor="middle", fontSize=16)
        )

        chart.save(out_path, scale_factor=2)
        print(f"[MetricPlotter] Saved plot to: {out_path}")
        return out_path
