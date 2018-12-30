"""HHTracker Setup"""
import setuptools


setuptools.setup(
    name="hhtracker",
    version="0.0.1",
    author="Andrey Khokhlin",
    author_email="khokhlin@gmail.com",
    description="HHTracker",
    url="https://github.com/khokhlin/hhtracker",
    packages=setuptools.find_packages(),
    install_requires=[
        "requests",
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
    entry_points={
        "console_scripts": [
            "hhtracker=hhtracker.hhtracker:main"
        ]
    }
)
