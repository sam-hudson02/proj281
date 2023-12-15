import sys
sys.path.append('src')
from src.utils.utils import vec_to_str, percent_to_str
from models.particle import UpdateMethod
from src.sims.earth_orbit import EarthOrbit
from src.utils.config import Config
import numpy as np
import unittest
import pandas as pd


class TestSolarSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = pd.DataFrame()

    def setUp(self):
        self.config = Config()
        self.sim = EarthOrbit(self.config.earth_orbit, None)
        self.radius = self.sim.radius

    def analytical_solution(self, t: float | int):
        """
        Args:
            t (float | int): time (seconds)
        Returns:
            (np.ndarray, np.ndarray): position, velocity

        Provides the analytical solution for the particle
        after time t.
        """

        omega = np.sqrt(self.sim.G * self.sim.mass / self.radius**3)
        theta = omega * t

        tan_vel = self.sim.orbital_velocity(self.radius)

        analytical_pos = np.array([self.radius * np.cos(theta),
                                   self.radius * np.sin(theta),
                                   0])

        analytical_vel = np.array([-tan_vel * np.sin(theta),
                                   tan_vel * np.cos(theta),
                                   0])

        return analytical_pos, analytical_vel

    def vetor_to_earth(self, sat_pos: np.ndarray, earth_pos: np.ndarray):
        """
        Args:
            sat_pos (np.ndarray): satellite position
            earth_pos (np.ndarray): earth position
        Returns:
            (np.ndarray): vector to earth

        Provides the vector from the satellite to the earth
        """
        return earth_pos - sat_pos

    def compare_position(self, analytical_pos: np.ndarray,
                         act_pos: np.ndarray):
        """
        Args:
            analytical_pos (np.ndarray): analytical position
            act_pos (np.ndarray): actual position
        Returns:
            (float): position accuracy

        Compares the analytical position with the particle position
        """

        # work out the difference vector
        difference_vec = act_pos - analytical_pos
        accuracy = np.linalg.norm(difference_vec) / \
            np.linalg.norm(analytical_pos)

        actual_radius = np.linalg.norm(act_pos)

        radius_accuracy = np.abs(actual_radius - self.radius) / self.radius

        print("\n")
        print("-" * 20, "Position Comparison", "-" * 20, "\n")
        print(f"Accuracy: {accuracy}")
        print(f"Analytical position: {analytical_pos}")
        print(f"Particle position: {act_pos}")
        print(f"Analytical radius: {self.radius}")
        print(f"Actual radius: {actual_radius}")
        print(f"Radius accuracy: {radius_accuracy}")

        self.assertTrue(accuracy < 2e-2)
        self.assertTrue(radius_accuracy < 2e-2)

        anl_radius_str = f"{self.radius:.2e}"
        act_radius_str = f"{actual_radius:.2e}"

        return [
            vec_to_str(act_pos),
            vec_to_str(analytical_pos),
            percent_to_str(float(accuracy)),
            act_radius_str,
            anl_radius_str,
            percent_to_str(float(radius_accuracy))
        ]

    def compare_velocity(self, analytical_vel: np.ndarray,
                         act_vel: np.ndarray):
        """
        Args:
            analytical_vel (np.ndarray): analytical velocity
            act_vel (np.ndarray): actual velocity
        Returns:
            (float): velocity accuracy

        Compares the analytical velocity with the particle velocity
        """

        # work out the difference vector
        difference_vec = act_vel - analytical_vel
        accuracy = np.linalg.norm(difference_vec) / \
            np.linalg.norm(analytical_vel)

        analytical_speed = np.linalg.norm(analytical_vel)
        act_speed = np.linalg.norm(act_vel)

        speed_accuracy = np.abs(
            analytical_speed - act_speed) / analytical_speed

        print("\n")
        print("-" * 20, "Velocity Comparison", "-" * 20, "\n")
        print(f"Velocity Accuracy: {accuracy}")
        print(f"Analytical velocity: {analytical_vel}")
        print(f"Particle velocity: {act_vel}")
        print(f"Analytical speed: {analytical_speed}")
        print(f"Particle speed: {act_speed}")
        print(f"Speed accuracy: {speed_accuracy}")

        self.assertTrue(accuracy < 2e-2)
        self.assertTrue(speed_accuracy < 2e-2)

        anl_speed_str = f"{analytical_speed:.2e}"
        act_speed_str = f"{act_speed:.2e}"

        return [
            vec_to_str(act_vel),
            vec_to_str(analytical_vel),
            percent_to_str(float(accuracy)),
            act_speed_str,
            anl_speed_str,
            percent_to_str(float(speed_accuracy))
        ]

    def run_sim_test(self, method: UpdateMethod):
        """
        Args:
            method (UpdateMethod): update method
        Returns:
            (dict): data

        Runs the simulation and returns the data
        """
        self.sim = EarthOrbit(self.config.earth_orbit)
        self.sim.set_method(method)
        _, data = self.sim.run()
        times = list(data.keys())

        last_time = times[-1]

        analytical_pos, analytical_vel = self.analytical_solution(last_time)

        last_pos_sat = np.array(data[last_time]['satellite']['position'])
        last_vel_sat = np.array(data[last_time]['satellite']['velocity'])

        last_pos_earth = np.array(data[last_time]['399']['position'])
        last_vel_earth = np.array(data[last_time]['399']['velocity'])

        pos = last_pos_sat - last_pos_earth
        vel = last_vel_sat - last_vel_earth

        pos_data = self.compare_position(analytical_pos, pos)
        vel_data = self.compare_velocity(analytical_vel, vel)

        df_data = pos_data + vel_data

        self.df[method.name] = df_data

    def test_euler(self):
        """
        Tests the euler method
        """
        print("\n")
        print("*" * 10 + "Euler" + "*" * 10)
        print("\n")

        self.run_sim_test(UpdateMethod.EULER)
        print("\n")

    def test_euler_cromer(self):
        """
        Tests the euler cromer method
        """
        print("\n")
        print("*" * 10 + "Euler Cromer" + "*" * 10)

        self.run_sim_test(UpdateMethod.EULER_CROMER)
        print("\n")

    def test_verlet(self):
        """
        Tests the verlet method
        """
        print("\n")
        print("*" * 10 + "Verlet" + "*" * 10)
        print("\n")

        self.run_sim_test(UpdateMethod.VERLET)

    def tearDown(self):
        """
        Tears down the test
        """

        indexes = [
            "Actual Position (m) (x, y, z)",
            "Analytical Position (m) (x, y, z)",
            "Position Accuracy",
            "Actual Radius (m)",
            "Analytical Radius (m)",
            "Radius Accuracy",
            "Actual Velocity (m/s) (x, y, z)",
            "Analytical Velocity (m/s) (x, y, z)",
            "Velocity Accuracy",
            "Actual Speed (m/s)",
            "Analytical Speed (m/s)",
            "Speed Accuracy"
        ]

        # rename indexes
        self.df.index = indexes

        self.df.to_latex("data/tests/earth_orbit.tex")
