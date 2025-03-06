from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_long_description():
    try:
        with open("README.md", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "A library for building and testing NLP models with PyTorch and Transformers."

setup(
    name="querysquirrel",  # Your package name
    version="0.1.12",  # Update version for each release
    author="Will Armstrong, Thomas Burns, Caroline Cordes, Sarah Lawlis",
    author_email="wma002@uark.edu",
    description="A library for building and testing NLP models with PyTorch and Transformers.",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/willarmstrong1/querysquirrel_library",  # Link to your GitHub repo
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "torch>=1.9.0",
        "transformers>=4.12.0",
        "sentence-transformers>=2.2.2",
        "scikit-learn>=0.24.0",
        "pandas>=1.3.0",
        "numpy>=1.19.0",
        "matplotlib>=3.4.3",
        "seaborn>=0.11.2",
        "dask[dataframe]>=2021.10.0",
        "pyarrow>=5.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

