# isolated_run.py
"""
Small driver script that:
  1. Loads example forecasts and observations from CSV files
  2. Instantiates one or more Plotter classes
  3. Runs each plotter and saves results into output/

This is intentionally independent of CHAP, so it's easy to test and
experiment with visualizations locally.
"""

from pathlib import Path
import pandas as pd


from scatter_plot import ScatterPlotter  # you can import more plotters later
from outbreak_plot import OutbreakProbPlotter
from metric_plot import MetricPlotter  

def main():
    # Directory where this file lives
    base = Path(__file__).parent

    # Paths to example CSVs
    forecasts_path = base / "example_data" / "forecasts.csv"
    observations_path = base / "example_data" / "observations.csv"

    # Output directory for PNGs
    out_dir = base / "output"
    out_dir.mkdir(exist_ok=True)

    # Load data once, reuse for all plotters
    forecasts = pd.read_csv(forecasts_path)
    observations = pd.read_csv(observations_path)

    # List of plotters to run.
    # To add more visualizations, just append more Plotter instances here.
    plotters = [
        ScatterPlotter(),
        MetricPlotter(), 
        OutbreakProbPlotter(),
        # e.g
        # . EndemicPlotter(), PICoveragePlotter(), ...
    ]

    for plotter in plotters:
        out_path = out_dir / f"{plotter.name}.png"
        print(f"[main] Running plotter '{plotter.name}' → {out_path}")
        plotter.plot(forecasts, observations, str(out_path))


if __name__ == "__main__":
    main()
