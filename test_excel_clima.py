import tempfile
import unittest
from pathlib import Path

from openpyxl import load_workbook

from ej import cargar_umbrales, evaluar_alerta, guardar_excel


class ExcelClimaTests(unittest.TestCase):
    def test_regla_or_limites_y_datos_faltantes(self):
        umbrales = {"mp25": 50, "lluvia_mm": 20}
        casos = [
            (50, 20, "SIN ALERTA"), (50.1, 0, "ALERTA"),
            (0, 20.1, "ALERTA"), (51, 21, "ALERTA"),
            (None, 21, "ALERTA"), (51, None, "ALERTA"),
            (None, 10, "SIN DATO"), (30, None, "SIN DATO"),
            (None, None, "SIN DATO"), (0, 0, "SIN ALERTA"),
        ]
        for mp25, lluvia, esperado in casos:
            with self.subTest(mp25=mp25, lluvia=lluvia):
                self.assertEqual(evaluar_alerta(
                    {"mp25": mp25, "lluvia_mm": lluvia}, umbrales), esperado)

    def test_cambio_de_umbrales(self):
        self.assertEqual(evaluar_alerta(
            {"mp25": 41, "lluvia_mm": 16},
            {"mp25": 50, "lluvia_mm": 20}), "SIN ALERTA")

    def test_maestro_y_exportacion(self):
        maestro = Path(__file__).with_name("maestro_umbrales_clima.xlsx")
        umbrales = cargar_umbrales(maestro)
        self.assertEqual(set(umbrales), {"mp25", "lluvia_mm"})
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = guardar_excel([
                {"estacion": "=texto literal", "mp25": 41, "lluvia_mm": 0},
                {"estacion": "Sin lectura", "mp25": None, "lluvia_mm": 16},
            ], umbrales, carpeta, "https://mantistcy.cl/clima/")
            libro = load_workbook(ruta)
            hoja = libro["Consolidado"]
            self.assertEqual(hoja["A8"].data_type, "s")
            self.assertEqual(hoja["E8"].value, 41)
            self.assertIsNone(hoja["E9"].value)
            self.assertIn('E8>$B$4', hoja["I8"].value)
            self.assertIn('F9>$D$4', hoja["I9"].value)
            self.assertEqual(hoja["B4"].value, umbrales["mp25"])
            self.assertEqual(hoja.auto_filter.ref, "A7:I9")
            libro.close()

    def test_maestro_faltante(self):
        with tempfile.TemporaryDirectory() as carpeta:
            with self.assertRaises(FileNotFoundError):
                cargar_umbrales(Path(carpeta) / "ausente.xlsx")


if __name__ == "__main__":
    unittest.main()
