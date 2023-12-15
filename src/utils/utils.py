import numpy as np
import time
import sys
import json
import os
import pandas as pd


def setup_folders() -> None:
    """
    Args:
        None
    Returns:
        None

    Creates the folders for the data and plots.
    """
    if not os.path.exists('plots'):
        os.makedirs('plots')
    if not os.path.exists('data/sims/solarsystem'):
        os.makedirs('data/sims/solarsystem')
    if not os.path.exists('data/sims/projectile'):
        os.makedirs('data/sims/projectile')
    if not os.path.exists('data/nasa_cache'):
        os.makedirs('data/nasa_cache')


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


def log_progress(step: int, total_steps: int,
                 start_time: float | None = None) -> None:
    """
    Args:
        step (int): The current step.
        total_steps (int): The total number of steps.
        start_time (float | None): The time the simulation started.
    Returns:
        None

    Prints a progress bar to the console.
    """

    percent = step / total_steps * 100

    # clear the current line
    print('\r', end='')

    # make the progress bar
    bar = f"[{'=' * int(percent / 10):10s}] {percent:.1f}%"

    # add the time information
    if start_time is not None:
        elapsed_time = time.time() - start_time
        estimated_time = elapsed_time / (step + 1) * (total_steps - step - 1)
        elapsed_string = f"Elapsed: {elapsed_time:.1f}s"
        remaining_string = f"Remaining: {estimated_time:.1f}s"
        print(
            f"{bar} {elapsed_string} {remaining_string}",
            end=''
        )
    else:
        print(bar, end='')

    # flush the output buffer
    sys.stdout.flush()


def load_data(filename: str = 'data/log.json'):
    with open(filename) as f:
        data = json.load(f)
    return data


def vec_to_str(vec: np.ndarray, unit: str | None = None) -> str:
    """
    Args:
        vec (np.ndarray): The vector to convert.
    Returns:
        str: The string representation of the vector.

    Converts a vector to a string with 4 significant figures.
    Uses scientific notation if the number is too small / large.
    """
    if unit is None:
        return f"({vec[0]:.2e}, {vec[1]:.2e}, {vec[2]:.2e})"
    else:
        return f"({vec[0]:.2e} {unit}, {vec[1]:.2e} {unit}, {vec[2]:.2e} {unit})"


def percent_to_str(percent: float) -> str:
    # 3 significant figures

    # format to x 10^y
    if percent == 0:
        return '0.00 \%'
    elif percent < 0.01:
        return f"{percent:.2e} \%"
    else:
        return f"{percent:.3f} \%"


planets: list[str] = ['199', '299', '399', '499', '599', '699', '799', '899']
