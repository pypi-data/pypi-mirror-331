"""
this is the setup of this package.
"""

from setuptools import setup

#from .sphinxcontrib.d2lang import __version__

with open('sphinxcontrib/requirements.txt', 'r', encoding='utf8') as file:
    install_requires = list(map(lambda x: x.strip(), file.readlines()))

with open('README.md', 'r', encoding='utf8') as file:
    long_description = file.read()

setup(
    name='sphinxcontrib-d2lang',
    version='0.0.4',
    author='Milka64',
    author_email='michael.ricart@0w.tf',
    url='https://git.0w.tf/Milka64/sphinx-d2lang/',
    description='an extension for sphinx to render d2lang diagrams in sphinx documents',
    packages=['sphinxcontrib.d2lang'],
    install_requires=install_requires,
    long_description=long_description,
    long_description_content_type='text/markdown',
    include_package_data=True,
    namespace_packages=["sphinxcontrib"],
)

