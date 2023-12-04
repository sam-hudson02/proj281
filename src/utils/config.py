import json
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.solar_system import Depth


class Config:
    def __init__(self, filename: str = 'config.json'):
        self._filename = filename
        self._raw = self._load_config()

    def _load_config(self) -> dict:
        with open(self._filename, 'r') as f:
            self._config = json.load(f)
        return self._config

    def get_particles(self, depth: 'Depth') -> list[int]:
        raw_list = self._raw['particles'][depth.name.lower()]
        return [int(x) for x in raw_list]
