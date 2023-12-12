import json
from datetime import datetime
from models.particle import UpdateMethod
from enum import Enum
import numpy as np


class Depth(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2


class SolarSystemConfig:
    """
    Parsed configuration file for the solar system simulation.
    """

    def __init__(self, raw: dict):
        self._raw = raw
        self.depth = self.parse_depth(self._raw.get('depth', 'low'))
        self.start_time = self.parse_start_time(self._raw.get('start_time',
                                                              ''))
        self.steps = self.parse_steps(self._raw.get('steps', '1000'))
        self.deltaT = self.parse_deltaT(self._raw.get('deltaT', '100.0'))
        self.method = self.parse_method(self._raw.get('method', 'euler'))
        self.particles = self.parse_particles(self._raw.get('particles', {}))
        self._raw_particles = self._raw.get('particles', {})
        self.log_interval = self.parse_log_interval(
            self._raw.get('log_interval', '100'))

    def parse_log_interval(self, log_interval: str) -> int:
        try:
            return int(log_interval)
        except ValueError:
            return 100

    def parse_particles(self, raw: dict) -> list[int]:
        raw_list = raw.get(self.depth.name.lower(), [])
        return [int(p) for p in raw_list]

    def parse_steps(self, steps: str) -> int:
        try:
            return int(steps)
        except ValueError:
            return 1000

    def parse_start_time(self, start_time: str) -> datetime:
        try:
            # parse data in format yyyy-mm-dd
            return datetime.strptime(start_time, '%Y-%m-%d')
        except ValueError:
            return datetime.now()

    def parse_deltaT(self, deltaT: str) -> float:
        try:
            return float(deltaT)
        except ValueError:
            return 100.0

    def parse_depth(self, depth: str) -> 'Depth':
        match depth.lower():
            case 'low':
                return Depth.LOW
            case 'medium':
                return Depth.MEDIUM
            case 'high':
                return Depth.HIGH
            case _:
                return Depth.LOW

    def parse_method(self, method: str) -> 'UpdateMethod':
        match method.lower():
            case 'euler':
                return UpdateMethod.EULER
            case 'verlet':
                return UpdateMethod.VERLET
            case 'euler_cromer':
                return UpdateMethod.EULER_CROMER
            case _:
                return UpdateMethod.EULER

    def to_dict(self) -> dict:
        return {
            'depth': self.depth.name.lower(),
            'start_time': self.start_time.strftime('%Y-%m-%d'),
            'steps': self.steps,
            'deltaT': self.deltaT,
            'method': self.method.name.lower(),
            'particles': self._raw_particles,
        }


class ProjectileConfig:
    """
    Parsed config for a Projectile Simulation.
    """

    def __init__(self, raw: dict):
        self._raw = raw
        self.deltaT = self.parse_deltaT(self._raw.get('deltaT', '0.01'))
        self.method = self.parse_method(self._raw.get('method', 'euler'))
        self.steps = self.parse_steps(self._raw.get('steps', '10000'))
        self.log_interval = self.parse_log_interval(
            self._raw.get('log_interval', '10'))
        self.gravity = self.parse_gravity(self._raw.get('gravity', '9.81'))
        self.mass = self.parse_mass(self._raw.get('mass', '1.0'))
        self.position: np.ndarray = self.parse_position(
            self._raw.get('position', ['0.0', '0.0', '0.0']))
        self.velocity: np.ndarray = self.parse_velocity(
            self._raw.get('velocity', ['50.0', '70.0', '0.0']))

    def parse_velocity(self, velocity: list) -> np.ndarray:
        try:
            return np.array([float(v) for v in velocity])
        except ValueError:
            return np.array([0.0, 0.0, 0.0])

    def parse_position(self, position: list) -> np.ndarray:
        try:
            return np.array([float(p) for p in position])
        except ValueError:
            return np.array([0.0, 0.0, 0.0])

    def parse_mass(self, mass: str) -> float:
        try:
            return float(mass)
        except ValueError:
            return 1.0

    def parse_gravity(self, gravity: str) -> float:
        try:
            g = float(gravity)
        except ValueError:
            g = 9.81
        if g < 0.0:
            return g
        else:
            return -g

    def parse_log_interval(self, log_interval: str) -> int:
        try:
            return int(log_interval)
        except ValueError:
            return 100

    def parse_deltaT(self, deltaT: str) -> float:
        try:
            return float(deltaT)
        except ValueError:
            return 100.0

    def parse_method(self, method: str) -> 'UpdateMethod':
        match method.lower():
            case 'euler':
                return UpdateMethod.EULER
            case 'verlet':
                return UpdateMethod.VERLET
            case 'euler_cromer':
                return UpdateMethod.EULER_CROMER
            case _:
                return UpdateMethod.EULER

    def parse_steps(self, steps: str) -> int:
        try:
            return int(steps)
        except ValueError:
            return 1000

    def to_dict(self) -> dict:
        return {
            'deltaT': self.deltaT,
            'method': self.method.name.lower(),
            'steps': self.steps,
            'log_interval': self.log_interval,
            'gravity': self.gravity,
            'mass': self.mass,
        }


class Config:
    """
    Parsed config for a Simulation.
    """

    def __init__(self, filename: str = 'config.json'):
        self._filename = filename
        self._raw = self._load_config()
        self.solar_system = SolarSystemConfig(
            self._raw.get('solar_system', {}))
        self.projectile = ProjectileConfig(
            self._raw.get('projectile', {}))
        self.save_config()

    def _load_config(self) -> dict:
        try:
            with open(self._filename, 'r') as f:
                self._config = json.load(f)
            return self._config
        except FileNotFoundError:
            with open(self._filename, 'w') as f:
                json.dump({}, f, indent=4)
            return {}

    def to_json(self) -> dict:
        return {
            'solar_system': self.solar_system.to_dict(),
            'projectile': self.projectile.to_dict(),
        }

    def save_config(self) -> None:
        with open(self._filename, 'w') as f:
            json.dump(self.to_json(), f, indent=4)
