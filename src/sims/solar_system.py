from models.solar_system import SolarSystem
from models.particle import Particle
from utils.config import SolarSystemConfig
from utils.nasa_data import NasaQuery
from utils.utils import log_progress
import time
import json


class SolarSystemSim:
    """
    Args:
        config (SolarSystemConfig): The configuration for the simulation.
        save_file (str) (optional): The output file for the simulation.

    A class that represents a solar system simulation.
    """

    def __init__(self, config: SolarSystemConfig,
                 save_file: str | None = None):
        self._ts: float = 0.0
        self._config = config
        self._method = self._config.method
        self._deltaT = self.get_deltaT()
        self._particle_ids = self._config.particles
        self._start_time = self._config.start_time
        self._steps = self._config.steps
        self._nq = NasaQuery(start_time=self._start_time)
        self._particles = self.load_particles()
        self._sim_init_time = time.time()
        self._solar_system = SolarSystem(self._particles, self._method)
        if save_file is not None:
            self._save_file = save_file
        else:
            self._save_file = self._create_title()
        self._data = {}

    def get_deltaT(self) -> float:
        return self._config.deltaT

    def load_particles(self) -> list[Particle]:
        """
        Args:
            None
        Returns:
            particles (list[Particle]): A list of particles.

        Initializes the particles in the simulation using NASA data
        as the initial state.
        """

        particles = []
        particles_data = self._nq.get_data(self._particle_ids)

        # get timestamp from first particle
        self._ts = particles_data[self._particle_ids[0]].ts

        for particle_id, data in particles_data.items():
            print(f'Loading particle {particle_id}...')

            position = data.vector_data.position
            velocity = data.vector_data.velocity
            mass = data.object_data.mass
            name = particle_id

            particle = Particle(position=position,
                                velocity=velocity,
                                mass=mass,
                                name=str(name),
                                method=self._method)
            particles.append(particle)

        for particle in particles:
            other_particles = particles.copy()
            other_particles.remove(particle)
            particle.set_bodies(other_particles)

        for particle in particles:
            particle.init_acceleration()

        return particles

    def reset(self) -> None:
        """
        Args:
            None
        Returns:
            None

        Resets the simulation.
        """
        self._solar_system.reset()

    def advance(self) -> None:
        """
        Args:
            None
        Returns:
            None

        Advances the simulation by one step.
        """
        self._solar_system.advance(self._deltaT)

    def _create_title(self) -> str:
        """
        Args:
            None
        Returns:
            title (str): The title of the output file.

        Generates a title for the output file based on the config.
        """
        start_str = self._start_time.strftime('%Y-%m-%d')
        title = f'{start_str}_'
        title += f'{self._steps}_'
        dt_str = str(self._deltaT).replace('.', '-')
        title += f'{dt_str}_'
        title += f'{self._config.method.name.lower()}'
        return title

    def save_data(self) -> str:
        """
        Args:
            None
        Returns:
            title (str): The title of the output file.

        Saves the simulation data to a json file.
        """
        print(f'Saving data to {self._save_file}.json')
        with open(f'data/sims/solarsystem/{self._save_file}.json', 'w') as f:
            json.dump(self._data, f, indent=4)
        return self._save_file

    def run(self) -> tuple[str, dict]:
        """
        Args:
            None
        Returns:
            title (str): The title of the output file.
            data (dict): The simulation data.

        Runs the simulation.
        """

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
        title = self.save_data()

        return title, self._data
