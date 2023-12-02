from matplotlib import pyplot as plt
import json
import numpy as np


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


if __name__ == '__main__':
    data = load_data()
    plot_2d_data(data)
    plot_2d_data_rel(data)
