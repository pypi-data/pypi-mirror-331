from setuptools import setup, find_packages

setup(
    name="emailynma",
    version="0.1.4",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.25.0",
    ],
)