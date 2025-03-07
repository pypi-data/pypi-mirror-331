# filepath: /home/astane/Desktop/GenericBike/genetic_bike_ictp_2024/setup.py
from setuptools import setup, find_packages

setup(
    name="genetic_bike_ictp_2024",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A bike simulation and optimization package for ICTP 2024",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy==2.1.3",
        "matplotlib==3.9.2",
        # add other dependencies here if needed
    ],
    entry_points={
        "console_scripts": [
            # If a command line entry point is needed, adjust accordingly.
            "genetic_bike=main:main",
        ]
    },
)
