"""Modelos de datos del proceso automatizado."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(slots=True)
class StationMeasurement:
    zone: str
    city: str
    temperature: float
    humidity: float
    pm25: float
    condition: str
    maximum: float
    minimum: float
    rainfall: float
    alert_level: str = "VERDE"
    alert_reason: str = "Sin superación de umbrales"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class Earthquake:
    source_alert: str
    magnitude: float
    location: str
    occurred_at: str
    depth: str
    threshold_alert: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class RunResult:
    stations: list[StationMeasurement]
    earthquakes: list[Earthquake]
    notices: list[str]
    forecast_summary: str
    excel_path: Path
    json_path: Path
    raw_download: Path | None = None

    @property
    def weather_alert_count(self) -> int:
        return sum(station.alert_level != "VERDE" for station in self.stations)

