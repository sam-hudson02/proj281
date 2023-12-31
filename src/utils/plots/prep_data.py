import numpy as np
import json
from datetime import datetime


class SimData:
    def __init__(self, filename: str, raw_data: dict | None = None):
        self._filename = filename.split('/')[-1].split('.')[0]
        if raw_data is None:
            self._raw_data = self._load_data(filename)
        else:
            self._raw_data = raw_data

        self._obj_list = list(list(self._raw_data.values())[0].keys())

        if 'system_info' in self._obj_list:
            self._obj_list.remove('system_info')

    @property
    def obj_list(self) -> list[str]:
        """
        Returns:
            list[str]: The list of objects in the simulation.
        """
        return self._obj_list

    def times(self) -> list[float]:
        """
        Returns:
            list[float]: The list of times in the simulation.
        """
        return list(map(float, self._raw_data.keys()))

    def _load_data(self, filename: str) -> dict:
        with open(filename, 'r') as f:
            data = json.load(f)

        return data

    def position(self, obj: str = '399') -> tuple[
            list[float],
            list[float],
            list[float]]:
        """
        Args:
            obj (str): The object to plot.
        Returns:
            tuple[list[float], list[float], list[float]]: The x, y, and z

        Converts the simulation position data into a format that can be
        plotted.
        """
        obj_x = []
        obj_y = []
        obj_z = []

        for step in self._raw_data.values():
            obj_data = step[obj]

            obj_pos = np.array(obj_data['position'])

            obj_x.append(obj_pos[0])
            obj_y.append(obj_pos[1])
            obj_z.append(obj_pos[2])

        return obj_x, obj_y, obj_z

    def velocity(self, obj: str = '399') -> tuple[
            list[float],
            list[float],
            list[float],
            list[float]]:
        """
        Args:
            obj (str): The object to plot.
        Returns:
            tuple[list[datetime] list[float],
                  list[float], list[float]]:
                The datetime, x, y, and z

        Converts the simulation velocity data into a format that can be
        plotted.
        """
        t = []

        obj_vx = []
        obj_vy = []
        obj_vz = []

        for ts in self._raw_data.keys():
            step = self._raw_data[ts]

            obj_data = step[obj]

            obj_vel = np.array(obj_data['velocity'])

            obj_vx.append(obj_vel[0])
            obj_vy.append(obj_vel[1])
            obj_vz.append(obj_vel[2])

            t.append(datetime.fromtimestamp(float(ts)))

        return t, obj_vx, obj_vy, obj_vz

    def momentum(self, obj: str = '399') -> tuple[
            list[float],
            list[float],
            list[float]]:
        """
        Args:
            obj (str): The object to plot.
        Returns:
            tuple[list[float], list[float], list[float]]: The x, y, and z

        Converts the simulation momentum data into a format that can be
        plotted.
        """
        obj_px = []
        obj_py = []
        obj_pz = []

        for step in self._raw_data.values():
            obj_data = step[obj]

            obj_mom = np.array(obj_data['momentum'])

            obj_px.append(obj_mom[0])
            obj_py.append(obj_mom[1])
            obj_pz.append(obj_mom[2])

        return obj_px, obj_py, obj_pz

    def ke(self, obj: str = '399') -> tuple[list[datetime],
                                            list[float]]:
        """
        Args:
            obj (str): The object to plot.
        Returns:
            tuple[list[float], list[float]]: The x, y, and z

        Converts the simulation ke data into a format that can be plotted.
        """

        obj_ke = []
        times = []

        for ts, step in self._raw_data.items():
            obj_data = step[obj]
            time = datetime.fromtimestamp(float(ts))
            times.append(time)
            obj_ke.append(obj_data['ke'])

        return times, obj_ke

    def pe(self, obj: str = '399') -> tuple[list[datetime],
                                            list[float]]:
        """
        Args:
            obj (str): The object to plot.
        Returns:
            tuple[list[float], list[float]]: The x, y, and z

        Converts the simulation pe data into a format that can be plotted.
        """
        obj_pe = []
        times = []

        for ts, step in self._raw_data.items():
            time = datetime.fromtimestamp(float(ts))
            obj_data = step[obj]

            times.append(time)
            obj_pe.append(obj_data['pe'])

        return times, obj_pe

    def system_energy(self) -> tuple[list[datetime], list[float]]:
        """
        Returns:
            tuple[list[float], list[float]]: The x, y, and z

        Converts the simulation system ke data into a format that can be
        plotted.
        """
        ke = []
        times = []

        for ts, step in self._raw_data.items():
            time = datetime.fromtimestamp(float(ts))
            times.append(time)
            ke.append(step['system_info']['energy'])

        return times, ke

    def system_momentum(self) -> tuple[list[datetime],
                                       list[float]]:
        """
        Returns:
            tuple[list[float], list[float]]: The x, y, and z

        Converts the simulation system momentum data into a format that can be
        plotted.
        """
        p = []
        times = []

        for ts, step in self._raw_data.items():
            times.append(datetime.fromtimestamp(float(ts)))
            momentum_vec = np.array(step['system_info']['momentum'])
            momentum = np.linalg.norm(momentum_vec)
            p.append(momentum)

        return times, p
