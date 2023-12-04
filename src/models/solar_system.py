from models.particle import Particle, UpdateMethod
from enum import Enum
from utils.config import Config
from datetime import datetime
from utils.nasa_data import NasaQuery


class Depth(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class SolarSystem:
    def __init__(self, config: Config,
                 depth: Depth = Depth.LOW,
                 update_method: UpdateMethod = UpdateMethod.EULER,
                 start_date: datetime = datetime.now()) -> None:
        self._particles = {}
        self._config = config
        self._depth = depth
        self._particle_id_list = self._config.get_particles(self._depth)
        self._start_date = start_date
        self._nq = NasaQuery()
        particle_datas = self._nq.get_data(self._particle_id_list)
        for particle_id, particle_data in particle_datas.items():
            ts = list(particle_data.vector_data.keys())[0]
            position = particle_data.vector_data[ts]['position']
            velocity = particle_data.vector_data[ts]['velocity']
            particle = Particle(position, velocity, name=particle_id,
                                mass=particle_data.object_data.mass,
                                method=update_method)
            self.add_particle(particle)

    def add_particle(self, particle: Particle) -> None:
        self._particles[particle.name] = particle

    def remove_particle(self, name: str) -> None:
        del self._particles[name]

    def get_particle(self, name: str) -> Particle:
        return self._particles[name]

    def advance(self, dt: float) -> None:
        for particle in self._particles.values():
            other_particles_dict = self._particles.copy()
            other_particles_dict.pop(particle.name)
            other_particles = list(other_particles_dict.values())
            particle.update_gravitational_acceleration(other_particles)
            particle.update(dt)

    def get_state(self) -> dict[str, Particle]:
        state = {}
        for particle in self._particles.values():
            state[particle.name] = particle.to_json()
        return state
