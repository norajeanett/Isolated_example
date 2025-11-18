# plotter.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
import pandas as pd


class Plotter(ABC):
    """
    Base class for all visualizations in this mini-project.

    Idea:
    - Each concrete plotter implements `plot(...)`.
    - We can easily add new plotters later (PI-coverage, endemic, etc.)
      without changing the code that calls them.
    """

    # Short name used for filenames (e.g. "scatter" -> scatter.png)
    name: str = "base"

    @abstractmethod
    def plot(
        self,
        forecasts: pd.DataFrame,
        observations: pd.DataFrame,
        out_path: str,
    ) -> str:
        """
        Create a plot and save it to `out_path`.

        Parameters
        ----------
        forecasts : pd.DataFrame
            Flat forecasts (one row per location/time_period/horizon_distance/sample).
        observations : pd.DataFrame
            Flat observations (one row per location/time_period).
        out_path : str
            File path where the PNG should be written.

        Returns
        -------
        str
            The path to the written file (convenient for logging).
        """
        raise NotImplementedError
