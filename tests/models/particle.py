from src.models.particle import Particle, UpdateMethod
# import testing framework
import unittest
import numpy as np
import random


class TestParticle(unittest.TestCase):
    def setUp(self):
        self.init_position = np.array([0, 0, 0], dtype=float)
        self.init_velocity = np.array([30, 20, 0], dtype=float)
        self.acceleration = np.array([0, -10, 0], dtype=float)
        self.mass = 3
        self.name = "test_particle"
        self.particle = Particle(self.init_position, self.init_velocity,
                                 self.acceleration, mass=self.mass,
                                 name=self.name)

    def create_particle(self):
        # random number between 20 and 100
        x = random.uniform(20, 100)
        y = random.uniform(20, 100)
        accel = random.uniform(3, 100)
        mass = random.uniform(1, 100)

        self.init_position = np.array([x, y, 0], dtype=float)
        self.init_velocity = np.array([0, 0, 0], dtype=float)
        self.acceleration = np.array([0, -accel, 0], dtype=float)
        self.mass = mass
        self.name = "test_particle"
        self.particle = Particle(self.init_position, self.init_velocity,
                                 self.acceleration, mass=self.mass,
                                 name=self.name)

    def analyitical_solution(self, t: float | int):
        """
        Args:
            t (float | int): time (seconds)
        Returns:
            (np.ndarray, np.ndarray): position, velocity

        Provides the analytical solution for the particle
        after time t.
        """

        position = self.init_position + self.init_velocity * t + \
            0.5 * self.acceleration * t**2
        velocity = self.init_velocity + self.acceleration * t
        return position, velocity

    def compare_position(self, analytical_position: np.ndarray):
        """
        Args:
            analytical_position (np.ndarray): analytical position
        Returns:
            (float): position accuracy

        Compares the analytical position with the particle position
        """

        # work out the difference vector
        difference_vec = self.particle.position - analytical_position
        diff = np.linalg.norm(difference_vec)

        analytical_pos_mag = np.linalg.norm(analytical_position)

        pos_accuracy = 1 - (diff / analytical_pos_mag)

        print(f"Analytical position: {analytical_position}")
        print(f"Particle position: {self.particle.position}")
        print(f"Position accuracy: {pos_accuracy}")

    def compare_velocity(self, analytical_velocity: np.ndarray):
        """
        Args:
            analytical_velocity (np.ndarray): analytical velocity
        Returns:
            (float): velocity accuracy

        Compares the analytical velocity with the particle velocity
        """

        # work out the difference vector
        difference_vec = self.particle.velocity - analytical_velocity
        diff = np.linalg.norm(difference_vec)

        analytical_vel_mag = np.linalg.norm(analytical_velocity)

        vel_accuracy = 1 - (diff / analytical_vel_mag)

        print(f"Analytical velocity: {analytical_velocity}")
        print(f"Particle velocity: {self.particle.velocity}")
        print(f"Velocity accuracy: {vel_accuracy}")

    def test_euler(self):
        """
        Tests the euler method accuracy
        """

        self.create_particle()
        self.particle.set_method(UpdateMethod.EULER)

        # evolvle the particle for 10 seconds with 1000 steps
        self.steps = 1000
        self.dt = 10 / self.steps
        for _ in range(self.steps):
            self.particle.update(self.dt)

        # get the analytical solution
        analytical_position, analytical_velocity = self.analyitical_solution(
            10)

        print('\n')
        print("=" * 10 + " Euler " + "=" * 10)
        self.compare_position(analytical_position)
        print('\n')
        self.compare_velocity(analytical_velocity)

        # check the position within 1% accuracy
        self.assertTrue(np.allclose(self.particle.position,
                                    analytical_position, rtol=0.01))

        # check the velocity within 1% accuracy
        self.assertTrue(np.allclose(self.particle.velocity,
                                    analytical_velocity, rtol=0.01))

    def test_verlet(self):
        """
        Tests the verlet method accuracy
        """

        self.create_particle()
        self.particle.set_method(UpdateMethod.VERLET)

        # evolvle the particle for 10 seconds with 1000 steps
        self.steps = 1000
        self.dt = 10 / self.steps
        for _ in range(self.steps):
            self.particle.update(self.dt)

        # get the analytical solution
        analytical_position, analytical_velocity = self.analyitical_solution(
            10)

        print('\n')
        print("=" * 10 + " Verlet " + "=" * 10)
        self.compare_position(analytical_position)
        print('\n')
        self.compare_velocity(analytical_velocity)

        # check the position within 1% accuracy
        self.assertTrue(np.allclose(self.particle.position,
                                    analytical_position, rtol=0.01))

    def test_euler_cramer(self):
        """
        Tests the euler-cramer method accuracy
        """

        self.create_particle()
        self.particle.set_method(UpdateMethod.EULER_CRAMER)

        # evolvle the particle for 10 seconds with 1000 steps
        self.steps = 1000
        self.dt = 10 / self.steps
        for _ in range(self.steps):
            self.particle.update(self.dt)

        # get the analytical solution
        analytical_position, analytical_velocity = self.analyitical_solution(
            10)

        print('\n')
        print("=" * 10 + " Euler-Cramer " + "=" * 10)
        self.compare_position(analytical_position)
        print('\n')
        self.compare_velocity(analytical_velocity)

        # check the position within 1% accuracy
        self.assertTrue(np.allclose(self.particle.position,
                                    analytical_position, rtol=0.01))

        # check the velocity within 1% accuracy
        self.assertTrue(np.allclose(self.particle.velocity,
                                    analytical_velocity, rtol=0.01))
