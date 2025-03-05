from setuptools import setup, find_packages

setup(
    name="galagain",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "galagain=galagain.cli:main",
        ],
    },
)
