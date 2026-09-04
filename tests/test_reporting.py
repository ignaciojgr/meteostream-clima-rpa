import json
import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

from meteostream_rpa.models import Earthquake
from meteostream_rpa.parsing import classify_station
from meteostream_rpa.reporting import export_excel, export_json
from tests.test_parsing import sample_station


class ReportingTests(unittest.TestCase):
    def test_exports_excel_and_json(self):
        station = classify_station(sample_station(pm25=45), 40, 15)
        earthquake = Earthquake("AMARILLO", 5.1, "Coquimbo", "2026-09-03", "55 km", True)

        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            excel = export_excel([station], [earthquake], [], target / "reporte.xlsx")
            summary = export_json([station], [earthquake], [], "Santiago", target / "resumen.json")

            workbook = load_workbook(excel)
            self.assertEqual(workbook["Clima"]["B2"].value, "Santiago")
            self.assertEqual(workbook["Sismos"]["B2"].value, 5.1)
            payload = json.loads(summary.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "SUCCESS")
            self.assertEqual(payload["estaciones_procesadas"], 1)


if __name__ == "__main__":
    unittest.main()

