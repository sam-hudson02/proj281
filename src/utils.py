import numpy as np


def cart_to_polar(cart: np.ndarray) -> np.ndarray:
    """
    Converts a cartesian vector to a polar vector in 3D space.
    """
    r = np.linalg.norm(cart)
    theta = np.arccos(cart[2] / r)
    phi = np.arctan2(cart[1], cart[0])
    return np.array([r, theta, phi])


def vec_to_sun(sun: np.ndarray, particle: np.ndarray) -> np.ndarray:
    """
    Returns the vector from the sun to the particle.
    """
    return sun - particle
