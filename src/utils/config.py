import json
from datetime import datetime
from models.particle import UpdateMethod
from enum import Enum
import numpy as np


class Depth(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2


class ConfigMeta:
    """
    Base class for configuration files.
    """

    def __init__(self, raw: dict) -> None:
        self._raw = raw

    def parse_float(self, key: str, default: float) -> float:
        try:
            return float(self._raw.get(key, default))
        except ValueError:
            return default

    def parse_int(self, key: str, default: int) -> int:
        try:
            return int(self._raw.get(key, default))
        except ValueError:
            return default

    def parse_str(self, key: str, default: str) -> str:
        return self._raw.get(key, default)

    def parse_depth(self, key: str, default: Depth) -> Depth:
        try:
            depth = self._raw.get(key, default.name)
            match depth.lower():
                case 'low':
                    return Depth.LOW
                case 'medium':
                    return Depth.MEDIUM
                case 'high':
                    return Depth.HIGH
                case _:
                    return default
        except KeyError:
            return default

    def parse_method(self, key: str, default: UpdateMethod) -> UpdateMethod:
        try:
            method = self._raw.get(key, default.name)
            match method.lower():
                case 'euler':
                    return UpdateMethod.EULER
                case 'verlet':
                    return UpdateMethod.VERLET
                case 'euler_cromer':
                    return UpdateMethod.EULER_CROMER
                case _:
                    return UpdateMethod.EULER
        except KeyError:
            return default

    def parse_datetime(self, key: str, default: datetime) -> datetime:
        try:
            start_time: str = self._raw[key]

            # parse data in format yyyy-mm-dd
            return datetime.strptime(start_time, '%Y-%m-%d')
        except KeyError or ValueError:
            return default

    def parse_particles(self, key: str, default: dict) -> tuple[
            list[int],
            list[int],
            list[int]]:

        raw_particles = self._raw.get(key, default)
        try:
            low = [int(p) for p in raw_particles['low']]
            medium = [int(p) for p in raw_particles['medium']]
            high = [int(p) for p in raw_particles['high']]
            return low, medium, high

        except KeyError or ValueError:
            return [], [], []

    def parse_vector(self, key: str, default: np.ndarray) -> np.ndarray:
        try:
            return np.array(self._raw.get(key, default))
        except ValueError:
            return default


class EarthOrbitConfig(ConfigMeta):
    """
    Parsed configuration file for the earth orbit simulation.
    """

    def __init__(self, raw: dict) -> None:
        self._raw = raw
        super().__init__(raw)
        self.radius = self.parse_float('radius', 15000000.0)
        self.mass = self.parse_float('mass', 500.0)
        self.deltaT = self.parse_float('deltaT', 100.0)
        self.method = self.parse_method('method', UpdateMethod.EULER)
        self.log_interval = self.parse_int('log_interval', 100)

    def to_dict(self) -> dict:
        return {
            'radius': self.radius,
            'mass': self.mass,
            'deltaT': self.deltaT,
            'method': self.method.name.lower(),
            'log_interval': self.log_interval
        }


class SolarSystemConfig(ConfigMeta):
    """
    Parsed configuration file for the solar system simulation.
    """

    def __init__(self, raw: dict):
        self._raw = raw
        super().__init__(raw)
        self.depth = self.parse_depth('depth', Depth.LOW)
        self.start_time = self.parse_datetime('start_time', datetime.now())
        self.steps = self.parse_int('steps', 1000)
        self.deltaT = self.parse_float('deltaT', 100.0)
        self.method = self.parse_method('method', UpdateMethod.EULER)
        self.log_interval = self.parse_int('log_interval', 100)
        particles = self.parse_particles('particles', {
            'low': [],
            'medium': [],
            'high': []
        })
        self.low_particles = particles[0]
        self.medium_particles = particles[1]
        self.high_particles = particles[2]
        self.particles = self.get_particles()

    def get_particles(self) -> list[int]:
        if self.depth == Depth.LOW:
            return self.low_particles
        elif self.depth == Depth.MEDIUM:
            all = self.low_particles + self.medium_particles
            # remove duplicates
            return list(dict.fromkeys(all))
        elif self.depth == Depth.HIGH:
            all = self.low_particles + self.medium_particles + self.high_particles
            return list(dict.fromkeys(all))
        else:
            return []

    def to_dict(self) -> dict:
        return {
            'depth': self.depth.name.lower(),
            'start_time': self.start_time.strftime('%Y-%m-%d'),
            'steps': self.steps,
            'deltaT': self.deltaT,
            'method': self.method.name.lower(),
            'particles': {
                'low': self.low_particles,
                'medium': self.medium_particles,
                'high': self.high_particles
            },
        }


class ProjectileConfig(ConfigMeta):
    """
    Parsed config for a Projectile Simulation.
    """

    def __init__(self, raw: dict):
        self._raw = raw
        self.deltaT = self.parse_float('deltaT', 0.01)
        self.method = self.parse_method('method', UpdateMethod.EULER)
        self.steps = self.parse_int('steps', 1000)
        self.log_interval = self.parse_int('log_interval', 10)
        self.gravity = self.parse_float('gravity', 9.81)
        self.mass = self.parse_float('mass', 1.0)
        default_position = np.array([0.0, 0.0, 0.0])
        self.position = self.parse_vector('position', default_position)
        default_velocity = np.array([20.0, 50.0, 0.0])
        self.velocity = self.parse_vector('velocity', default_velocity)

    def to_dict(self) -> dict:
        return {
            'deltaT': self.deltaT,
            'method': self.method.name.lower(),
            'steps': self.steps,
            'log_interval': self.log_interval,
            'gravity': self.gravity,
            'mass': self.mass,
            'position': self.position.tolist(),
            'velocity': self.velocity.tolist()
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
        self.earth_orbit = EarthOrbitConfig(
            self._raw.get('earth_orbit', {}))
        self.save_config()

    def _load_config(self) -> dict:
        try:
            with open(self._filename, 'r') as f:
                self._config = json.load(f)
            return self._config
        except FileNotFoundError or json.decoder.JSONDecodeError:
            with open(self._filename, 'w') as f:
                json.dump({}, f, indent=4)
            return {}

    def to_json(self) -> dict:
        return {
            'earth_orbit': self.earth_orbit.to_dict(),
            'solar_system': self.solar_system.to_dict(),
            'projectile': self.projectile.to_dict(),
        }

    def save_config(self) -> None:
        with open(self._filename, 'w') as f:
            json.dump(self.to_json(), f, indent=4)
