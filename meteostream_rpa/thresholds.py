"""Lectura de la planilla maestra de umbrales en formato CSV."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Threshold:
    pm25_max: float
    rain_max: float


def load_thresholds(path: Path, default_pm25: float, default_rain: float) -> dict[str, Threshold]:
    values: dict[str, Threshold] = {"*": Threshold(default_pm25, default_rain)}
    if not path.exists():
        return values

    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            city = (row.get("ciudad") or "").strip()
            if not city:
                continue
            values[city] = Threshold(
                pm25_max=float(row["pm25_max"]),
                rain_max=float(row["lluvia_max"]),
            )
    return values


def threshold_for(city: str, values: dict[str, Threshold]) -> Threshold:
    return values.get(city, values["*"])

