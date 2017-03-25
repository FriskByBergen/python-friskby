from setuptools import setup

_dependencies = ['requests', 'gitpython', 'pyserial', 'python-dateutil']

setup(
    name='friskby',
    version='0.61.1',
    description='The friskby module',
    url='http://github.com/FriskbyBergen/python-friskby',
    author='Friskby Bergen',
    author_email='pgdr@statoil.com',
    license='GNU General Public License, Version 3',
    packages=['friskby'],
    zip_safe=False,
    setup_requires=_dependencies,
    install_requires=_dependencies
)
