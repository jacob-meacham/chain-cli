"""Client for chain"""

import json
import time
from enum import Enum

import os


class Frequency(Enum):
    daily = 1
    weekly = 2
    monthly = 3


class ChainExistsException(Exception):
    def __init__(self, name):
        Exception.__init__(self)
        self.message = 'Chain {} already exists'.format(name)


class NoChainExistsException(Exception):
    def __init__(self, name):
        Exception.__init__(self)
        self.message = 'No Chain named {} exists'.format(name)


def _safe_makedirs(dir_name):
    """Make a directory if it doesn't already exist.

    Args:
        dir_name: The directory to make.

    """
    try:
        os.makedirs(dir_name)
    except OSError:
        if not os.path.isdir(dir_name):
            raise


def _ensure_chain_file(file_path):
    if not os.path.exists(file_path):
        _safe_makedirs(os.path.dirname(file_path))

        with open(file_path, 'x') as f:
            json.dump([], f)


class ChainClient(object):
    """Main client for chain

        :param chain_file_path: The path to the chain file to update
    """
    def __init__(self, chain_file_path):
        self._chain_file_path = os.path.expanduser(chain_file_path)

        _ensure_chain_file(self._chain_file_path)

    def _update_chains(self, chains):
        with open(self._chain_file_path, 'w') as f:
            json.dump(chains, f, indent=4, separators=[',', ': '])

    def new_chain(self, name, title=None, frequency=Frequency.daily, description='', num_required=1):
        """Create a new chain

        :param name: The name of the chain (case insensitive)
        :param frequency: The frequency of the chain, using the chain.Frequency enum
        :param description: The description of this chain
        :param num_required: The number of links required for the chain to be considered unbroken
        :return: The created chain
        """
        if title is None:
            title = name

        name = name.lower()

        with open(self._chain_file_path, 'r') as f:
            chains = json.load(f)

        if len([c for c in chains if c['id'] == name]) > 0:
            # Chain already exists
            raise ChainExistsException(name)

        chain = {
            "id": name,
            "title": title,
            "frequency": frequency.name,
            "description": description,
            "required": num_required,
            "links": []
        }

        chains.append(chain)

        self._update_chains(chains)
        return chain

    def list_chains(self):
        with open(self._chain_file_path, 'r') as f:
            chains = json.load(f)

        return chains

    def add_link_to_chain(self, name, number=1, message=''):
        """Adds a link to an existing chain

        :param name: The name of the chain (case insensitive)
        :param number: The number of links to add
        :param message: The message to attach to the link(s)
        :return: The updated chain
        """
        name = name.lower()

        with open(self._chain_file_path, 'r') as f:
            chains = json.load(f)

        # Find the correct chain
        chain_to_update = [(i, c) for i, c in enumerate(chains) if c['id'] == name]
        if len(chain_to_update) == 0:
            raise NoChainExistsException(name)

        # Just take the first chain, if there are multiple.
        index, updated_chain = chain_to_update[0]
        updated_chain['links'].append({
            # TODO: Fix this to make it timezone agnostic
            'timestamp': int(time.time()),
            'number': number,
            'message': message
        })

        chains[index] = updated_chain

        self._update_chains(chains)
        return updated_chain
