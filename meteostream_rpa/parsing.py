"""Conversión y validación de los valores mostrados por la web."""

from __future__ import annotations

import re

from .models import StationMeasurement


NUMBER_PATTERN = re.compile(r"-?\d+(?:[.,]\d+)?")


def parse_number(text: str) -> float:
    """Extrae el primer número de un texto como ``15.3 mm``."""
    match = NUMBER_PATTERN.search(text.replace("\xa0", " "))
    if not match:
        raise ValueError(f"No se encontró un valor numérico en: {text!r}")
    return float(match.group(0).replace(",", "."))


def classify_station(
    station: StationMeasurement,
    pm25_max: float,
    rain_max: float,
) -> StationMeasurement:
    """Aplica el semáforo usando condicionales explícitas."""
    high_pm25 = station.pm25 > pm25_max
    high_rain = station.rainfall > rain_max

    if high_pm25 and high_rain:
        station.alert_level = "ROJO"
        station.alert_reason = "PM2.5 y lluvia superan los umbrales"
    elif high_pm25:
        station.alert_level = "AMARILLO"
        station.alert_reason = f"PM2.5 supera {pm25_max:g} µg/m³"
    elif high_rain:
        station.alert_level = "AMARILLO"
        station.alert_reason = f"Lluvia supera {rain_max:g} mm"
    else:
        station.alert_level = "VERDE"
        station.alert_reason = "Sin superación de umbrales"
    return station

