import unittest

from meteostream_rpa.models import StationMeasurement
from meteostream_rpa.parsing import classify_station, parse_number


def sample_station(pm25: float = 10, rainfall: float = 2) -> StationMeasurement:
    return StationMeasurement("Centro", "Santiago", 20, 50, pm25, "Despejado", 25, 10, rainfall)


class ParsingTests(unittest.TestCase):
    def test_parse_number_with_units_and_decimal_comma(self):
        self.assertEqual(parse_number("Lluvia: 15,3 mm"), 15.3)
        self.assertEqual(parse_number("-3.2°C"), -3.2)

    def test_parse_number_rejects_text_without_number(self):
        with self.assertRaises(ValueError):
            parse_number("sin dato")

    def test_green_when_values_are_under_thresholds(self):
        result = classify_station(sample_station(), 40, 15)
        self.assertEqual(result.alert_level, "VERDE")

    def test_yellow_when_one_threshold_is_exceeded(self):
        result = classify_station(sample_station(pm25=41), 40, 15)
        self.assertEqual(result.alert_level, "AMARILLO")
        self.assertIn("PM2.5", result.alert_reason)

    def test_red_when_both_thresholds_are_exceeded(self):
        result = classify_station(sample_station(pm25=41, rainfall=16), 40, 15)
        self.assertEqual(result.alert_level, "ROJO")


if __name__ == "__main__":
    unittest.main()

