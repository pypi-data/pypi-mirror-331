# -*- coding: utf-8 -*-
#############################################
# File Name: setup.py
# Author: Basti.yourDeveloper
# Mail: basti.yourDeveloper@gmail.com
# Created Time:  2025-02-22
#############################################
from setuptools import setup, find_packages


setup(
    name="unionfind_link",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[],
    description="simple UnionFind model with test on element is inside. How to use, see jupyter book in https://github.com/BastiYourDeveloper/clustering-closest-pairs ",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Basti.YourDeveloper",
    author_email="basti.yourDeveloper@gmail.com",
    url="https://github.com/BastiYourDeveloper/unionfind-link.git",
    license="LGPL-3.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)

