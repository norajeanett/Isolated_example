
# CHAP-Compatible Metric & Modular Visualization Example
Overview

This project provides:

1. A simple CHAP-compatible custom metric implemented in ExampleMetric.

2. An isolated example (isolated_asses.py) demonstrating the same metric outside CHAP for easy debugging.

3. A modular visualization framework based on Altair, enabling clean and extendable plotting logic.

4. A standalone runner (isolated_run.py) that loads example CSV data and runs selected visualizations.

This structure makes it easy to experiment with metrics and visualizations before integrating them into CHAP Core.



## Project Structure
project/
│
├── example_data/
│   ├── forecasts.csv
│   └── observations.csv
│
├── plotter.py                  # Base class for all plotters
├── scatter_plot.py             # Altair scatter visualization (as class)
├── isolated_run.py             # Runs selected visualizations
│
├── example_metric.py           # CHAP-compatible metric implementation
└── isolated_asses.py           # Pure pandas version of the metric (for testing)


## 1. CHAP-Compatible Metric

The CHAP-compatible metric is implemented in example_metric.py.
It computes absolute error per location and time period and declares a MetricSpec, making it valid for integration into CHAP Core.

To integrate it into CHAP later:

- Add the file to chap_core/assessment/metrics/

- Import the class in __init__.py

- Register it in the available_metrics dictionary

Once registered, it becomes available in the CHAP Modeling App.


## 2. Isolated Metric (outside CHAP)

isolated_asses.py provides a standalone version of the same metric using only pandas.

Run it with:
python3 isolated_asses.py

This is helpful when prototyping new metrics without needing the full CHAP environment.


## Modular Visualization Framework (Altair)

The project includes a small visualization system:

plotter.py

Defines an abstract Plotter base class:
class Plotter(ABC):
    name: str
    def plot(self, forecasts, observations, out_path): ...

Every visualization inherits from this class.

scatter_plot.py

Implements ScatterPlotter, an Altair scatter plot comparing:

- Observed cases (x-axis)

- Predicted cases (y-axis)

It also includes:

- A diagonal reference line

- A clean legend placed to the right

- Tooltip support

- Nicely styled axes and gridlines

The plot is saved to a PNG file using Altair’s built-in renderer.



## Running Visualizations

Use isolated_run.py:

python3 isolated_run.py


It:

- Loads forecasts and observations CSV files

- Instantiates selected plotters

- Generates the output under output/ (e.g., output/scatter.png)

You can enable or disable visualizations by editing the list:

plotters = [
    ScatterPlotter(),
    # Add more: PICoveragePlotter(), EndemicPlotter(), ...
]

## Dependencies 
Install required packages inside your virtual environment
pip install pandas altair vega_datasets

This modular structure makes it easy to add new visualizations without changing any core logic.


# Scatter Plot (Truth vs Prediction)

File: scatter_plot.py
Output: output/scatter.png

What it shows

Each point is one data item:

- x-axis: observed values (disease_cases)

- y-axis: predicted values (forecast)

The black dashed reference line represents perfect predictions (truth = forecast).

How to interpret it

- Points on the line → good predictions

- Points above the line → the model over-predicts

- Points below the line → the model under-predicts

Why this plot is useful

- Quick visual check of the model’s accuracy

- Easy to compare different models

- A standard plot in predictive modelling and forecasting


# Metric: Example Absolute Error
Files:
    isolated_asses.py
    example_metric.py


This project also includes an example of a custom evaluation metric that can be used both standalone (outside CHAP) and as a CHAP-compatible metric.

What the metric computes:
    The metric is an absolute error per location and time_period:
metric=∣forecast−disease_cases∣\text{metric} = | \text{forecast} - \text{disease\_cases} |metric=∣forecast−disease_cases∣

Given the two flat dataframes:

- forecasts
    columns: location, time_period, horizon_distance, sample, forecast


- observations
    columns: location, time_period, disease_cases




The metric is computed by:
1. Merging forecasts and observations on location and time_period.
2. Taking the absolute difference between forecast and disease_cases.
3. Returning a dataframe with:
    location, time_period, metric

In isolated_asses.py this logic is implemented as a simple function my_metric(...) that operates directly on pandas DataFrames.

In example_metric.py the same idea is implemented as a CHAP-compatible class ExampleMetric, which:
- subclasses MetricBase
- defines a MetricSpec with:
    - output_dimensions = (time_period, location)
    - a metric id and a human-readable name
- implements compute(observations, forecasts) and returns a dataframe with the required columns.


Why this metric is useful
- It gives a simple, interpretable measure of model error at the same granularity as the data (per location and time period).
- It is easy to inspect and debug, both in the standalone version (isolated_asses.py) and via the CHAP-compatible ExampleMetric.
- It serves as a template for implementing more advanced metrics that follow the same pattern:
    - define a flat input format (forecasts + observations)
    - compute the metric in a reproducible way
    - expose the metric through a clear specification (MetricSpec) so that CHAP can validate and use it.





# Outbreak & Probability Plot (PI, Threshold, P(exceed))

File: outbreak_plot.py
Output: output/outbreak_prob.png

This is an epidemiological time-series plot inspired by the CHAP/Shiny visualizations.

It shows four things at the same time:

## 1. 95% Prediction Interval (PI band)

Shown as a grey band

Represents the uncertainty in the model’s prediction

Bounded by the 2.5% and 97.5% quantiles of the forecast distribution

## 2. Prediction Mean

- Shown as an orange line with points

. The average predicted value for each time period

## 3. Threshold (MA + 2 SD)

- Shown as a purple dashed line

- Computed as:

        a rolling mean (MA) of the observed values over several weeks

        plus 2 × standard deviation

- Used to detect unusual increases in cases
    → potential outbreak signal

## 4. P(exceed) – Probability of Exceedance

- Shown as a green line on a separate right-hand y-axis

- The probability that forecast > threshold
    (i.e. the probability that the next value will exceed the threshold)

- Interpreted as a measure of outbreak risk




Intuition

Scatter plot = model accuracy
    → “How well does the model predict the numbers?”

Outbreak plot = risk and surveillance
    → “Is there a potential disease outbreak?”

The code is structured so that adding new visualizations should be easy:
    you can plug in new plotter classes alongside the existing ScatterPlotter and OutbreakProbPlotter without changing the rest of the pipeline.


Utvikling: 

- Heatmap av feil per uke per location

- Plot av prediction interval width over tid

- Rolling absolute error

- Residual plot (observed - predicted)

## Some background on evaluation metrics

When evaluating a chap-compatible model with chap, the model will give some `samples` for every `time_period` (e.g. a week in some year) for every `location` (e.g. a district in a country). An important detail is that this is done for different **split points** in the dataset. For each such split point, the model will predict a certain number of periods (e.g. weeks a head).

This means that every predicted disease case can be tied to four variables:

- `location`
- `time_period`
- `horizon_distance`  (how far from a split point was this prediction made)
- `sample` (just an index for the sample, if the model gives 10 predictions for this location/time_period/horizon_distance, then this will go from 0 to 9)

When dealing with metrics in chap, we represent all this information using a "flat" pandas dataframe. Below is an example of the predictions given by a model for two different locations two weeks ahead:

```
  location time_period  horizon_distance  sample  forecast
0     loc1    2023-W01                 1       1        10
1     loc1    2023-W02                 2       1        12
2     loc2    2023-W01                 1       1        21
3     loc2    2023-W02                 2       1        23
```

From the above data, we can see that the model just gave one sample for each location/time_period/horizon_distance combination. Also, there was only one split point (and two horizon distances, meaning the model predicted two weeks ahead). Note that all this could vary based on the evaluation setup and the model.

The "true" observations can be represented in a similar way, except that we don't need to represent the sample index for true observations:

```
  location time_period  disease_cases
0     loc1    2023-W01           11.0
1     loc1    2023-W02           13.0
2     loc2    2023-W01           19.0
3     loc2    2023-W02           21.0
```

### Metrics in chap

Metrics in chap are in principle functions that take observed disease cases and predicted cases in the format shown above and returns a dataframe with the metric.

The output format is a dataframe with columns corresponding to what "level of detail" the metric has been computed for. For instance, if a metric is computed for each location, the output columns will be "location" and "metric", e.g:

```
    location  metric
0      loc1    1.0
1      loc2    2.0
```

However, a metric is free to aggregate over locations, time_periods or horizon_distance as it sees fit. For instance, a metric that only aggregates over time_periods might give this output:

```
    location  horizon_distance  metric
0      loc1                 1    0.5
1      loc2                 1    0.6
2      loc1                 2    0.7
3      loc2                 2    0.8
```


## Isolated example: Starting by implementing a simple metric outside of chap

Since a metric only depends on these simple pandas dataframes, it is easy to implement new metrics as a function outside of chap. 
This is useful for testing and debugging. Later in this guide, we show how to move a metric inside chap so that it can be used in the platform (e.g. to generate plots in the modeling app). 
This only requires implementing the metric function in a class that follows a interface.

This example only requires that you have pandas installed.

```python
import pandas as pd
    
forecasts = pd.DataFrame(
    {
        "location": ["loc1", "loc1", "loc2", "loc2"],
        "time_period": ["2023-W01", "2023-W02", "2023-W01", "2023-W02"],
        "horizon_distance": [1, 2, 1, 2],
        "sample": [1, 1, 1, 1],
        "forecast": [10, 12, 21, 23],
    }
)


observations = pd.DataFrame(
    {
        "location": ["loc1", "loc1", "loc2", "loc2"],
        "time_period": ["2023-W01", "2023-W02", "2023-W01", "2023-W02"],
        "disease_cases": [11.0, 13.0, 19.0, 21.0],
    }
)


def my_metric(forecasts: pd.DataFrame, observations: pd.DataFrame) -> pd.DataFrame:
    # sum of absolute error per location and time_period
    merged = forecasts.merge(observations, on=["location", "time_period"], how="left")
    merged["metric"] = (merged["forecast"] - merged["disease_cases"]).abs()
    return merged[["location", "time_period", "metric"]]

print(my_metric(forecasts, observations))
```

This code can also be found in isolated_asses.py. Feel free to play around with it and try to implement other metrics. The output from running `isolated_asses.py` should look like this:

```
  location time_period  metric
0     loc1    2023-W01     1.0
1     loc1    2023-W02     1.0
2     loc2    2023-W01     2.0
3     loc2    2023-W02     2.0
```


## Implementing a custom metric that is compatible with chap
Currently, metrics are implemented in chap-core in the assessment/metrics/ directory. A valid metric subclasses the MetricBase class and implements a compute method.

The compute method is similar to a function implemented in the isolated_asses.py example above, but in chap-core we can take use of some typing to ease development.

In the example_metric.py file, we have implemented the metric above in an ExampleMetric class. The code can also be found working inside chap-core in [example_metric.py](https://github.com/dhis2-chap/chap-core/blob/master/chap_core/assessment/metrics/example_metric.py) assessment/metrics/.

Note the metric_spec variable. This is important in order to tell chap what the metric outputs:

```python
# ...
spec = MetricSpec(
        output_dimensions=(DataDimension.location, DataDimension.time_period),
        metric_name="Example Absolute Error",
        metric_id="example_metric",
        description="Sum of absolute error per location and time_period",
    )
# ...
```

If you run `get_metric` on this class, chap will check that the output actually matches the spec. If for instance, you forget to specify location, you will get this error message from chap:

```
ValueError: ExampleMetric produced wrong columns.
Expected: [<DataDimension.time_period: 'time_period'>, 'metric']
Missing: []
Extra: ['location']
```



## Adding the metric to the chap-core codebase
After succesfully implementing a chap-compatible metric, all that is needed in order to use it in chap is to add it to the available_metrics registry in chap-core/assessment/metrics/__init__.py. Typically, your metric would be in a separate file in the assessment/metrics/ directory, and you would import it in the __init__.py file and add it to the available_metrics dictionary.

If the metric is compatible with plotting (valid output dimensions), it will automatically be available as a plotting option in the modeling app in chap.


