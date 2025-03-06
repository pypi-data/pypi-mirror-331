#! /usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="canonicalwebteam.parser",
    version="1.0.0",
    author="Canonical webteam",
    author_email="webteam@canonical.com",
    url="https://github.com/canonical/canonicalwebteam.parser",
    description=(
        "Flask extension to parse websites and extract structured data"
    ),
    packages=find_packages(),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=[
        "Flask>=1.0.2",
        "beautifulsoup4",
        "humanize",
        "lxml",
        "requests",
        "python-dateutil",
        "validators",
        "python-slugify",
    ],
)
