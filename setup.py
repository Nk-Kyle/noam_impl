from setuptools import setup, find_packages
import os

curr_dir = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(curr_dir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="noam_impl",
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="1.0.0",
    description="Implementation of NOAM with application of Aggregation and Partitioning",
    author="Ng Kyle",
    author_email="kyle.treoxer@gmail.com",
    install_requires=[
        "pandas",
    ],
    python_requires=">=3.6",
)
