"""
Setup script for l2data_reader.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="l2data_reader",
    version="0.1.0",
    author="Jason Jiang",
    author_email="chinese88+3@2925.com",
    description="A package for reading level 2 market data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/l2data-reader",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "protobuf>=3.12.0",
    ],
)