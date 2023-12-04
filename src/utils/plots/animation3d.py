from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from utils.utils import planets
from plots.prep_data import make_3d_data
from datetime import datetime
import time


def get_lines(ax, planets_data: dict, i: int, style: dict[str, str]):
    lines = []
    for planet, planet_data in planets_data.items():
        planet_x, planet_y, planet_z = planet_data

        # create trajectory arrays
        planet_x = planet_x[:i+1]
        planet_y = planet_y[:i+1]
        planet_z = planet_z[:i+1]

        # create point arrays
        planet_point_x = planet_x[-1]
        planet_point_y = planet_y[-1]
        planet_point_z = planet_z[-1]

        # plot trajectory
        line1 = ax.plot(planet_x, planet_y, planet_z,
                        label=planet, linewidth=0.5,
                        color=style[planet])

        # plot point
        line2 = ax.plot(planet_point_x, planet_point_y, planet_point_z,
                        marker='o', markersize=5,
                        color=style[planet])

        # add lines to list
        lines.append(line1[0])
        lines.append(line2[0])

    # return lines as tuple
    return tuple(lines)


def animation_3d(data: dict, frames: int = 24 * 60,
                 filename: str = 'animation_3d.gif'):

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')

    planets_data = {}

    for planet in planets:
        planet_x, planet_y, planet_z = make_3d_data(data, planet)
        planets_data[planet] = (planet_x, planet_y, planet_z)

    sun_x, sun_y, sun_z = make_3d_data(data, 'sun')
    planets_data['sun'] = (sun_x, sun_y, sun_z)

    plt.title('Earth orbiting the sun')

    style = {
        "sun": "yellow",
        "mercury": "grey",
        "venus": "orange",
        "earth": "blue",
        "mars": "red",
        "jupiter": "brown",
        "saturn": "yellow",
        "uranus": "cyan",
        "neptune": "purple"
    }

    def animate(i):
        lines = []
        print(i)
        ax.clear()

        lim = 2e11
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)

        lines = get_lines(ax, planets_data, i, style)

        # display date
        keys = data.keys()
        secs: float = float(list(keys)[i])
        date = secs + time.time()
        date_time = datetime.fromtimestamp(date)
        date_str = date_time.strftime("%Y-%m")
        ax.text2D(0.05, 0.95, date_str, transform=ax.transAxes, color='black')

        # return lines as tuple
        return tuple(lines)

    anim = FuncAnimation(fig, animate, interval=1,
                         blit=True, frames=frames, repeat=True)
    anim.save(f'plots/{filename}.gif',
              writer=PillowWriter(fps=24), dpi=200)
