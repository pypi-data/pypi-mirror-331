from setuptools import setup, find_packages

setup(
    name="RFC-Draw",
    version="2.26",
    author="Nevil Brownlee, Brian Carpenter",
    author_email="nevil.brownlee@gmail.com",
    url="https://github.com/nevil-brownlee/rfc-draw",
    packages=find_packages(),
    description="Drawing program to create svg drawings for IETF RFCs",
    classifiers=[
        "Development Status :: Mature, version 2.26",
        "Intended Audience :: IETF RFC authors",
        "Topic :: SVG diagrams for IETF RFCs",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Linux, Windows, MacOS",
    ] )
