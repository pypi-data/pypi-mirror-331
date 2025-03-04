# setup.py
from setuptools import setup, find_packages

setup(
    name="langtools-cli",
    version="0.0.1",
    author="jiuhu",
    author_email="your.email@example.com",
    description="A Python package for language processing utilities",
    long_description="A Python package for language processing utilities",
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/langtools-cli",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
