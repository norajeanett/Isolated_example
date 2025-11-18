# outbreak_plot.py
"""
Outbreak & Probability plot.

Viser:
    - 95 % prediksjonsintervall (grått bånd)
    - Mean prediction (oransje linje m/ punkter)
    - Threshold = MA + 2·SD (lilla stiplet linje)
    - P(exceed) på høyre y-akse (grønn linje)

Input:
    forecasts:    pandas.DataFrame med kolonner
                  ["location", "time_period", "forecast", ...]
    observations: pandas.DataFrame med kolonner
                  ["location", "time_period", "disease_cases"]

Brukes fra isolated_run.py sammen med andre plottere.
"""

from __future__ import annotations

import math
import os
from typing import Final, List, Tuple, Dict

import altair as alt
import numpy as np
import pandas as pd

from plotter import Plotter

# Altair default har max_rows-begrensning, vi skrur den av.
alt.data_transformers.disable_max_rows()

# Farger brukt konsekvent i plottet
PRED_COLOR: Final[str] = "#ff7f0e"   # oransje
THR_COLOR: Final[str] = "#9575cd"    # lilla
BAND_COLOR: Final[str] = "#d9d9d9"   # lys grå for PI-bånd
PROB_COLOR: Final[str] = "#43a047"   # grønn


class OutbreakProbPlotter(Plotter):
    """Time series of prediction, threshold and P(exceed)."""

    # Navn brukes til å lage filnavn: outbreak_prob.png
    name: str = "outbreak_prob"

#Hjelpefunksjoner for databehandling
    @staticmethod
    def _series_means_over_locations(
        observations: pd.DataFrame,
    ) -> Tuple[List[str], List[float]]:
        """
        Beregn gjennomsnittlig disease_cases per time_period
        på tvers av alle locations.
        """
        grouped = (
            observations
            .groupby("time_period")["disease_cases"]
            .mean()
            .sort_index()
        )
        times = grouped.index.tolist()
        values = grouped.values.astype(float).tolist()
        return times, values

    @staticmethod
    def _rolling_ma_sd(values: List[float], k: int = 3) -> Tuple[List[float], List[float]]:
        """
        Glidende gjennomsnitt og standardavvik med vindu ±k.
        For korte serier (som her) gir dette i praksis en "smoothed" versjon.
        """
        n = len(values)
        arr = np.array(values, dtype=float)
        ma, sd = [], []
        for i in range(n):
            lo, hi = max(0, i - k), min(n, i + k + 1)
            window = arr[lo:hi]
            ma.append(float(window.mean()))
            sd.append(float(window.std(ddof=0)))
        return ma, sd

    @staticmethod
    def _pred_samples_by_time(forecasts: pd.DataFrame) -> Dict[str, List[float]]:
        """
        Samler alle forecast-verdier per time_period.
        Her har vi bare én sample per rad, men funksjonen
        støtter flere samples per time_period.
        """
        by_time: Dict[str, List[float]] = {}
        for _, row in forecasts.iterrows():
            t = row["time_period"]
            v = float(row["forecast"])
            by_time.setdefault(t, []).append(v)
        return by_time

    @classmethod
    def _make_endemic_df(
        cls,
        forecasts: pd.DataFrame,
        observations: pd.DataFrame,
        z: float = 2.0,
        k: int = 3,
    ) -> pd.DataFrame:
        """
        Bygger en DataFrame med alle størrelser vi trenger:

            time_period
            obs_mean   : mean observed cases
            ma         : rolling mean(obs_mean)
            thr        : threshold = ma + z * sd
            pred_mean  : mean forecast per time_period
            pred_lo    : 2.5-percentil av forecast
            pred_hi    : 97.5-percentil av forecast
            p_exc      : P(forecast > thr)
        """
        # Observasjoner: gjennomsnitt per uke
        times, obs_mean = cls._series_means_over_locations(observations)
        ma, sd = cls._rolling_ma_sd(obs_mean, k=k)
        thr = [m + z * s for m, s in zip(ma, sd)]

        obs_map = dict(zip(times, obs_mean))
        ma_map = dict(zip(times, ma))
        thr_map = dict(zip(times, thr))

        # Forecast-samples per uke
        samples_by_time = cls._pred_samples_by_time(forecasts)

        rows = []
        all_times = sorted(set(times) | set(samples_by_time.keys()))
        for t in all_times:
            samples = np.array(samples_by_time.get(t, []), dtype=float)
            if samples.size:
                pred_mean = float(samples.mean())
                pred_lo = float(np.percentile(samples, 2.5))
                pred_hi = float(np.percentile(samples, 97.5))
            else:
                pred_mean = pred_lo = pred_hi = None

            obs_t = obs_map.get(t)
            ma_t = ma_map.get(t)
            thr_t = thr_map.get(t)

            if samples.size and thr_t is not None:
                p_exc = float((samples > thr_t).mean())
            else:
                p_exc = None

            rows.append(
                dict(
                    time_period=t,
                    obs_mean=obs_t,
                    ma=ma_t,
                    thr=thr_t,
                    pred_mean=pred_mean,
                    pred_lo=pred_lo,
                    pred_hi=pred_hi,
                    p_exc=p_exc,
                )
            )

        return pd.DataFrame(rows).sort_values("time_period")

    #Plot

    def plot(
        self,
        forecasts: pd.DataFrame,
        observations: pd.DataFrame,
        output_path: str,
    ) -> str:
        """
        Lager outbreak/probability-plott og lagrer det til output_path.
        """
        df = self._make_endemic_df(forecasts, observations)

        # Sørg for at output-mappe finnes
        outdir = os.path.dirname(output_path)
        if outdir:
            os.makedirs(outdir, exist_ok=True)

        # dynamisk y-skala basert på dataene 
        try:
            y_min = float(df[["pred_lo", "thr", "pred_mean"]].min().min())
            y_max = float(df[["pred_hi", "thr", "pred_mean"]].max().max())
        except (TypeError, ValueError):
            y_min, y_max = 0.0, 1.0

        if not (math.isfinite(y_min) and math.isfinite(y_max)):
            y_min, y_max = 0.0, 1.0

        if y_max == y_min:
            y_max = y_min + 1.0

        margin = 0.05 * (y_max - y_min)
        y_min -= margin
        y_max += margin
        y_scale = alt.Scale(domain=[y_min, y_max])

        # base-chart: kategorisk x-akse, lite padding 
        base = alt.Chart(df).encode(
            x=alt.X(
                "time_period:N",
                title="Time",
                axis=alt.Axis(labelAngle=0, labelOverlap=True),
                scale=alt.Scale(paddingInner=0.2, paddingOuter=0.05),
            )
        )

        # 95 % PI (grått bånd)
        band = base.mark_area(opacity=0.25, color=BAND_COLOR).encode(
            y=alt.Y("pred_lo:Q", axis=None, scale=y_scale),
            y2="pred_hi:Q",
        )

        # Prediksjons-mean (oransje linje med punkter)
        pred = base.mark_line(point=True, color=PRED_COLOR).encode(
            y=alt.Y(
                "pred_mean:Q",
                title="Prediction / Threshold / PI",
                scale=y_scale,
            ),
        )

        # Threshold (MA + 2·SD, lilla stiplet)
        thr = base.mark_line(strokeDash=[5, 4], color=THR_COLOR).encode(
            y=alt.Y("thr:Q", axis=None, scale=y_scale),
        )

        # P(exceed) på høyre akse (grønn)
        prob = base.mark_line(color=PROB_COLOR, strokeWidth=2).encode(
            y=alt.Y(
                "p_exc:Q",
                title="P(exceed)",
                axis=alt.Axis(orient="right"),
                scale=alt.Scale(domain=[0, 1]),
            )
        )

        main_chart = (
            alt.layer(band, pred, thr, prob)
            .resolve_scale(y="independent")
            .properties(
                title="Outbreak & Probability (95% PI, threshold, P(exceed))",
                width=450,
                height=350,
            )
            
        )

        # design
        # Legend-data: hver label får to punkter (x=0 og x=1) slik at vi kan tegne en kort linje
        legend_df = pd.DataFrame({
            "label": ["95% PI", "95% PI",
                    "P(exceed)", "P(exceed)",
                    "Prediction", "Prediction",
                    "Threshold", "Threshold"],
            "x":     [0, 1,
                    0, 1,
                    0, 1,
                    0, 1],
            "group": ["95% PI", "95% PI",
                    "P(exceed)", "P(exceed)",
                    "Prediction", "Prediction",
                    "Threshold", "Threshold"],
        })

        legend_chart = (
            alt.Chart(legend_df)
            .mark_line(strokeWidth=3)
            .encode(
                x=alt.X("x:Q", axis=None),
                y=alt.Y("label:N", axis=alt.Axis(title=None)),
                color=alt.Color(
                    "label:N",
                    scale=alt.Scale(
                        domain=["Prediction", "Threshold", "95% PI", "P(exceed)"],
                        range=[PRED_COLOR, THR_COLOR, BAND_COLOR, PROB_COLOR],
                    ),
                    legend=None,
                ),
                detail="group:N",   # sørger for én linje per label
            )
            .properties(width=160, height=140)
        )


        # Kombiner hovedplott + legend horisontalt
        final_chart = alt.hconcat(main_chart, legend_chart, spacing=20)
        final_chart = (
            final_chart
            .configure_title(fontSize=18, anchor="middle")
            .configure_axis(gridOpacity=0.3)
        )
        # Lagre til PNG (eller .html hvis du vil)
        final_chart.save(output_path, scale_factor=2)
        print(f"[OutbreakProbPlotter] Saved plot to: {output_path}")
        return output_path
