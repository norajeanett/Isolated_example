"""
Example metric for demonstration purposes.

import pandas as pd
from chap_core.assessment.flat_representations import DataDimension, FlatForecasts, FlatObserved
from chap_core.assessment.metrics.base import MetricBase, MetricSpec


class ExampleMetric(MetricBase):
    
    Example metric that computes absolute error per location and time_period.
    This is a demonstration metric showing how to create custom metrics.
    

    spec = MetricSpec(
        output_dimensions=(DataDimension.time_period, DataDimension.location),
        metric_name="Example Absolute Error",
        metric_id="example_metric",
        description="Sum of absolute error per location and time_period",
    )

    def compute(self, observations: FlatObserved, forecasts: FlatForecasts) -> pd.DataFrame:
        # sum of absolute error per location and time_period
        merged = forecasts.merge(observations, on=["location", "time_period"], how="left")
        merged["metric"] = (merged["forecast"] - merged["disease_cases"]).abs()
        return merged[["location", "time_period", "metric"]]


if __name__ == "__main__":
    # Read the CSV files
    forecasts = pd.read_csv("example_data/forecasts.csv")
    observations = pd.read_csv("example_data/observations.csv")
    
    # Create FlatForecasts and FlatObserved objects
    flat_forecasts = FlatForecasts(forecasts)
    flat_observations = FlatObserved(observations)
    
    # Create ExampleMetric object and compute the metric
    metric = ExampleMetric()
    result = metric.get_metric(flat_observations, flat_forecasts)
    
    print("Example Metric Results:")
    print(result)
    
"""


import pandas as pd

forecasts = pd.read_csv("example_data/forecasts.csv")
observations = pd.read_csv("example_data/observations.csv")

def my_metric(forecasts: pd.DataFrame, observations: pd.DataFrame) -> pd.DataFrame:
    merged = forecasts.merge(observations, on=["location", "time_period"], how="left")
    merged["metric"] = (merged["forecast"] - merged["disease_cases"]).abs()
    return merged[["location", "time_period", "metric"]]

if __name__ == "__main__":
    print(my_metric(forecasts, observations))
