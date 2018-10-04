from setuptools import setup


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

packages = ['artnet']

setup(
    name='python-artnet',
    version='0.1.0',
    description='ArtNet lib, proto_lab',
    long_description=readme,
    author='proto_lab',
    author_email=' kontakt@proto-lab.de',
    url='http://protolab-rosenheim.de/',
    license=license,
    packages=packages,
    package_dir={'artnet': 'artnet'},
)
