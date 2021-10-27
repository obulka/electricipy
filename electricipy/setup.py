#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="electricipy",
    version="0.0.1",
    description="Electronic device control.",
    author="Owen Bulka",
    packages=find_packages(where="./src"),
    package_dir={"": "src"},
    scripts=["./src/timelapse"],
)
