from __future__ import annotations
import numpy as np
from enum import Enum
from typing import Callable


class UpdateMethod(Enum):
    EULER = 1
    VERLET = 2
    EULER_CROMER = 3


class Particle:
    """
    A class that represents a particle in a simulation.
    """

    def __init__(
        self,
        position: np.ndarray = np.array([0, 0, 0], dtype=float),
        velocity: np.ndarray = np.array([0, 0, 0], dtype=float),
        acceleration: np.ndarray = np.array([0, 0, 0], dtype=float),
        name: str = 'Ball',
        mass: float = 1.0,
        method: UpdateMethod = UpdateMethod.EULER
    ):
        self.init_position = position
        self.init_velocity = velocity
        self.first_acceleration = acceleration

        # convert numpy arrays to arrays of floats
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.acceleration = np.array(acceleration, dtype=float)
        self.last_acceleration = np.array(acceleration, dtype=float)

        self.name = name
        self.mass = mass
        self.G = 6.67408e-11

        # set the update method
        self._method = method

        # create a dictionary of update methods
        self._method_map: dict[UpdateMethod, Callable[[float], None]] = {
            UpdateMethod.EULER: self.euler_update,
            UpdateMethod.EULER_CROMER: self.euler_cromer_update,
            UpdateMethod.VERLET: self.verlet_update_velocity
        }

        self._bodies = []

    def reset(self) -> None:
        """
        Args:
            None
        Returns:
            None

        Resets the particle to its initial state.
        """
        self.position = self.init_position
        self.velocity = self.init_velocity
        self.acceleration = self.first_acceleration
        self.last_acceleration = self.first_acceleration

    def set_method(self, method: UpdateMethod) -> None:
        """
        Args:
            method (UpdateMethod): The method to use to update the particle.
        Returns:
            None

        Sets the method used to update the particle.
        """
        self._method = method

    def init_acceleration(self) -> None:
        """
        Args:
            None
        Returns:
            None

        Initializes the acceleration of the particle.
        """
        accel = self._calculate_acceleration(self._bodies)
        self.acceleration = accel
        self.last_acceleration = accel

    def set_bodies(self, bodies: list[Particle]) -> None:
        """
        Args:
            bodies (list[Particle]): A list of particles that are exerting a
            gravitational force on the particle.
        Returns:
            None

        Sets the bodies that are exerting a gravitational force on the particle.
        """
        self._bodies = bodies

    @property
    def method(self) -> UpdateMethod:
        return self._method

    def euler_update(self, deltaT: float) -> None:
        """
        Args:
            deltaT (float): The amount of time to update the particle by.
        Returns:
            None

        Updates the position and velocity of the particle by the amount of time
        using the Euler method.
        """
        self.position += self.velocity * deltaT
        self.velocity += self.acceleration * deltaT

    def verlet_update_position(self, deltaT: float) -> None:
        """
        Args:
            deltaT (float): The amount of time to update the particle by.
        Returns:
            None

        Updates the position and velocity of the particle by the amount of time
        using the Verlet method.
        """
        self.position += self.velocity * deltaT + 0.5 * self.acceleration * deltaT**2

    def verlet_update_velocity(self, deltaT: float) -> None:
        """
        Args:
            deltaT (float): The amount of time to update the particle by.
        Returns:
            None

        Updates the position and velocity of the particle by the amount of time
        using the Verlet method.
        """
        self.velocity += 0.5 * (self.acceleration +
                                self.last_acceleration) * deltaT

    def euler_cromer_update(self, deltaT: float) -> None:
        """
        Args:
            deltaT (float): The amount of time to update the particle by.
        Returns:
            None

        Updates the position and velocity of the particle by the amount of time
        using the Euler-Cromer method.
        """
        self.velocity += self.acceleration * deltaT
        self.position += self.velocity * deltaT

    def update(self, deltaT: float) -> None:
        """
        Args:
            deltaT (float): The amount of time to update the particle by.
        Returns:
            None

        Updates the position and velocity of the particle by the amount of time
        """
        self._method_map[self._method](deltaT)

    def update_gravitational_acceleration(self) -> None:
        """
        Args:
            None
        Returns:
            None

        Updates the acceleration of the particle due to the gravitational force
        of the bodies.
        """
        if len(self._bodies) == 0:
            return

        self.last_acceleration = self.acceleration

        self.acceleration = self._calculate_acceleration(self._bodies)

    def _calculate_acceleration(self, bodies: list[Particle]) -> np.ndarray:
        """
        Args:
            bodies (list[Particle]): A list of particles that are exerting a
            gravitational force on the particle.
        Returns:
            None

        Updates the acceleration of the particle due to the gravitational force
        of the bodies passed in.
        """
        total_acceleration = np.array([0, 0, 0], dtype=float)
        for body in bodies:
            acceleration = np.array([0, 0, 0], dtype=float)
            # calculate the distance between the two particles
            distance = np.linalg.norm(self.position - body.position)

            # calculate the gravitational force
            force = self.G * self.mass * body.mass / distance**2

            # calculate the direction of the force
            direction = (body.position - self.position) / distance

            # calculate the acceleration
            acceleration = force / self.mass * direction

            # add the acceleration to the total acceleration
            total_acceleration += acceleration

        # update the acceleration
        return total_acceleration

    @property
    def kinetic_energy(self) -> np.float64:
        """
        Args:
            None
        Returns:
            np.float64: The kinetic energy of the particle.
        """
        return 0.5 * self.mass * np.linalg.norm(self.velocity)**2

    @property
    def momentum(self) -> np.ndarray:
        """
        Args:
            None
        Returns:
            np.ndarray: The momentum of the particle.
        """
        return self.mass * self.velocity

    def potential_energy(self) -> float:
        """
        Args:
            bodies (list[Particle]): A list of particles that are exerting a
            gravitational force on the particle.
        Returns:
            np.float64: The potential energy of the particle.
        """
        potential = 0.0
        for body in self._bodies:
            # calculate the distance between the two particles
            distance = np.linalg.norm(self.position - body.position)

            # calculate the gravitational force
            potential = self.G * self.mass * body.mass / distance

        return -float(potential)

    def __str__(self):
        return "Particle: {0}, Mass: {1:.3e}, Position: {2}, \
                Velocity: {3}, Acceleration: {4}".format(
            self.name,
            self.mass,
            self.position,
            self.velocity,
            self.acceleration
        )

    def to_json(self):
        """
        Args:
            None
        Returns:
            dict: A dictionary containing the position, velocity,
            acceleration, name and mass of the particle.
        """
        return {
            'position': self.position.tolist(),
            'velocity': self.velocity.tolist(),
            'acceleration': self.acceleration.tolist(),
            'ke': self.kinetic_energy,
            'pe': self.potential_energy(),
            'momentum': self.momentum.tolist(),
            'name': self.name,
            'mass': self.mass,
        }
