"""CLI for chain.

This module is not intended to be used programmatically - if this is something you want, use chain.client instead.
"""
import click

from chain.chain import ChainClient, Frequency, NoChainExistsException, ChainExistsException
from termcolor import colored

# No docstrings for this file, as the functions are not meant to be called directly.
# pylint: disable=missing-docstring

DEFAULT_DATA_PATH = '~/.chain/chains.json'
DONT_BREAK_TEXT = colored("Don't break the chain!", 'red', attrs=['underline'])

# This is idiomatic for click
# pylint: disable=C0103
pass_chain_context = click.make_pass_decorator(ChainClient)


def _format_chain_name(name):
    return colored('"{}"'.format(name), 'green', attrs=['bold'])


@click.group()
@click.option('--file', metavar='FILE', help='Data file path, default is ~/.chain/chains.json', type=click.Path(),
              default=DEFAULT_DATA_PATH)
@click.version_option('0.1.0')
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

    click.echo("New chain {} created. {}".format(_format_chain_name(name), DONT_BREAK_TEXT))


@cli.command(name='add', help='add a link to the chain')
@click.argument('name')
@click.option('--num', '-n', help='Number of links to add', default=1)
@click.option('--message', '-m', help='Message attached to the added link', default='')
@pass_chain_context
def add_link(client, name, num, message):
    try:
        client.add_link_to_chain(name, num, message=message)
    except NoChainExistsException as e:
        raise click.BadArgumentUsage(e.message)

    num_links_text = colored('{}'.format(num), "blue", attrs=['bold'])
    link_pluralization = 'link' if num == 1 else 'links'
    click.echo('Added {} {} to chain {}. {}'.format(num_links_text, link_pluralization,
                                                    _format_chain_name(name), DONT_BREAK_TEXT))


@cli.command(name='ls', help='List chains')
@click.option('-q', help='List name only', is_flag=True)
@click.option('--prefix', help='List only those chains whose name matches this prefix')
@pass_chain_context
def list_chains(client, q, prefix):
    try:
        chains = [c for c in client.list_chains() if prefix is None or c['id'].startswith(prefix)]
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
