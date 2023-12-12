from models.particle import Particle
from utils.config import ProjectileConfig
from utils.utils import log_progress
import numpy as np
import json


class ProjectileSim:
    """
    A class that represents a projectile simulation.

    Args:
        config (ProjectileConfig): The configuration for the simulation.
        output_file (str) (optional): The output file for the simulation.
    """

    def __init__(self, config: ProjectileConfig,
                 output_file: str | None = None):
        self.config = config
        self.particle = Particle(
            position=self.config.position,
            velocity=self.config.velocity,
            mass=self.config.mass,
            acceleration=np.array([0.0, self.config.gravity, 0.0]),
            method=self.config.method
        )
        self.deltaT = self.config.deltaT
        self.steps = self.config.steps
        self.log_interval = self.config.log_interval
        self._data = {}
        if output_file:
            self.output_file = output_file
        else:
            self.output_file = self._create_title()

    def advance(self) -> None:
        """
        Args:
            None
        Returns:
            None

        Advances the simulation by one step.
        """
        self.particle.update(self.deltaT)

    def _create_title(self) -> str:
        """
        Args:
            None
        Returns:
            title (str): The title of the output file.

        Generates a title for the output file based on the config.
        """
        title = f'{self.config.method.name.lower()}_'
        title += f'{self.config.steps}_'
        dt_str = str(self.config.deltaT).replace('.', '-')
        title += f'{dt_str}_'
        g_str = str(self.config.gravity).replace('.', '-')
        title += f'{g_str}_'
        m_str = str(self.config.mass).replace('.', '-')
        title += f'{m_str}'
        return title

    def save(self) -> str:
        """
        Args:
            None
        Returns:
            title (str): The title of the output file. 

        Saves the data to a json file.
        """
        print(f'Saving data to data/sims/projectile/{self.output_file}.json..')
        with open(f'data/sims/projectile/{self.output_file}.json', 'w') as f:
            json.dump(self._data, f)
        print('Data saved!')

        return self.output_file

    def run(self) -> tuple[str, dict]:
        """
        Args:
            None
        Returns:
            title (str): The title of the output file.
            data (dict): The data from the simulation.

        Runs the simulation.
        """

        print('Running simulation\n')
        for step in range(self.steps):
            self.advance()

            # Stop simulation if particle hits ground
            if self.particle.position[1] <= 0:
                print('Particle hit ground!')
                break

            if step % self.log_interval == 0:
                step_time = step * self.deltaT
                self._data[step_time] = {
                    "projectile": self.particle.to_json()
                }
                log_progress(step, self.steps)

        print('\nSimulation finished!')
        title = self.save()
        return title, self._data
