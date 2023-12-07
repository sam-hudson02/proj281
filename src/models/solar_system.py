from models.particle import Particle
import numpy as np


class SolarSystem:
    def __init__(self,
                 particles: list[Particle],
                 ) -> None:
        self._particles: dict[str, Particle] = {}
        for particle in particles:
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

    def get_system_energy(self) -> float:
        energy = self.get_system_kinetic_energy()
        energy += self.get_system_potential_energy()
        return energy

    def get_system_momentum(self) -> np.ndarray:
        momentum = np.array([0.0, 0.0, 0.0])
        for particle in self._particles.values():
            momentum += particle.momentum
        return momentum

    def get_system_potential_energy(self) -> float:
        total_potential = 0.0
        for particle in self._particles.values():
            other_particles_dict = self._particles.copy()
            other_particles_dict.pop(particle.name)
            other_particles = list(other_particles_dict.values())
            total_potential += particle.potential_energy(other_particles)
        return total_potential

    def get_system_kinetic_energy(self) -> float:
        total_kinetic = 0.0
        for particle in self._particles.values():
            total_kinetic += float(particle.kinetic_energy)
        return total_kinetic

    def get_state(self) -> dict[str, Particle]:
        state = {}
        for particle in self._particles.values():
            other_particles_dict = self._particles.copy()
            other_particles_dict.pop(particle.name)
            other_particles = list(other_particles_dict.values())
            state[particle.name] = particle.to_json(other_particles)
        sytem_info = {
            'energy': self.get_system_energy(),
            'momentum': self.get_system_momentum().tolist()
        }
        state['system_info'] = sytem_info
        return state
