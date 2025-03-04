cat kwwutils.egg-info/PKG-INFO

from setuptools import setup, find_packages

setup(
    name='kwwutils',
    version='0.1.14',
    packages=find_packages(include=['kwwutils', 'tests']),
    # other options like install_requires, author, etc.
)


mv setup.cfg setup_old.cfg  # Move any existing setup.cfg file
nano setup.cfg


[metadata]
name = kwwutils
version = 0.1.14


rm -rf build dist kwwutils.egg-info
python setup.py sdist bdist_wheel
uv pip install --force-reinstall --no-cache-dir -e .


- debugging
from setuptools import setup, find_packages

version = '0.1.14'
print(f"Building version {version}")

setup(
    name='kwwutils',
    version=version,
    packages=find_packages(include=['kwwutils', 'tests']),
    # other options like install_requires, author, etc.
)

