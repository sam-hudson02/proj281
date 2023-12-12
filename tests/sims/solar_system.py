import os
import unittest
from src.utils.config import Config
from src.sims.solar_system import SolarSystemSim


class TestSolarSystem(unittest.TestCase):
    def setUp(self) -> None:
        self._config = Config()
        output = "sol_test"
        self._solar_system = SolarSystemSim(self._config.solar_system, output)

    def test_init(self) -> None:
        self.assertEqual(len(self._solar_system._particles), 9)

    def test_run(self) -> None:
        # delete the file if it exists
        if os.path.exists("data/solar_system/sol_test.json"):
            os.remove("data/solar_system/sol_test.json")

        title, data = self._solar_system.run()

        # check that the file was created
        self.assertTrue(os.path.exists("data/solar_system/sol_test.json"))

    def check_orbit(self, data: dict):
        # check that the orbit is closed
        pass
