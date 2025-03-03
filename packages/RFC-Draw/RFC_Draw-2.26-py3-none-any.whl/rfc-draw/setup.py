from setuptools import setup, find_packages

setup(
    name='RFC-Draw',
    version='2.26',
    author='Nevil Brownlee, Brian Carpenter',
    url='https://github.com/nevil-brownlee/rfc-draw',
    packages=find_packages(),
    description='Drawing program to create svg drawings for IETF RFCs',
    long_description=read('README.md'),
    classifiers=[
        'Development Status :: Mature, version 2.26',
        'Intended Audience :: IETF RFC authors',
        'Topic :: SVG diagrams for IETF RFCs',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.12',
        'Operating System :: Linux, Windows, MacOS',
    ] )
