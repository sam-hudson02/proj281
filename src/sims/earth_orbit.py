from models.particle import Particle, UpdateMethod
import numpy as np
import time
from utils.config import EarthOrbitConfig
from utils.utils import log_progress
import os
import json


class EarthOrbit:
    def __init__(self, config: EarthOrbitConfig,
                 output: str | None = None) -> None:
        self._config = config
        self._deltaT = self._config.deltaT
        self._method = self._config.method
        self.radius = self._config.radius
        self.earth = Particle(name='Earth', mass=5.972e24, method=self._method)
        self.mass = self._config.mass
        self.G = 6.67408e-11
        self.satellite = self.create_satellite(self.radius)

        # run simulation for at least one period
        self.steps = int(self.period() / self._deltaT) + 1
        self._data = {}
        self.init_orbit()
        if output is not None:
            self._title = output
        else:
            self._title = self._create_title()

    def set_method(self, method: UpdateMethod):
        """
        Sets the update method.
        """
        self._method = method
        self.earth.set_method(method)
        self.satellite.set_method(method)

    def _create_title(self):
        mass_str = f'{self.mass:.2e}'.replace('.', '-')
        radius_str = f'{self.radius:.2e}'.replace('.', '-')
        deltaT_str = f'{self._deltaT:.2e}'.replace('.', '-')
        return f'{mass_str}_{radius_str}_{deltaT_str}'

    def period(self):
        """
        Calculates the period of the satellite.
        """
        p = 2 * np.pi * self.radius / self.orbital_velocity(self.radius)
        return p

    def orbital_velocity(self, r: float):
        """
        Calculates the orbital velocity of a satellite around the Earth.
        """
        return (self.G * self.earth.mass / r) ** 0.5

    def create_satellite(self, r: float):
        """
        Creates a satellite around the Earth.
        """
        position = np.array([r, 0, 0])
        velocity = np.array([0, self.orbital_velocity(r), 0])
        return Particle(name='Satellite',
                        mass=self.mass,
                        position=position,
                        velocity=velocity,
                        method=self._method)

    def init_orbit(self):
        """
        Initializes the orbit of the satellite around the Earth.
        """
        self.earth.set_bodies([self.satellite])
        self.satellite.set_bodies([self.earth])
        self.earth.init_acceleration()
        self.satellite.init_acceleration()

    def update(self):
        """
        Updates the position and velocity of the satellite.
        """
        if self._method == UpdateMethod.VERLET:
            self.earth.verlet_update_position(self._deltaT)
            self.satellite.verlet_update_position(self._deltaT)
        self.earth.update_gravitational_acceleration()
        self.satellite.update_gravitational_acceleration()
        self.earth.update(self._deltaT)
        self.satellite.update(self._deltaT)

    def save_data(self):
        os.makedirs('data/sims/earth_orbit/', exist_ok=True)
        with open(f'data/sims/earth_orbit/{self._title}.json', 'w') as f:
            json.dump(self._data, f, indent=4)

    def get_system_energy(self):
        """
        Returns the system energy.
        """
        pe = self.earth.potential_energy() + self.satellite.potential_energy()
        ke = self.earth.kinetic_energy + self.satellite.kinetic_energy
        return pe + ke

    def get_system_momentum(self):
        """
        Returns the system momentum.
        """
        return list(self.earth.momentum + self.satellite.momentum)

    def get_system_info(self):
        """
        Returns the system information.
        """
        info = {
            'energy': self.get_system_energy(),
            'momentum': self.get_system_momentum()
        }
        return info

    def run(self):
        """
        Runs the simulation.
        """
        start = time.time()

        print(f'Running simulation for {self.steps} steps...')
        for step in range(self.steps):
            self.update()
            if step % self._config.log_interval == 0:
                log_progress(step, self.steps, start)
                step_time = step * self._deltaT
                self._data[step_time] = {
                    'satellite': self.satellite.to_json(),
                    '399': self.earth.to_json(),
                    'system_info': self.get_system_info()
                }

        print(f'\nSimulation finished in {time.time() - start:.2f} seconds.')

        self.save_data()

        return self._title, self._data
