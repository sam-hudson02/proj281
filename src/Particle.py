from __future__ import annotations
import numpy as np


class Particle:
    def __init__(
        self,
            position: np.ndarray = np.array([0, 0, 0], dtype=float),
            velocity: np.ndarray = np.array([0, 0, 0], dtype=float),
            acceleration: np.ndarray = np.array([0, -10, 0], dtype=float),
            name: str = 'Ball',
            mass: float = 1.0,
    ):
        # convert numpy arrays to arrays of floats
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.acceleration = np.array(acceleration, dtype=float)

        self.name = name
        self.mass = mass
        self.G = 6.67408e-11

    def update(self, deltaT):
        self.position += self.velocity * deltaT
        self.velocity += self.acceleration * deltaT

    def update_gravitational_acceleration(self, bodies: list[Particle]):
        """
        Updates the acceleration of the particle due to the gravitational force
        of the body passed in.
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
        self.acceleration = total_acceleration

    @property
    def kinetic_energy(self):
        return 0.5 * self.mass * np.linalg.norm(self.velocity)**2

    def __str__(self):
        return "Particle: {0}, Mass: {1:.3e}, Position: {2}, Velocity: {3}, Acceleration: {4}".format(
            self.name,
            self.mass,
            self.position,
            self.velocity,
            self.acceleration
        )

    def to_json(self):
        return {
            'position': self.position.tolist(),
            'velocity': self.velocity.tolist(),
            'acceleration': self.acceleration.tolist(),
            'name': self.name,
            'mass': self.mass
        }
