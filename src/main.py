from sims.solar_system import SolarSystemSim
from click import option
from utils.config import Config
from utils.plots.prep_data import SimData
from utils.plots.plot2d import Plot2D
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
    sim_data = SimData(data)
    plot = Plot2D(sim_data)
    plot.plot_all_pos()
    plot.plot_system_energy()
    plot.plot_system_momentum()
    plot.plot_ke(['399'])
    plot.plot_pe(['399'])
    plot.plot_energy(['399'])


# run click parser
if __name__ == '__main__':
    cli()
