from matplotlib import pyplot as plt
from utils.plots.prep_data import SimData
from utils.plots.style import Styles
from ing_theme_matplotlib import mpl_style
import numpy as np
import os


class CompareProjectiles:
    def __init__(self, data_1: SimData, data_2: SimData):
        self._data_1: SimData = data_1
        self._data_2: SimData = data_2

    def init_plot(self) -> None:
        """
        Initializes the plot.
        """
        mpl_style(dark=True)

    def save_plot(self, tag: str) -> None:
        """
        Saves the plot.
        """
        plt.legend()

        if not os.path.exists(f'plots/projectile/{self._data_1._filename}'):
            os.makedirs(f'plots/projectile/{self._data_1._filename}')
        plt.savefig(f'plots/projectile/{self._data_1._filename}/{tag}.png',
                    dpi=300, bbox_inches='tight')
        plt.clf()

    def plot_pos(self) -> None:
        """
        Plots the position of the object.
        """
        self.init_plot()
        x_1, y_1, _ = self._data_1.position("projectile")
        x_2, y_2, _ = self._data_2.position("projectile")

        plt.plot(x_1, y_1, label=self._data_1._filename, linewidth=0.5)
        plt.plot(x_2, y_2, label=self._data_2._filename, linewidth=0.5)

        # add labels
        plt.xlabel('x (m)')
        plt.ylabel('y (m)')

        # add title
        plt.title('Position of Projectile')

        self.save_plot('pos')

    def plot_vel(self) -> None:
        """
        Plots the y velocity of the object.
        """
        self.init_plot()
        t_1, _, vy_1, _ = self._data_1.velocity("projectile")
        t_2, _, vy_2, _ = self._data_2.velocity("projectile")

        plt.plot(t_1, vy_1, label=self._data_1._filename, linewidth=0.5)
        plt.plot(t_2, vy_2, label=self._data_2._filename, linewidth=0.5)

        # add labels
        plt.xlabel('t (s)')
        plt.ylabel('v (m/s)')

        # add title
        plt.title('Velocity of Projectile')

        self.save_plot('vel')

    def plot_momentum(self) -> None:
        """
        Plots the momentum of the object.
        """
        self.init_plot()
        t, p_1 = self._data_1.system_momentum()
        t, p_2 = self._data_2.system_momentum()

        plt.plot(t, p_1, label=self._data_1._filename, linewidth=0.5)
        plt.plot(t, p_2, label=self._data_2._filename, linewidth=0.5)

        # add labels
        plt.xlabel('t (s)')
        plt.ylabel('p (kg m/s)')

        # add title
        plt.title('Momentum of Projectile')

        self.save_plot('mom')


class CompareSol:
    def __init__(self, datas: list[SimData]):
        self._datas: list[SimData] = datas
        self._styles: Styles = Styles()

    def init_plot(self) -> None:
        """
        Initializes the plot.
        """
        mpl_style(dark=True)

    def save_plot(self, tag: str) -> None:
        """
        Saves the plot.
        """
        plt.legend()

        if not os.path.exists('plots/solarsystem/comparison'):
            os.makedirs('plots/solarsystem/comparison')
        plt.savefig(f'plots/solarsystem/comparison/{tag}.png',
                    dpi=300, bbox_inches='tight')
        plt.clf()

    def plot_momentum(self) -> None:
        """
        Plots the momentum of the object.
        """
        self.init_plot()
        for data in self._datas:
            style = self._styles.get_style(data._filename)
            t, p = data.system_momentum()
            plt.plot(t, p, label=style.name, color=style.color, linewidth=0.5)

        # add labels
        plt.xlabel('t (s)')
        plt.ylabel('p (kg m/s)')

        # add title
        plt.title('Momentum of Projectile')

        self.save_plot('mom')

    def plot_energy(self) -> None:
        self.init_plot()
        for data in self._datas:
            style = self._styles.get_style(data._filename)
            t, e = data.system_energy()
            plt.plot(t, e, label=style.name, color=style.color, linewidth=0.5)

        # add labels
        plt.xlabel('t (s)')
        plt.ylabel('E (J)')

        # add title
        plt.title('Energy of System')

        self.save_plot('energy')


class Plot2DProjectile:
    def __init__(self, data: SimData):
        self._data: SimData = data

    def init_plot(self, style: str = "dark_background") -> None:
        """
        Initializes the plot.
        """
        mpl_style(dark=True)

    def save_plot(self, tag: str) -> None:
        """
        Saves the plot.
        """

        plt.legend()

        if not os.path.exists(f'plots/projectile/{self._data._filename}'):
            os.makedirs(f'plots/projectile/{self._data._filename}')
        plt.savefig(f'plots/projectile/{self._data._filename}/{tag}.png',
                    dpi=300, bbox_inches='tight')
        plt.clf()

    def plot_pos(self) -> None:
        """
        Plots the position of the object.
        """
        self.init_plot()
        x, y, _ = self._data.position("projectile")

        plt.plot(x, y, linewidth=0.5)

        # add labels
        plt.xlabel('x (m)')
        plt.ylabel('y (m)')

        # add title
        plt.title('Position of Projectile')

        self.save_plot('pos')

    def plot_vel(self) -> None:
        """
        Plots the y velocity of the object.
        """
        self.init_plot()
        t, _, vy, _ = self._data.velocity("projectile")

        plt.plot(t, vy, label='vy', linewidth=0.5)

        # add labels
        plt.xlabel('t (s)')
        plt.ylabel('v (m/s)')

        # add title
        plt.title('Velocity of Projectile')

        self.save_plot('vel')


class Plot2DSol:
    def __init__(self, data: SimData):
        self._styles = Styles()
        self._data: SimData = data

    def init_plot(self) -> None:
        """
        Initializes the plot.
        """
        mpl_style(dark=True)

    def save_plot(self, tag: str) -> None:
        """
        Saves the plot.
        """
        if not os.path.exists(f'plots/solarsystem/{self._data._filename}'):
            os.makedirs(f'plots/solarsystem/{self._data._filename}')

        # add legend with font size 8
        plt.legend(fontsize=8)

        plt.xticks(fontsize=6)
        plt.yticks(fontsize=6)

        plt.savefig(f'plots/solarsystem/{self._data._filename}/{tag}.png',
                    dpi=300, bbox_inches='tight')
        plt.clf()

    def plot_pos(self, bodies: list[str], save: bool = True) -> None:
        """
        Plots the position of the object.
        """
        self.init_plot()
        for body in bodies:
            x, y, _ = self._data.position(body)

            style = self._styles.get_style(body)

            # plot line of trajectory
            plt.plot(x, y, label=style.name, color=style.color, linewidth=0.5)

            # plot start and end points
            plt.plot(x[0], y[0], 'x', color=style.color, markersize=3)
            plt.plot(x[-1], y[-1], 'o', color=style.color, markersize=3)

        # even axis
        plt.gca().set_aspect('equal', adjustable='box')

        # decrease grid tick font size
        plt.xticks(fontsize=6)
        plt.yticks(fontsize=6)

        # label axes with font size 8
        plt.xlabel('x (m)', fontsize=8)
        plt.ylabel('y (m)', fontsize=8)

        bodies_str = '_'.join(bodies)

        plt.title('Position of ' + bodies_str)

        if save:
            self.save_plot('pos_' + bodies_str)

    def plot_all_pos(self) -> None:
        """
        Plots the position of all objects.
        """
        self.init_plot()
        bodies = self._data.obj_list

        self.plot_pos(bodies, save=False)

        plt.title('Position of Planets')
        self.save_plot('pos_all')

    def plot_ke(self, bodies: list[str], save: bool = True) -> None:
        """
        Plots the kinetic energy of the object.
        """
        self.init_plot()

        body_names = []

        for body in bodies:
            t, ke = self._data.ke(body)

            style = self._styles.get_style(body)

            plt.plot(t, ke, label=style.name, linewidth=0.5, color=style.color)

            body_names.append(style.name)

        # label axes
        plt.xlabel('date', fontsize=8)
        plt.ylabel('KE (J)', fontsize=8)

        bodies_str = '_'.join(body_names)
        bodies_str_spaces = ' '.join(body_names)

        plt.title('Kinetic Energy of ' + bodies_str_spaces)
        if save:
            self.save_plot(f'{bodies_str}_ke')

    def plot_pe(self, bodies: list[str], save: bool = True) -> None:
        """
        Plots the potential energy of the object.
        """
        self.init_plot()

        body_names = []

        for body in bodies:
            style = self._styles.get_style(body)

            t, pe = self._data.pe(body)

            plt.plot(t, pe, label=style.name, linewidth=0.5, color=style.color)

            body_names.append(style.name)

        # label axes
        plt.xlabel('date', fontsize=8)
        plt.ylabel('PE (J)', fontsize=8)

        bodies_str = '_'.join(body_names)
        bodies_str_spaces = ' '.join(body_names)

        plt.title('Potential Energy of ' + bodies_str_spaces)
        if save:
            self.save_plot(f'{bodies_str}_pe')

    def plot_system_energy(self) -> None:
        """
        Plots the kinetic energy of the system.
        """
        self.init_plot()
        t, energy = self._data.system_energy()

        plt.plot(t, energy, label='Energy', linewidth=0.5)

        # label axes
        plt.xlabel('date', fontsize=8)
        plt.ylabel('Total Energy (J)', fontsize=8)

        # ylim at least 20% of max
        # plt.ylim(bottom=0, top=max(energy)*1.2)

        plt.title('Total Energy of System')

        self.save_plot('system_energy')

    def plot_energy(self, bodies: list[str], save: bool = True) -> None:
        """
        Plots the energy of the object.
        """
        self.init_plot()

        body_names = []

        for body in bodies:
            t, ke = np.array(self._data.ke(body))
            t, pe = self._data.pe(body)

            energy = list(ke + pe)

            style = self._styles.get_style(body)

            plt.plot(t, energy, label=style.name, color=style.color,
                     linewidth=0.5)

            body_names.append(style.name)

        bodies_str_spaces = ' '.join(body_names)
        bodies_str = '_'.join(body_names)

        # label axes
        plt.xlabel('date', fontsize=8)
        plt.ylabel('Energy (J)', fontsize=8)

        plt.title('Energy of ' + bodies_str_spaces)

        if save:
            self.save_plot(bodies_str + '_energy')

    def plot_system_momentum(self) -> None:
        """
        Plots the momentum of the system.
        """
        self.init_plot()
        t, p = self._data.system_momentum()

        plt.plot(t, p, label='Momentum', linewidth=0.5)

        # ylim at least 20% of max
        # plt.ylim(bottom=0, top=max(p)*1.2)

        # label axes
        plt.xlabel('date', fontsize=8)
        plt.ylabel('Total Momentum (kg m/s)', fontsize=8)

        plt.title('Total Momentum of System')

        self.save_plot('system_momentum')
