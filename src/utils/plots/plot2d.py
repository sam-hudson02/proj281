from matplotlib import pyplot as plt
from utils.plots.prep_data import SimData
import numpy as np


class Plot2D:
    def __init__(self, data: SimData):
        self._data: SimData = data

    def init_plot(self, style: str = "ggplot") -> None:
        """
        Initializes the plot.
        """
        plt.style.use(style)

    def save_plot(self, tag: str) -> None:
        """
        Saves the plot.
        """
        plt.savefig(f'plots/{self._data._filename}_{tag}_2dplot.png',
                    dpi=300, bbox_inches='tight')
        plt.clf()

    def plot_pos(self, bodies: list[str], save: bool = True) -> None:
        """
        Plots the position of the object.
        """
        self.init_plot()
        for body in bodies:
            x, y, _ = self._data.position(body)

            plt.plot(x, y, label=body)

        # even axis
        plt.gca().set_aspect('equal', adjustable='box')

        plt.legend()
        bodies_str = '_'.join(bodies)
        if save:
            self.save_plot('pos_' + bodies_str)

    def plot_all_pos(self) -> None:
        """
        Plots the position of all objects.
        """
        self.init_plot()
        bodies = self._data.obj_list

        self.plot_pos(bodies, save=False)
        self.save_plot('pos_all')

    def plot_ke(self, bodies: list[str], save: bool = True) -> None:
        """
        Plots the kinetic energy of the object.
        """
        self.init_plot()
        for body in bodies:
            t, ke = self._data.ke(body)

            plt.plot(t, ke, label=body)

        plt.legend()
        bodies_str = '_'.join(bodies)
        if save:
            self.save_plot('ke_' + bodies_str)

    def plot_pe(self, bodies: list[str], save: bool = True) -> None:
        """
        Plots the potential energy of the object.
        """
        self.init_plot()
        for body in bodies:
            t, pe = self._data.pe(body)

            plt.plot(t, pe, label=body)

        plt.legend()
        bodies_str = '_'.join(bodies)
        if save:
            self.save_plot('pe_' + bodies_str)

    def plot_system_energy(self) -> None:
        """
        Plots the kinetic energy of the system.
        """
        self.init_plot()
        t, ke = self._data.system_energy()

        plt.plot(t, ke)

        # ylim at least 20% of max
        plt.ylim(bottom=0, top=max(ke)*1.2)

        self.save_plot('system_energy')

    def plot_energy(self, bodies: list[str], save: bool = True) -> None:
        """
        Plots the energy of the object.
        """
        self.init_plot()
        for body in bodies:
            t, ke = np.array(self._data.ke(body))
            t, pe = self._data.pe(body)

            energy = list(ke + pe)

            plt.plot(t, energy, label=body)

        plt.legend()
        bodies_str = '_'.join(bodies)
        if save:
            self.save_plot('e_' + bodies_str)

    def plot_system_momentum(self) -> None:
        """
        Plots the momentum of the system.
        """
        self.init_plot()
        t, p = self._data.system_momentum()

        plt.plot(t, p)

        # ylim at least 20% of max
        plt.ylim(bottom=0, top=max(p)*1.2)

        self.save_plot('momentum_system')
