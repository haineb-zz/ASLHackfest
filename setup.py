#!/usr/bin/env python3

from setuptools import setup, find_packages


setup(
    name = "asl_sdr_hackfest",
    version = "0.0.1",
    author = "Brandon Haines",
    author_email = "haineb@gmail.com",
    description = ("Adversarial Science Lab's code for DARPA's SDR Hackfest."),
    license = "LGPL v2.1",
    url = "https://github.com/haineb/ASLHackfest",
    packages = find_packages(),
    install_requires=[
        'bitstring',
        'zmq',
        'numpy',
    ],
)
