#!/usr/bin/env python
import os
import subprocess
import sys

import click
import flake8.main
from coverage.cmdline import main as coverage_main
from termcolor import colored

here = os.path.abspath(os.path.dirname(__file__))
SOURCE_DIR = os.path.join(here, 'chain')
TEST_DIR = os.path.join(here, 'chain', 'test')
COVERAGE_TARGET_DIR = os.path.join(here, 'build', 'coverage')


@click.group()
def cli():
    pass


def run_step(step_name):
    def decorator(func):
        def func_wrapper(*args, **kwargs):
            click.echo(colored('Running {} step...'.format(step_name), 'blue'))
            ret = func(*args, **kwargs)
            if ret != 0:
                click.echo(colored('{} failed with code: {}!\n'.format(step_name, ret), 'red'))
            else:
                click.echo(colored('{} successful!\n'.format(step_name), 'green'))
            return ret

        return func_wrapper

    return decorator


@cli.command('lint', help='run lint on the project')
def lint():
    return _lint()


@run_step('lint')
def _lint():
    errno = 0
    errno |= _run_flake8()
    errno |= _run_pylint()

    return errno


def _run_flake8():
    # Flake8 doesn't expect to be called like this, so Hack up argv
    sys.argv = ['', SOURCE_DIR, '--verbose']
    try:
        flake8.main.main()
    except SystemExit:
        return 17

    return 0


def _run_pylint():
    message_template = '{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}'
    errno = 0

    # pylint on source
    errno |= subprocess.call(
        ['pylint', SOURCE_DIR, '--ignore', 'test', '-rn', '--msg-template',
         message_template])

    test_disabled_warnings = [
        'missing-docstring',  # No need for docstrings in tests
        'redefined-outer-name',  # pytest.fixture uses this
        'protected-access',  # Tests require protected access
        'unused-argument',  # Fixtures with side effects only require this
        'no-self-use',  # pytest classes often use this
        'attribute-defined-outside-init',  # pytest classes often use this
        'no-member',  # MagicMocks often have no member
        'super-init-not-called',  # Stubs often don't call super init
        'duplicate-code',  # Moderately acceptable in tests
    ]

    # pylint on test
    errno |= subprocess.call(
        ['pylint', TEST_DIR, '--disable={}'.format(','.join(test_disabled_warnings)), '-rn', '--msg-template',
         message_template])

    return errno


@run_step('test')
def _test():
    errno = coverage_main(['run', '--source', SOURCE_DIR, '-m', 'py.test', '-rw', TEST_DIR])
    errno |= coverage_main(['html', '-d', os.path.join(COVERAGE_TARGET_DIR, 'html')])
    errno |= coverage_main(['xml', '-o', os.path.join(COVERAGE_TARGET_DIR, 'coverage.xml')])
    errno |= coverage_main(['report'])
    return errno


@cli.command('test', help='run project tests and compute coverage')
def test():
    sys.exit(_test())


@run_step('build')
def _build():
    errno = 0
    errno |= _lint()
    errno |= _test()
    return errno


@cli.command('build', help='run full build')
def build():
    sys.exit(_build())


if __name__ == '__main__':
    cli()
