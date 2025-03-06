from setuptools import setup, find_packages

setup(
    name="emailynma_1",  # Package name
    version="0.1.2",
    packages=find_packages("emailynma_1"),  # Automatically find `emailynma` package
    install_requires=[
        "requests",  # Example dependency
    ],
)