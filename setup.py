# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE.txt') as f:
    license = f.read()

setup(
    name='Python ArcGIS Convertor',
    version='0.1.0',
    description='A package to convert data between python and ArcGIS',
    long_description=readme,
    author='Saeid Adli',
    author_email='saeid.adli@gmail.com',
    url='spatialanalyst.ir',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

