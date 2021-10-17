#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="pilectric",
    version="0.1",
    description="Raspberry Pi Device Control",
    author="Owen Bulka",
    packages=find_packages(where="./src"),
    package_dir={"": "src"},
)
