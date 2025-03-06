from setuptools import find_packages, setup

with open("readme.md", "r") as fh:
    long_description = fh.read()

setup(
    name="phisher",
    packages=find_packages(),
    version="0.1.0",
    description="Phish Classificator based on URL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="WUT",
    author_email="bartosz.kosinski.b@gmail.com",
    license="MIT",
    url="https://github.com/Bartolo72/phisher",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
