from sims.solar_system import SolarSystemSim
from click import option
from utils.config import Config
from utils.plots.prep_data import SimData
from utils.plots.plot2d import Plot2D
from utils.plots.animation3d import animation_3d
import click


@click.group()
def cli():
    pass


@cli.command('sim')
@option('--sim', '-s', default='sol', help='Simulation to run.')
@option('--config_file', '-c', default='config.json', help='Configuration file.')
@option('--plot', '-p', is_flag=True, help='Plot the simulation.')
@option('--output', '-o', help='Output file.')
def sim(sim, config_file: str, plot: bool, output: str | None):
    """Run a simulation."""
    config = Config(config_file)
    match sim.lower():
        case 'sol':
            SolarSystemSim(config.solar_system, output).run()
    click.echo('Simulation complete.')


@cli.command('plot')
@option('--data', '-d', help='Data directory.')
@option('--animation', '-a', is_flag=True, help='Animate the simulation.')
def plot(data: str, animation: bool):
    """Plot a simulation."""
    file_name = data.split('/')[-1].split('.json')[0]
    sim_data = SimData(data)
    plot2d = Plot2D(sim_data)
    plot2d.plot_all_pos()
    plot2d.plot_system_energy()
    plot2d.plot_system_momentum()
    plot2d.plot_ke(['399'])
    plot2d.plot_pe(['399'])
    plot2d.plot_energy(['399'])
    if animation:
        output_file = f'{file_name}_animation_3d'
        animation_3d(sim_data, filename=output_file)


# run click parser
if __name__ == '__main__':
    cli()
