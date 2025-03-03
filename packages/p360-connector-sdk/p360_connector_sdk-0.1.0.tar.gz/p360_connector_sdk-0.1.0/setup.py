from setuptools import setup, find_packages

setup(
    name="p360_connector_sdk",
    version="0.1.0",
    author="P360",
    author_email="mail@p360.com",
    description="An SDK for developing integration connectors",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/username/connector-sdk",  # TODO
    packages=find_packages(include=["p360_connector_sdk", "p360_connector_sdk.*"]),
    install_requires=[
        "pydantic>=2.0.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
