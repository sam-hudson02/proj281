from sims.solar_system import SolarSystemSim
from click import option
from utils.config import Config
import click


@click.group()
def cli():
    pass


@cli.command('sim')
@option('--sim', '-s', default='sol', help='Simulation to run.')
@option('--config_file', '-c', default='config.json', help='Configuration file.')
@option('--plot', '-p', is_flag=True, help='Plot the simulation.')
def sim(sim, config_file: str, plot: bool):
    """Run a simulation."""
    config = Config(config_file)
    match sim.lower():
        case 'sol':
            SolarSystemSim(config.solar_system).run()
    click.echo('Simulation complete.')


@cli.command('plot')
@option('--level', '-l', default='all', help='Plot level.')
@option('--data', '-d', default='data', help='Data directory.')
def plot(level: str, data: str):
    """Plot a simulation."""
    pass


# run click parser
if __name__ == '__main__':
    cli()
