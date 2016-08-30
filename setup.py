from setuptools import setup, find_packages

setup(
    name='chain',
    version='0.1.0',
    description='CLI and Python API for Chain',
    url='https://github.com/jacob-meacham/chain-cli',
    author='jemonjam',
    author_email='jacob.e.meacham@gmail.com',

    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click==6.6',
        'termcolor==1.1.0'
    ],

    entry_points='''
        [console_scripts]
        chain=chain.cli:cli
    ''',
)
