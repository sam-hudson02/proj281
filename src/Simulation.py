import numpy as np
from Particle import Particle
from solar_system import SolarSystem
import json
import sys
import time


def load_particles(filename: str) -> list[Particle]:
    particles = []
    with open(filename, 'r') as f:
        data = json.load(f)
        for name, particle_data in data.items():
            position = np.array(particle_data['position'])
            velocity = np.array(particle_data['velocity'])
            mass = particle_data['mass']
            particles.append(
                Particle(
                    position=position,
                    velocity=velocity,
                    mass=mass,
                    name=name
                )
            )
    return particles


def log_progress(step: int, total_steps: int,
                 start_time: float | None = None) -> None:
    percent = step / total_steps * 100
    # clear the current line
    print('\r', end='')
    # print the progress bar
    bar = f"[{'=' * int(percent / 10):10s}] {percent:.1f}%"
    if start_time is not None:
        elapsed_time = time.time() - start_time
        estimated_time = elapsed_time / (step + 1) * (total_steps - step - 1)
        elapsed_string = f"Elapsed: {elapsed_time:.1f}s"
        remaining_string = f"Remaining: {estimated_time:.1f}s"
        print(
            f"{bar} {elapsed_string} {remaining_string}",
            end=''
        )
    else:
        print(bar, end='')
    # flush the output buffer
    sys.stdout.flush()


def simulate(sol: SolarSystem, t: int | float | None = None,
             dt: float = 1.0, steps: int = 1000,
             logging: bool = True, log_interval: int = 100) -> None:
    if t is not None:
        steps = int(t / dt)
    start_time = time.time()
    log = {}
    for step in range(steps):
        log_progress(step, steps, start_time)
        if logging and step % log_interval == 0:
            info = sol.get_state()
            step_time = step * dt
            log[step_time] = info
        sol.advance(dt)
    if logging:
        save_log(log, './data/log.json')


def save_log(log: dict, filename: str) -> None:
    with open(filename, 'w') as f:
        json.dump(log, f, indent=4)


def main():
    particles = load_particles('./data/nasa_data.json')
    print(particles[0])
    solar_system = SolarSystem(particles)
    year = (365.25 * 24 * 60 * 60) / 2
    dt = 100.0
    simulate(solar_system, t=year, dt=dt)
    print(particles[0])


if __name__ == '__main__':
    main()
