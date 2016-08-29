import click

from chain.chain import ChainClient

DEFAULT_DATA_PATH='~/.chain/chains.json'

# This is idiomatic for click
# pylint: disable=C0103
pass_chain_context = click.make_pass_decorator(ChainClient)

@click.group()
@click.option('--file', metavar='FILE', help='Data file, default is ~/.chain/chains.json', type=click.Path(), default=DEFAULT_DATA_PATH)
@click.version_option('0.0.1')
@click.pass_context
def cli(ctx, file):
    ctx.obj = ChainClient(file)

@cli.command(name='new', help='add a new chain')
@click.argument('name', help='name of the chain')
@click.option('--daily', is_flag=True, help='Add daily links', default=True)
@click.option('--weekly', is_flag=True, help='Add weekly links')
@click.option('--monthly', is_flag=True, help='Add monthly links')
@click.option('--required', help='Number of links required for the chain to be considered unbroken')
@click.option('--description', help='Description of this chain')
@pass_chain_context
def new_chain(client, name, daily, weekly, monthly, required, description):
    client.new_chain(name, frequency=0, description=description, num_required=required)
    click.echo("New chain {} created. Don't break the chain!".format(name))

@cli.command(name='add', help='add a link to the chain')
@click.argument('name', help='name of the chain')
@click.argument('name', help='name of the chain')
@click.option('--message', '-m', help='Number of links required for the chain to be considered unbroken')