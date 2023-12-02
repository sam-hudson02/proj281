from models.particle import Particle


class SolarSystem:
    def __init__(self, particles: list[Particle] = []):
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

    def get_state(self) -> dict[str, Particle]:
        state = {}
        for particle in self._particles.values():
            state[particle.name] = particle.to_json()
        return state
