import os
import unittest

from meteostream_rpa import MeteoStreamRobot, Settings


@unittest.skipUnless(os.getenv("RUN_LIVE_TESTS") == "1", "Prueba en vivo desactivada")
class LiveSmokeTests(unittest.TestCase):
    def test_public_site_exposes_climate_and_earthquakes(self):
        settings = Settings(headless=True)
        with MeteoStreamRobot(settings) as robot:
            robot._open_home()
            stations = robot.scrape_stations()
            earthquakes = robot.open_and_scrape_earthquakes()
        self.assertGreaterEqual(len(stations), 10)
        self.assertGreaterEqual(len(earthquakes), 1)


if __name__ == "__main__":
    unittest.main()

