import json
from datetime import datetime
from models.particle import UpdateMethod
from enum import Enum


class Depth(Enum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2


class SolarSystemConfig:
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


class Config:
    def __init__(self, filename: str = 'config.json'):
        self._filename = filename
        self._raw = self._load_config()
        self.solar_system = SolarSystemConfig(
            self._raw.get('solar_system', {}))
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
        }

    def save_config(self) -> None:
        with open(self._filename, 'w') as f:
            json.dump(self.to_json(), f, indent=4)
