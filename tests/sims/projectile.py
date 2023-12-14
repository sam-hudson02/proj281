from models.particle import UpdateMethod
from src.sims.projectile import ProjectileSim
from src.utils.config import Config
import numpy as np
import unittest
import pandas as pd
import os
from src.utils.utils import percent_to_str, vec_to_str
import sys
sys.path.append('src')


class TestProjectile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = Config()
        cls.sim = ProjectileSim(cls.config.projectile)
        cls.mass = cls.config.projectile.mass
        cls.init_pos = cls.config.projectile.position.copy()
        cls.init_vel = cls.config.projectile.velocity.copy()
        cls.gravity = cls.config.projectile.gravity

        cls.df = pd.DataFrame()

    def analyitical_solution(self, t: float | int):
        """
        Args:
            t (float | int): time (seconds)
        Returns:
            (np.ndarray, np.ndarray): position, velocity

        Provides the analytical solution for the particle
        after time t.
        """
        accel = np.array([0, self.gravity, 0], dtype=float)

        position = self.init_pos + self.init_vel * t + \
            0.5 * accel * t**2
        velocity = self.init_vel + accel * t
        return position, velocity

    def analyse_conserved_quantities(self, position: np.ndarray,
                                     velocity: np.ndarray):
        """
        Args:
            data (dict): The data from the simulation.
            method (UpdateMethod): The method used in the simulation.
        Returns:
            None

        Analyse the conserved quantities of the simulation.
        """
        ke_init = 0.5 * self.mass * np.linalg.norm(self.init_vel)**2
        pe_init = self.mass * self.gravity * self.init_pos[1]
        energy_init = ke_init + pe_init

        ke = 0.5 * self.mass * np.linalg.norm(velocity)**2
        pe = self.mass * self.gravity * position[1]
        energy = ke - pe

        energy_error = np.linalg.norm(
            energy - energy_init) / np.linalg.norm(energy_init)

        print(f"Initial energy: {energy_init}")
        print(f"Initial kinetic energy: {ke_init}")
        print(f"Initial potential energy: {pe_init}")
        print(f"Final energy: {energy}")
        print(f"Final kinetic energy: {ke}")
        print(f"Final potential energy: {pe}")
        print(f"Energy error: {energy_error}")

        return [
            energy_init,
            energy,
            percent_to_str(float(energy_error)),
        ]

    def analyse_data(self, data: dict, method: UpdateMethod):
        times = list(data.keys())
        first_time = times[0]
        last_time = times[-1]
        total_time = last_time - first_time
        print(f"First time: {first_time}")
        print(f"Last time: {last_time}")
        print(f"Total time: {total_time}")

        analytical_position, analytical_velocity = self.analyitical_solution(
            total_time)

        position = np.array(data[last_time]['projectile']['position'])
        velocity = np.array(data[last_time]['projectile']['velocity'])

        position_error = np.linalg.norm(
            position - analytical_position) / np.linalg.norm(analytical_position)

        velocity_error = np.linalg.norm(
            velocity - analytical_velocity) / np.linalg.norm(analytical_velocity)

        print(f"Analytical position: {analytical_position}")
        print(f"Particle position: {position}")
        print(f"Position accuracy: {position_error}")
        print(f"Analytical velocity: {analytical_velocity}")
        print(f"Particle velocity: {velocity}")
        print(f"Velocity accuracy: {velocity_error}")

        # append data to column of method.name
        df_data = [
            vec_to_str(position),
            vec_to_str(analytical_position),
            percent_to_str(float(position_error)),
            vec_to_str(velocity),
            vec_to_str(analytical_velocity),
            percent_to_str(float(velocity_error)),
        ]

        conserved_quantities = self.analyse_conserved_quantities(
            position, velocity)

        df_data.extend(conserved_quantities)

        self.df[method.name] = df_data

        print(self.df)

    def run_sim(self, method: UpdateMethod):
        self.sim.reset()
        self.sim.set_method(method)
        title = f'{method.name.lower()}'
        _, data = self.sim.run(output=title)
        print(self.sim.particle.method)

        self.analyse_data(data, method)

    def test_euler(self):
        """
        Tests the euler method accuracy
        """
        self.run_sim(UpdateMethod.EULER)

    def test_euler_cromer(self):
        """
        Tests the euler-cromer method accuracy
        """
        self.run_sim(UpdateMethod.EULER_CROMER)

    def test_verlet(self):
        """
        Tests the verlet method accuracy
        """
        self.run_sim(UpdateMethod.VERLET)

    def tearDown(self):
        # change row names to velcoity, position, etc.
        self.df.index = [
            'Position (m) (x, y, z)',
            'Analytical position (m) (x, y, z)',
            'Position error',
            'Velocity (m/s) (x, y, z)',
            'Analytical velocity (m/s) (x, y, z)',
            'Velocity error',
            'Initial energy (J)',
            'Final energy (J)',
            'Energy error'
        ]

        os.makedirs('data/tests', exist_ok=True)
        self.df.to_latex('data/tests/projectile.tex')
