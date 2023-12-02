from numpy.core.multiarray import ndarray
from particle import Particle
import numpy as np


class Planet(Particle):
    def __init__(self, position: np.ndarray, velocity: np.ndarray,
                 acceleration: np.ndarray, name: str, mass: float,
                 radius: float, axis: np.ndarray, tangential_velocity: float,
                 null_island: np.ndarray):
        super().__init__(position, velocity, acceleration, name, mass)
        self.radius: float = radius

        # axis is a normalized vector pointing to the north pole
        self.axis: ndarray = axis

        self.north_pole: ndarray = radius * axis + position
        self.south_pole: ndarray = -radius * axis + position

        self.tangential_velocity: float = tangential_velocity

        # null island is a vector pointing to 0deg, 0deg
        self.null_island: ndarray = null_island

    def update(self, deltaT):
        # update null island
        null_island_angle = self.tangential_velocity * deltaT / self.radius

        # create rotation matrix
        null_island_rotation_matrix = np.array(
            [[np.cos(null_island_angle), -np.sin(null_island_angle)],
             [np.sin(null_island_angle), np.cos(null_island_angle)]])

        # rotate null island vector
        self.null_island = np.matmul(null_island_rotation_matrix,
                                     self.null_island)

        return super().update(deltaT)
