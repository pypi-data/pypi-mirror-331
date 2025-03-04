from setuptools import find_packages
from setuptools import setup

setup(
    name="z-rer",
    version="0.0.1",
    description="rer is a thin wrapper around pip that automatically handles requirements txt files.",
    url="https://github.com/mzguntalan/z-rer",
    author="Marko Zolo Gozano Untalan",
    author_email="mzguntalan@gmail.com",
    license="Apache-2.0",
    keywords=["package manager", "pip", "package", "resolver"],
    packages=find_packages(),
    requires=["pip"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
)
