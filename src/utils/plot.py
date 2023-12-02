from matplotlib import pyplot as plt
import json
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from datetime import datetime
import time


def load_data(filename: str = 'data/log.json'):
    with open(filename) as f:
        data = json.load(f)
    return data


planets = ['mercury', 'venus', 'earth', 'mars',
           'jupiter', 'saturn', 'uranus', 'neptune']


def make_2d_data_rel(data: dict, planet: str = 'earth'):
    earth_x = []
    earth_y = []
    for step in data.values():
        sun_data = step['sun']
        planet_data = step[planet]

        earth_pos = np.array(planet_data['position'])
        sun_pos = np.array(sun_data['position'])

        earth_vector = earth_pos - sun_pos

        earth_x.append(earth_vector[0])
        earth_y.append(earth_vector[1])

    return earth_x, earth_y


def make_2d_data(data: dict, obj: str = 'earth'):
    obj_x = []
    obj_y = []
    for step in data.values():
        obj_data = step[obj]

        obj_pos = np.array(obj_data['position'])

        obj_x.append(obj_pos[0])
        obj_y.append(obj_pos[1])

    return obj_x, obj_y


def make_3d_data(data: dict, obj: str = 'earth'):
    obj_x = []
    obj_y = []
    obj_z = []
    for step in data.values():
        obj_data = step[obj]

        obj_pos = np.array(obj_data['position'])

        obj_x.append(obj_pos[0])
        obj_y.append(obj_pos[1])
        obj_z.append(obj_pos[2])

    return obj_x, obj_y, obj_z


def plot_2d_data_rel(data: dict):

    plt.figure(figsize=(8, 8))
    plt.style.use('ggplot')

    plt.plot(0, 0, 'yo', markersize=10)
    for planet in planets:
        planet_x, planet_y = make_2d_data(data, planet)
        plt.plot(planet_x, planet_y, label=planet, linewidth=0.5)
    plt.axis('equal')
    plt.xlabel('x')
    plt.ylabel('y')

    plt.title('Earth orbiting the sun')

    plt.savefig('data/plot.png', dpi=300, bbox_inches='tight')
    # clear figure
    plt.clf()


def plot_2d_data(data: dict):
    objs = ['sun', 'earth']

    plt.figure(figsize=(8, 8))
    plt.style.use('ggplot')

    for obj in objs:
        obj_x, obj_y = make_2d_data(data, obj)
        plt.plot(obj_x, obj_y, label=obj, linewidth=0.5)

    plt.axis('equal')
    plt.xlabel('x')
    plt.ylabel('y')

    plt.title('Solar system')

    plt.savefig('data/plot_2d.png', dpi=300, bbox_inches='tight')
    # clear figure
    plt.clf()


def plot_3d_data_rel(data: dict):

    plt.figure(figsize=(8, 8)).add_subplot(projection='3d')
    plt.style.use('ggplot')

    plt.plot(0, 0, 0, 'yo', markersize=10)
    for planet in planets:
        planet_x, planet_y, planet_z = make_3d_data(data, planet)
        plt.plot(planet_x, planet_y, planet_z, label=planet, linewidth=2)
    plt.axis('equal')
    plt.xlabel('x')
    plt.ylabel('y')

    plt.title('Earth orbiting the sun')

    plt.savefig('data/plot_3d.png', dpi=300, bbox_inches='tight')
    # clear figure
    plt.clf()


def animation_2d(data: dict):

    plt.figure(figsize=(8, 8)).add_subplot(projection='3d')

    # use dark style
    plt.style.use('dark_background')

    fig, ax = plt.subplots()

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
        ax.set_xlim(-5e11, 5e11)
        ax.set_ylim(-5e11, 5e11)
        for planet, data in planets_data.items():
            planet_x, planet_y, _ = data
            planet_x = planet_x[:i+1]
            planet_y = planet_y[:i+1]
            planet_point_x = planet_x[-1]
            planet_point_y = planet_y[-1]
            line1 = ax.plot(planet_x, planet_y,
                            label=planet, linewidth=0.5,
                            color=style[planet])
            line2 = ax.plot(planet_point_x, planet_point_y,
                            marker='o', markersize=5,
                            color=style[planet])
            lines.append(line1[0])
            lines.append(line2[0])

        # return lines as tuple
        return tuple(lines)

    anim = FuncAnimation(fig, animate, interval=1,
                         blit=True, frames=1000, repeat=True)
    anim.save('data/animation.gif', writer=PillowWriter(fps=24), dpi=300)


def animation_3d(data: dict):

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')

    # use dark style
    plt.style.use('dark_background')

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

    frames = 24 * 60

    def animate(i):
        lines = []
        print(i)
        ax.clear()

        lim = 2e11
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        for planet, planet_data in planets_data.items():
            planet_x, planet_y, planet_z = planet_data
            planet_x = planet_x[:i+1]
            planet_y = planet_y[:i+1]
            planet_z = planet_z[:i+1]
            planet_point_x = planet_x[-1]
            planet_point_y = planet_y[-1]
            planet_point_z = planet_z[-1]
            line1 = ax.plot(planet_x, planet_y, planet_z,
                            label=planet, linewidth=0.5,
                            color=style[planet])
            line2 = ax.plot(planet_point_x, planet_point_y, planet_point_z,
                            marker='o', markersize=5,
                            color=style[planet])
            lines.append(line1[0])
            lines.append(line2[0])

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
    anim.save('data/animation_3d_test.gif',
              writer=PillowWriter(fps=24), dpi=200)


if __name__ == '__main__':
    data = load_data()
    plot_2d_data(data)
    plot_2d_data_rel(data)
    plot_3d_data_rel(data)
    animation_3d(data)
