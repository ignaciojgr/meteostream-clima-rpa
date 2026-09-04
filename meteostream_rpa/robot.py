"""Automatización del sitio METEOSTREAM usando únicamente Selenium."""

from __future__ import annotations

import logging
import re
import time
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from .config import Settings
from .models import Earthquake, RunResult, StationMeasurement
from .parsing import classify_station, parse_number
from .reporting import export_excel, export_json
from .thresholds import load_thresholds, threshold_for


class RobotExecutionError(RuntimeError):
    """Error controlado de una ejecución del robot."""


class MeteoStreamRobot:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.driver: webdriver.Firefox | None = None
        self.wait: WebDriverWait | None = None
        self.logger = logging.getLogger("meteostream_rpa")

    def __enter__(self) -> "MeteoStreamRobot":
        self.settings.ensure_directories()
        self._configure_logging()
        self.driver = self._build_driver()
        self.wait = WebDriverWait(self.driver, self.settings.timeout)
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        if self.driver is not None:
            self.driver.quit()

    def _configure_logging(self) -> None:
        log_file = self.settings.log_dir / "meteostream_rpa.log"
        if not self.logger.handlers:
            formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            self.logger.setLevel(logging.INFO)

    def _build_driver(self) -> webdriver.Firefox:
        options = Options()
        if self.settings.headless:
            options.add_argument("-headless")
        options.add_argument("--width=1440")
        options.add_argument("--height=1200")

        # Firefox descarga la telemetría sin abrir diálogos interactivos.
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", str(self.settings.download_dir.resolve()))
        options.set_preference("browser.download.useDownloadDir", True)
        options.set_preference("browser.download.alwaysOpenPanel", False)
        options.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/plain,application/octet-stream")
        options.set_preference("pdfjs.disabled", True)
        try:
            return webdriver.Firefox(options=options)
        except WebDriverException as exc:
            raise RobotExecutionError(f"No fue posible iniciar Mozilla Firefox: {exc.msg}") from exc

    def run(self, download_raw: bool = False, fill_demo_form: bool = False) -> RunResult:
        """Ejecuta el flujo completo y devuelve las rutas de los resultados."""
        if self.driver is None or self.wait is None:
            raise RobotExecutionError("El robot debe ejecutarse dentro de un bloque 'with'.")

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.logger.info("Inicio de extracción de datos")
        raw_path: Path | None = None

        try:
            self._open_home()
            self._screenshot("01_inicio_clima.png")
            stations = self.scrape_stations()
            forecast = self.select_forecast_city(self.settings.forecast_city)
            if download_raw:
                raw_path = self.download_raw_telemetry()

            earthquakes = self.open_and_scrape_earthquakes()
            self._screenshot("02_sismos.png")

            notices = self.open_and_scrape_notices()
            self._hide_sensitive_page_details()
            self._screenshot("03_avisos.png")
            if fill_demo_form:
                self.fill_notice_form_demo()
                self._hide_sensitive_page_details()
                self._screenshot("04_formulario_demo_sin_publicar.png")

            thresholds = load_thresholds(
                self.settings.thresholds_file,
                self.settings.default_pm25_max,
                self.settings.default_rain_max,
            )
            for station in stations:
                limit = threshold_for(station.city, thresholds)
                classify_station(station, limit.pm25_max, limit.rain_max)

            excel_path = export_excel(
                stations,
                earthquakes,
                notices,
                self.settings.output_dir / f"clima_consolidado_{stamp}.xlsx",
            )
            json_path = export_json(
                stations,
                earthquakes,
                notices,
                forecast,
                self.settings.output_dir / f"resumen_ejecucion_{stamp}.json",
            )
            self.logger.info("Ejecución exitosa: %s estaciones procesadas", len(stations))
            return RunResult(stations, earthquakes, notices, forecast, excel_path, json_path, raw_path)
        except (TimeoutException, NoSuchElementException, ValueError, WebDriverException) as exc:
            error_path = self.settings.evidence_dir / f"error_{stamp}.png"
            try:
                self.driver.save_screenshot(str(error_path))
            except WebDriverException:
                self.logger.exception("No fue posible guardar la captura de error")
            self.logger.exception("Fallo controlado durante la automatización")
            raise RobotExecutionError(str(exc)) from exc

    def _open_home(self) -> None:
        self.driver.get(self.settings.base_url)
        self.wait.until(EC.visibility_of_element_located((By.XPATH, "//h5[normalize-space()='Arica']")))

    def _screenshot(self, filename: str) -> None:
        self.driver.save_screenshot(str(self.settings.evidence_dir / filename))

    def _hide_sensitive_page_details(self) -> None:
        """Oculta la IP reflejada por avisos.php antes de crear evidencia pública."""
        candidates = self.driver.find_elements(
            By.XPATH,
            "//*[not(*) and (contains(normalize-space(.), 'Tu IP:') or "
            "contains(normalize-space(.), 'IP:'))]",
        )
        for element in candidates:
            self.driver.execute_script("arguments[0].style.visibility='hidden';", element)

    @staticmethod
    def _value_after_label(card, label: str) -> str:
        locator = (
            ".//small[contains(translate(normalize-space(.), "
            "'abcdefghijklmnopqrstuvwxyzáéíóúüñ', 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÜÑ'), "
            + repr(label.upper())
            + ")]/following-sibling::*[1]"
        )
        return card.find_element(By.XPATH, locator).text.strip()

    def scrape_stations(self) -> list[StationMeasurement]:
        cards = self.wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.bd-card.h-100"))
        )
        stations: list[StationMeasurement] = []

        # Ciclo principal: recorre todas las tarjetas encontradas en la matriz.
        for card in cards:
            try:
                city = card.find_element(By.TAG_NAME, "h5").text.strip()
            except NoSuchElementException:
                continue
            card_text = card.text
            maximum = re.search(r"Máx:\s*(-?[\d.,]+)", card_text, re.IGNORECASE)
            minimum = re.search(r"Mín:\s*(-?[\d.,]+)", card_text, re.IGNORECASE)
            rainfall = re.search(r"Lluvia:\s*(-?[\d.,]+)", card_text, re.IGNORECASE)
            if not (maximum and minimum and rainfall):
                raise ValueError(f"La tarjeta de {city} no contiene máximas, mínimas y lluvia.")

            stations.append(
                StationMeasurement(
                    zone=card.find_element(By.CSS_SELECTOR, "span.text-uppercase").text.replace("ESTACIÓN", "").strip().title(),
                    city=city,
                    temperature=parse_number(self._value_after_label(card, "TEMP ACTUAL")),
                    humidity=parse_number(self._value_after_label(card, "HUMEDAD")),
                    pm25=parse_number(self._value_after_label(card, "MP 2.5")),
                    condition=self._value_after_label(card, "CONDICIÓN"),
                    maximum=parse_number(maximum.group(1)),
                    minimum=parse_number(minimum.group(1)),
                    rainfall=parse_number(rainfall.group(1)),
                )
            )

        if not stations:
            raise ValueError("No se extrajo ninguna estación meteorológica.")
        return stations

    def select_forecast_city(self, city: str) -> str:
        self.driver.find_element(By.ID, "pronostico-tab").click()
        select_element = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "select[name='ciudad_pro']"))
        )
        selector = Select(select_element)
        available = [option.text.strip() for option in selector.options]
        if city not in available:
            self.logger.warning("Ciudad %s no disponible; se utilizará Santiago", city)
            city = "Santiago"
        selector.select_by_visible_text(city)
        self.wait.until(lambda driver: city in driver.find_element(By.ID, "pronostico").text)
        text = self.driver.find_element(By.ID, "pronostico").text
        return " ".join(text.split())[:500]

    def download_raw_telemetry(self) -> Path:
        self.driver.find_element(By.ID, "tiempo-real-tab").click()
        before = {
            path: path.stat().st_mtime_ns
            for path in self.settings.download_dir.iterdir()
            if path.is_file()
        }
        self.driver.find_element(By.CSS_SELECTOR, "a[href='index.php?download=1']").click()
        deadline = time.monotonic() + self.settings.timeout

        # Espera activa acotada: termina al aparecer un archivo completo o al vencer el plazo.
        while time.monotonic() < deadline:
            completed = [
                path
                for path in self.settings.download_dir.iterdir()
                if not path.name.startswith(".")
                and path.suffix != ".crdownload"
                and path.is_file()
                and path.stat().st_size > 0
                and (path not in before or path.stat().st_mtime_ns != before[path])
            ]
            if completed:
                self.logger.info("Telemetría Raw descargada: %s", completed[0].name)
                return completed[0]
            time.sleep(0.25)
        raise TimeoutException("La descarga de telemetría Raw no finalizó a tiempo.")

    def open_and_scrape_earthquakes(self) -> list[Earthquake]:
        self._open_home()
        self.driver.find_element(By.CSS_SELECTOR, "a[href='obtener_sismos.php']").click()
        rows = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr")))
        earthquakes: list[Earthquake] = []
        for row in rows:
            cells = [cell.text.strip() for cell in row.find_elements(By.TAG_NAME, "td")]
            if len(cells) < 5:
                continue
            magnitude = parse_number(cells[1])
            earthquakes.append(
                Earthquake(cells[0], magnitude, cells[2], cells[3], cells[4], magnitude >= self.settings.earthquake_min)
            )
        return earthquakes

    def open_and_scrape_notices(self) -> list[str]:
        self._open_home()
        self.driver.find_element(By.CSS_SELECTOR, "a[href='avisos.php']").click()
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "form select[name='region']")))
        cards = self.driver.find_elements(By.CSS_SELECTOR, "div.bd-card")
        notices: list[str] = []
        for card in cards:
            text = " ".join(card.text.split())
            if "Avisos Activos" in text:
                # El sitio refleja la IP del visitante; se anonimiza antes de exportar.
                sanitized = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "[IP OCULTA]", text)
                notices.append(sanitized)
        return notices

    def fill_notice_form_demo(self) -> None:
        """Carga datos en el formulario sin enviar ni modificar el sitio público."""
        region = Select(self.driver.find_element(By.CSS_SELECTOR, "select[name='region']"))
        alert_type = Select(self.driver.find_element(By.CSS_SELECTOR, "select[name='tipo_alerta']"))
        region.select_by_visible_text("Región Metropolitana")
        alert_type.select_by_visible_text("Aviso Meteorológico")
        description = self.driver.find_element(By.CSS_SELECTOR, "textarea[name='descripcion']")
        description.clear()
        description.send_keys("DEMOSTRACIÓN ACADÉMICA: formulario completado por Selenium, sin publicar.")
        self.logger.info("Formulario de aviso rellenado en modo demostración; no se envió")
