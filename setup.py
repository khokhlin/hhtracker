import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hhtracker",
    version="0.0.1",
    author="Andrey Khokhlin",
    author_email="khokhlin@gmail.com",
    description="HHTracker",
    long_description=long_description,
    long_description_content_type="text/markdown",
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
          'console_scripts': [
              'hhtracker=hhtracker.hhtracker:main'
          ]
      }
)
