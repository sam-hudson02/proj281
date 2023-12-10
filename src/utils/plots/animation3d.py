from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from utils.utils import planets
from utils.plots.prep_data import SimData
from utils.utils import log_progress
from datetime import datetime
import time


def animation_3d(data: SimData, frames: int = 24 * 60,
                 filename: str = 'animation_3d'):

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')

    start = time.time()

    print('Creating animation...')

    # use dark style
    plt.style.use('ggplot')

    planets_data = {}

    for planet in planets:
        planet_x, planet_y, planet_z = data.position(planet)
        planets_data[planet] = (planet_x, planet_y, planet_z)

    sun_x, sun_y, sun_z = data.position('10')
    planets_data['10'] = (sun_x, sun_y, sun_z)

    plt.title('Earth orbiting the sun')

    style = {
        "10": "orange",
        "199": "mediumspringgreen",
        "299": "gold",
        "399": "cornflowerblue",
        "499": "orangered",
        "599": "navajowhite",
        "699": "papayawhip",
        "799": "powderblue",
        "899": "midnightblue",
    }

    def animate(i):
        lines = []
        ax.clear()

        # log progress
        if i % 10 == 0:
            log_progress(i, frames, start)

        lim = 2e11
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
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

        # display date
        keys = data.times()
        date: float = float(list(keys)[i])
        date_time = datetime.fromtimestamp(date)
        date_str = date_time.strftime("%Y-%m")
        ax.text2D(0.05, 0.95, date_str, transform=ax.transAxes, color='black')

        # return lines as tuple
        return tuple(lines)

    anim = FuncAnimation(fig, animate, interval=1,
                         blit=True, frames=frames, repeat=True)
    print(f'Saving animation to plots/{filename}.gif...')
    anim.save(f'plots/{filename}.gif',
              writer=PillowWriter(fps=24), dpi=200)
    print(f'Animation saved to plots/{filename}.gif')

