from setuptools import setup
import sys
import platform

setup(
    name='ariana',
    version='0.2.2',
    description='Ariana CLI - A tool for code instrumentalization and execution with observability',
    packages=['ariana'],
    package_data={
        'ariana': ['bin/ariana-linux-x64', 'bin/ariana-macos-x64', 'bin/ariana-macos-arm64', 'bin/ariana-windows-x64.exe'],
    },
    entry_points={
        'console_scripts': [
            'ariana = ariana:main',
        ],
    },
    license='BSD-3-Clause',
    url='https://github.com/dedale-dev/ariana',
)
