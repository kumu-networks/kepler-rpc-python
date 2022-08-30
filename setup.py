from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='keplerrpc',
    version='0.1.0',
    author='',
    author_email='@kumunetworks.com',
    description='Python package Kepler RPC client.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['tests', 'examples']),
    install_requires=[
        'pyserial','msgpack','stm32loader','numpy'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3',
)
