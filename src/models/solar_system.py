from models.particle import Particle, UpdateMethod
import numpy as np


class SolarSystem:
    def __init__(self,
                 particles: list[Particle],
                 method: UpdateMethod
                 ) -> None:
        self._particles: dict[str, Particle] = {}
        self._method = method
        for particle in particles:
            self.add_particle(particle)

    def reset(self) -> None:
        for particle in self._particles.values():
            particle.reset()
        for particle in self._particles.values():
            particle.init_acceleration()

    def add_particle(self, particle: Particle) -> None:
        self._particles[particle.name] = particle

    def remove_particle(self, name: str) -> None:
        del self._particles[name]

    def get_particle(self, name: str) -> Particle:
        return self._particles[name]

    def set_method(self, method: UpdateMethod) -> None:
        self._method = method
        for particle in self._particles.values():
            particle.set_method(method)

    def advance(self, dt: float) -> None:
        if self._method == UpdateMethod.VERLET:
            # Verlet requires the position to be updated first so the
            # acceleration can be calculated for the next step
            for particle in self._particles.values():
                particle.verlet_update_position(dt)
        for particle in self._particles.values():
            particle.update_gravitational_acceleration()
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
            total_potential += particle.potential_energy()
        return total_potential

    def get_system_kinetic_energy(self) -> float:
        total_kinetic = 0.0
        for particle in self._particles.values():
            total_kinetic += float(particle.kinetic_energy)
        return total_kinetic

    def get_state(self) -> dict[str, Particle]:
        state = {}
        for particle in self._particles.values():
            state[particle.name] = particle.to_json()
        sytem_info = {
            'energy': self.get_system_energy(),
            'momentum': self.get_system_momentum().tolist()
        }
        state['system_info'] = sytem_info
        return state
