from models.solar_system import SolarSystem
from models.particle import Particle
from utils.config import SolarSystemConfig
from utils.nasa_data import NasaQuery
from utils.utils import log_progress
import numpy as np
import time
import json


class SolarSystemSim:
    def __init__(self, config: SolarSystemConfig,
                 save_file: str | None = None):
        self._ts: float = 0.0
        self._config = config
        self._deltaT = self.get_deltaT()
        self._particle_ids = self._config.particles
        self._start_time = self._config.start_time
        self._steps = self._config.steps
        self._nq = NasaQuery(start_time=self._start_time)
        self._particles = self.load_particles()
        self._sim_init_time = time.time()
        self._solar_system = SolarSystem(self._particles)
        self._save_file = save_file
        self._data = {}

    def get_deltaT(self) -> float:
        return self._config.deltaT

    def load_particles(self) -> list[Particle]:
        particles = []
        particles_data = self._nq.get_data(self._particle_ids)
        ts = list(
            particles_data[self._particle_ids[0]].vector_data.keys())[0]
        self._ts = float(ts)
        for particle_id, data in particles_data.items():
            print(f'Loading particle {particle_id}...')
            position = np.array(data.vector_data[ts]['position'])
            velocity = np.array(data.vector_data[ts]['velocity'])
            mass = data.object_data.mass
            name = particle_id
            particle = Particle(position=position,
                                velocity=velocity,
                                mass=mass,
                                name=str(name))
            particles.append(particle)
            # list masses
            print(f'Particle {particle_id} mass: {mass}')
        return particles

    def advance(self) -> None:
        self._solar_system.advance(self._deltaT)

    def save_data(self) -> None:
        start_str = self._start_time.strftime('%Y-%m-%d')
        title = 'sol_'
        title += f'{start_str}_'
        title += f'{self._steps}_'
        dt_str = str(self._deltaT).replace('.', ',')
        title += f'{dt_str}_'
        title += f'{self._config.method.name.lower()}'
        if self._save_file is not None:
            title = self._save_file
        print(f'Saving data to {title}.json')
        with open(f'data/{title}.json', 'w') as f:
            json.dump(self._data, f, indent=4)

    def run(self) -> None:
        print('\n')
        print('Running simulation...')
        for step in range(self._steps):
            self.advance()

            step_time = self._ts + (step * self._deltaT)

            if step % self._config.log_interval == 0:
                log_progress(step, self._steps, self._sim_init_time)
                self._data[step_time] = self._solar_system.get_state()

        print('\n')
        print('Saving data...')
        self.save_data()
