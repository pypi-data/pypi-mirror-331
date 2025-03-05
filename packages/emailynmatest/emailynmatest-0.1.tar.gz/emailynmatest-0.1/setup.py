from setuptools import setup, find_packages

setup(
    name="emailynmatest",  # Package name
    version="0.1",
    packages=find_packages("emailynmatest"),  # Automatically find `emailynma` package
    install_requires=[
        "requests",  # Example dependency
    ],
)