"""Configuración centralizada y segura del robot."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _bool_from_env(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "si", "sí", "on"}


@dataclass(slots=True)
class Settings:
    base_url: str = "https://mantistcy.cl/clima/"
    timeout: int = 20
    headless: bool = True
    forecast_city: str = "Santiago"
    default_pm25_max: float = 40.0
    default_rain_max: float = 15.0
    earthquake_min: float = 5.0
    output_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "salidas")
    download_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "descargas")
    evidence_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "evidencias")
    log_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "logs")
    thresholds_file: Path = field(
        default_factory=lambda: PROJECT_ROOT / "data" / "maestro_umbrales_clima.csv"
    )

    @classmethod
    def from_environment(cls) -> "Settings":
        defaults = cls()
        return cls(
            base_url=os.getenv("METEOSTREAM_BASE_URL", defaults.base_url).rstrip("/") + "/",
            timeout=int(os.getenv("METEOSTREAM_TIMEOUT", "20")),
            headless=_bool_from_env(os.getenv("METEOSTREAM_HEADLESS"), True),
            forecast_city=os.getenv("METEOSTREAM_CIUDAD", "Santiago"),
            default_pm25_max=float(os.getenv("METEOSTREAM_PM25_MAX", "40")),
            default_rain_max=float(os.getenv("METEOSTREAM_LLUVIA_MAX", "15")),
            earthquake_min=float(os.getenv("METEOSTREAM_SISMO_MIN", "5.0")),
        )

    def ensure_directories(self) -> None:
        for path in (self.output_dir, self.download_dir, self.evidence_dir, self.log_dir):
            path.mkdir(parents=True, exist_ok=True)
