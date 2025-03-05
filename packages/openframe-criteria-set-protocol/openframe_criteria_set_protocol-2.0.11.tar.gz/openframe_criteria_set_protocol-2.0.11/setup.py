from setuptools import setup, find_packages

setup(
    name='openframe_criteria_set_protocol',
    packages=find_packages(),
    version="2.0.11",
    description='A protocol and tools for defining and working with criteria sets',
    author='Andrés Angulo <aa@openframe.org>',
    setup_requires=['pytest-runner']
)
