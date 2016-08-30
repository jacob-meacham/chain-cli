"""CLI for chain.

This module is not intended to be used programmatically - if this is something you want, use chain.client instead.
"""

import click

from chain.chain import ChainClient, Frequency, NoChainExistsException, ChainExistsException

DEFAULT_DATA_PATH = '~/.chain/chains.json'

# This is idiomatic for click
# pylint: disable=C0103
pass_chain_context = click.make_pass_decorator(ChainClient)


# No docstrings for these, as they are not meant to be called.
# pylint: disable=missing-docstring

@click.group()
@click.option('--file', metavar='FILE', help='Data file path, default is ~/.chain/chains.json', type=click.Path(),
              default=DEFAULT_DATA_PATH)
@click.version_option('0.0.1')
@click.pass_context
def cli(ctx, file):
    ctx.obj = ChainClient(file)


@cli.command(name='new', help='add a new chain')
@click.argument('name')
@click.option('--title', '-t', help='Title of this chain. If not specified, the title will be the name')
@click.option('--daily', is_flag=True, help='Add daily links (Default)')
@click.option('--weekly', is_flag=True, help='Add weekly links')
@click.option('--monthly', is_flag=True, help='Add monthly links')
@click.option('--required', help='Number of links required for the chain to be considered unbroken', default=1)
@click.option('--description', '-d', help='Description of this chain', default='')
@pass_chain_context
def new_chain(client, name, title, daily, weekly, monthly, required, description):
    if [daily, weekly, monthly].count(True) > 1:
        raise click.BadArgumentUsage('One and only one of --daily, --weekly, --monthly must be set.')

    # Pylint has bugs with enums
    # pylint: disable=redefined-variable-type
    if weekly:
        frequency = Frequency.weekly
    elif monthly:
        frequency = Frequency.monthly
    else:
        frequency = Frequency.daily

    try:
        client.new_chain(name, title=title, frequency=frequency, description=description, num_required=required)
    except ChainExistsException as e:
        raise click.BadArgumentUsage(e.message)

    click.echo("New chain \"{}\" created. Don't break the chain!".format(name))


@cli.command(name='add', help='add a link to the chain')
@click.argument('name')
@click.option('--num', help='Number of links to add', default=1)
@click.option('--message', '-m', help='Message attached to the added link', default='')
@pass_chain_context
def add_link(client, name, num, message):
    try:
        client.add_link_to_chain(name, num, message=message)
    except NoChainExistsException as e:
        raise click.BadArgumentUsage(e.message)

    click.echo("Added {} links to chain \"{}\". Don't break the chain!".format(num, name))


@cli.command(name='ls', help='List chains')
@click.option('-q', help='List name only', is_flag=True)
@pass_chain_context
def list_chains(client, q):
    try:
        chains = client.list_chains()
        if q:
            for c in chains:
                click.echo(c['id'])
        else:
            for c in chains:
                # TODO: List them using termtable
                click.echo(c)
    except NoChainExistsException as e:
        raise click.BadArgumentUsage(e.message)


if __name__ == '__main__':
    # pylint: disable=E1120
    cli()
