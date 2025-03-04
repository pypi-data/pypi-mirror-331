import inspect
import json
import os
import pathlib
import pickle
from typing import Any, Callable

import click

from bionemo.api import BionemoClient, RequestId, version

HOME = pathlib.Path(os.environ.get('HOME'))
CONFIG_DIR = HOME / ".config/bionemo/credentials"
CONFIG_FILE = CONFIG_DIR / "config.json"


@click.group()
@click.version_option(version=version.__version__, prog_name='bionemo')
@click.pass_context
def cli(ctx):
    pass


@cli.group()
def config():
    pass


@config.command(help="Use `bionemo config set` to enter your credentials and host address.")
def set():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

    host_address = click.prompt("Please enter the host address")
    api_key = click.prompt("Please enter your API key")

    with open(CONFIG_FILE, 'w') as f:
        json.dump({"api_key": api_key, "host_address": host_address}, f)

    click.echo("Configuration saved.")


@config.command()
def show():
    """Show the current configuration."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        click.echo(json.dumps(config, indent=4))
    except FileNotFoundError:
        click.echo("No configuration found.")


@config.command()
@click.argument("key")
def get(key):
    """Get a specific configuration value."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        click.echo(config.get(key))
    except FileNotFoundError:
        click.echo("No configuration found.")


def create_command(method: Callable):
    """Create a click command for a given method."""
    params = [
        click.Option([f'--{k}'], default=v.default)
        if v.default is not inspect.Parameter.empty
        else click.Argument([f'{k}'])
        for k, v in inspect.signature(method).parameters.items()
        if k != 'self'
    ]

    @cli.command(name=method.__name__, params=params, help=method.__doc__)
    @click.pass_context
    def new_command(ctx, *args, **kwargs):  # type: ignore
        # Instantiate a new client.
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            host = config.get("host_address")
            key = config.get("api_key")
        except FileNotFoundError:
            raise Exception(f"No configuration file found. Please run 'bionemo config set' to set up your API client.")

        ctx.obj = BionemoClient(api_key=key, api_host=host)

        # Call the method.
        if ctx.obj is not None:
            result = method(ctx.obj, *args, **kwargs)
            click.echo(result)
        else:
            click.echo('API not initialized. Please initialize the API first using the shell command: $bionemo login.')

    # Get parameters of the method (excluding 'self') and add them as arguments to the new command
    return new_command


# Get all marked functions from the client and create a corresponding CLI command for them.
decorated_member_functions = [
    getattr(BionemoClient, attr)
    for attr in dir(BionemoClient)
    if callable(getattr(BionemoClient, attr)) and getattr(getattr(BionemoClient, attr), 'is_decorated', False)
]


# Create a command for each method and add it to the cli group
for method in decorated_member_functions:
    create_command(method)


if __name__ == '__main__':
    cli()
