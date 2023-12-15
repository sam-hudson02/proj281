from sims.solar_system import SolarSystemSim
from sims.projectile import ProjectileSim
from sims.earth_orbit import EarthOrbit
from click import option
from utils.config import Config
from utils.plots.prep_data import SimData
from utils.plots.plot2d import CompareSol, Plot2DSol, Plot2DProjectile, CompareProjectiles
from utils.plots.animation3d import animation_3d
from utils.utils import setup_folders
import click


@click.group()
def cli():
    setup_folders()


@cli.command('sim')
@option('--sim', '-s', default='sol', help='Simulation to run.')
@option('--config_file', '-c', default='config.json', help='Configuration file.')
@option('--plot', '-p', is_flag=True, help='Plot the simulation.')
@option('--animate', '-a', is_flag=True, help='Animate the simulation.')
@option('--output', '-o', help='Output file.')
def sim(sim, config_file: str, plot: bool, animate: bool, output: str | None):
    """Run a simulation."""
    config = Config(config_file)

    match sim.lower():
        case 'sol':
            title, data = SolarSystemSim(config.solar_system, output).run()
            if plot:
                plot_sol(title, animation=animate, data=data)
        case 'proj':
            title, data = ProjectileSim(config.projectile, output).run()
            if plot:
                plot_projectile(title, animation=animate, data=data)
        case 'orbit':
            title, data = EarthOrbit(config.earth_orbit, output).run()
            if plot:
                plot_sol(title, animation=animate, data=data)
        case _:
            raise ValueError(f'Invalid simulation: {sim}')

    click.echo('Simulation complete.')


@cli.command('plot')
@option('--data', '-d', help='Filename of the data file.')
@option('--animation', '-a', is_flag=True, help='Animate the simulation.')
@option('--sim', '-s', default='sol', help='Simulation type.')
def plot(data: str, animation: bool, sim: str):
    """Plot a simulation."""
    match sim.lower():
        case 'sol':
            plot_sol(data, animation)
        case 'proj':
            plot_projectile(data, animation)


@cli.command('compare')
@option('--files', '-f', default='euler euler_cromer verlet',
        help='list of files to compare.')
@option('--sim', '-s', default='sol', help='Simulation type.')
def compare(files: str, sim: str):
    """Compare two simulations."""
    file_list = files.split(' ')
    match sim.lower():
        case 'sol':
            compare_sol(file_list)
        case 'proj':
            compare_projectile(file_list)
        case 'orbit':
            compare_orbit(file_list)


def compare_orbit(files: list[str]) -> None:
    datas = []
    for file in files:
        file_name = file.split('/')[-1].split('.json')[0]
        file_dir = f"data/sims/earth_orbit/{file_name}.json"
        sim_data = SimData(file_dir)
        datas.append(sim_data)

    compare = CompareSol(datas)
    compare.plot_momentum()
    compare.plot_energy()
    compare.plot_pos()

    print('Plotting 2d plots...')


def compare_projectile(files: list[str]) -> None:
    datas = []
    for file in files:
        file_name = file.split('/')[-1].split('.json')[0]
        file_dir = f"data/sims/projectile/{file_name}.json"
        sim_data = SimData(file_dir)
        datas.append(sim_data)

    compare = CompareProjectiles(datas)

    compare.plot_pos()
    compare.plot_vel()
    compare.plot_momentum()

    print('Plotting 2d plots...')


def compare_sol(files: list[str]) -> None:
    datas = []
    for file in files:
        file_name = file.split('/')[-1].split('.json')[0]
        file_dir = f"data/sims/solarsystem/{file_name}.json"
        sim_data = SimData(file_dir)
        datas.append(sim_data)

    compare = CompareSol(datas)
    compare.plot_momentum()
    compare.plot_energy()

    print('Plotting 2d plots...')


def plot_sol(filename: str, animation: bool, data: dict | None = None):
    file_name = filename.split('/')[-1].split('.json')[0]
    file_dir = f"data/sims/solarsystem/{file_name}.json"
    sim_data = SimData(file_dir, data)
    plot2d = Plot2DSol(sim_data)

    print('Plotting 2d plots...')
    plot2d.plot_all_pos()
    plot2d.plot_system_energy()
    plot2d.plot_system_momentum()
    plot2d.plot_ke(['399'])
    plot2d.plot_pe(['399'])
    plot2d.plot_energy(['399'])
    print('Finished plotting 2d plots.')

    if animation:
        output_file = f'{file_name}_animation_3d'
        animation_3d(sim_data, filename=output_file)


def plot_projectile(filename: str, animation: bool, data: dict | None = None):
    file_name = filename.split('/')[-1].split('.json')[0]
    file_dir = f"data/sims/projectile/{file_name}.json"
    sim_data = SimData(file_dir, data)
    plot2d = Plot2DProjectile(sim_data)

    print('Plotting 2d plots...')
    plot2d.plot_pos()
    plot2d.plot_vel()
    print('Finished plotting 2d plots.')


def plot_orbit(filename: str, animation: bool, data: dict | None = None):
    file_name = filename.split('/')[-1].split('.json')[0]
    file_dir = f"data/sims/solarsystem/{file_name}.json"
    sim_data = SimData(file_dir, data)
    plot2d = Plot2DSol(sim_data)

    print('Plotting 2d plots...')
    plot2d.plot_all_pos()
    plot2d.plot_system_energy()
    plot2d.plot_system_momentum()
    plot2d.plot_ke(['sattelite'])
    plot2d.plot_pe(['sattelite'])
    plot2d.plot_energy(['sattelite'])
    print('Finished plotting 2d plots.')

    if animation:
        output_file = f'{file_name}_animation_3d'
        animation_3d(sim_data, filename=output_file)


# run click parser
if __name__ == '__main__':
    cli()
