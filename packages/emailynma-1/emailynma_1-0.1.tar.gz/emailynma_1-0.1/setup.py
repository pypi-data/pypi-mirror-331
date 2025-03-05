from setuptools import setup, find_packages

setup(
    name="emailynma_1",  # Package name
    version="0.1",
    packages=find_packages(),  # Automatically find `emailynma` package
    install_requires=[
        "requests",  # Example dependency
    ],
)