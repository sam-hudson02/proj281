import numpy as np


def make_3d_data(data: dict,
                 obj: str = 'earth'
                 ) -> tuple[list[float], list[float], list[float]]:
    """
    Args:
        data (dict): The simulation data.
        obj (str): The object to plot.
    Returns:
        tuple[list[float], list[float], list[float]]: The x, y, and z

    Converts the simulation data into a format that can be plotted in 3D.
    """
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
