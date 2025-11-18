# isolated_asses.py
"""
Isolated metric example (COMPLETELY outside CHAP).

This file:
  - Builds small example DataFrames directly in code
  - Defines a simple metric function
  - Prints the result

It is useful for quickly checking logic and explaining how metrics
are computed, without needing CHAP's MetricBase or Flat* structures.
"""

import pandas as pd

# Example forecasts DataFrame:
# one row per location + time_period (+ horizon_distance + sample)
forecasts = pd.DataFrame(
    {
        "location": ["loc1", "loc1", "loc2", "loc2"],
        "time_period": ["2023-W01", "2023-W02", "2023-W01", "2023-W02"],
        "horizon_distance": [1, 2, 1, 2],
        "sample": [1, 1, 1, 1],
        "forecast": [10, 12, 21, 23],
    }
)

# Example observations DataFrame:
# one row per location + time_period, with the true disease count.
observations = pd.DataFrame(
    {
        "location": ["loc1", "loc1", "loc2", "loc2"],
        "time_period": ["2023-W01", "2023-W02", "2023-W01", "2023-W02"],
        "disease_cases": [11.0, 13.0, 19.0, 21.0],
    }
)


def my_metric(
    forecasts: pd.DataFrame, observations: pd.DataFrame
) -> pd.DataFrame:
    """
    Example metric: absolute error per location and time_period.

    For each row:
        metric = | forecast - disease_cases |

    Returns a DataFrame with:
        location, time_period, metric
    """
    # Merge so each row has both forecast and disease_cases
    merged = forecasts.merge(observations, on=["location", "time_period"], how="left")

    # Compute absolute error
    merged["metric"] = (merged["forecast"] - merged["disease_cases"]).abs()

    # Keep only columns we care about in the final output
    return merged[["location", "time_period", "metric"]]


if __name__ == "__main__":
    # When run directly: compute metric on the example data and print it
    result = my_metric(forecasts, observations)
    print(result)
