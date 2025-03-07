"""
This is the setup file for the json_logger_loki package.
It uses setuptools to manage the installation of the package and its dependencies.
"""
from setuptools import setup, find_packages

# Read the content of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="json_logger_loki",
    version="0.2.0",
    packages=find_packages(),
    install_requires=["requests", "opentelemetry-api"],
    author="Rafael Brandao Ferreira",
    description="A JSON logger with OpenTelemetry and Loki support",
    python_requires=">=3.7",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rafaelbrandaof/json_logger_loki",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
