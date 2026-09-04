"""Interfaz de línea de comandos del robot."""

from __future__ import annotations

import argparse
import logging
import sys

from .config import Settings
from .robot import MeteoStreamRobot, RobotExecutionError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extrae telemetría, sismos y avisos con Python + Selenium."
    )
    display = parser.add_mutually_exclusive_group()
    display.add_argument("--headless", action="store_true", help="Ejecuta sin ventana visible.")
    display.add_argument("--visible", action="store_true", help="Muestra el navegador.")
    parser.add_argument("--ciudad", default=None, help="Ciudad del pronóstico extendido.")
    parser.add_argument(
        "--descargar-raw",
        action="store_true",
        help="Descarga la telemetría Raw usando un clic de Selenium.",
    )
    parser.add_argument(
        "--llenar-formulario-demo",
        action="store_true",
        help="Rellena el formulario de avisos sin publicarlo.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = Settings.from_environment()

    if args.headless:
        settings.headless = True
    elif args.visible:
        settings.headless = False
    if args.ciudad:
        settings.forecast_city = args.ciudad

    try:
        with MeteoStreamRobot(settings) as robot:
            result = robot.run(
                download_raw=args.descargar_raw,
                fill_demo_form=args.llenar_formulario_demo,
            )
    except RobotExecutionError as exc:
        logging.getLogger(__name__).error("La ejecución no pudo completarse: %s", exc)
        return 1

    print(f"Estaciones procesadas: {len(result.stations)}")
    print(f"Sismos procesados: {len(result.earthquakes)}")
    print(f"Alertas meteorológicas: {result.weather_alert_count}")
    print(f"Reporte Excel: {result.excel_path}")
    print(f"Resumen JSON: {result.json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

