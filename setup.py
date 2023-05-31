from pathlib import Path
from typing import Union

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


def read_requirements(path: Union[str, Path]):
    with open(path, "r") as file:
        return file.read().splitlines()


requirements = read_requirements("requirements.txt")
requirements_dev = read_requirements("requirements_dev.txt")

setuptools.setup(
    name="pyaipersonality",
    version="1.0.0",
    author="Saifeddine ALOUI",
    author_email="aloui.saifeddine@gmail.com",
    description="A python library for AI personality definition",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ParisNeo/PyAIPersonality",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    extras_require={"dev": requirements_dev},
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
