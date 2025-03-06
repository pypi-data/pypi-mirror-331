from setuptools import setup, find_packages

setup(
    name="chessminal",
    version="1.6",
    packages=find_packages(include=["chessminal", "chessminal.*"]),
    package_data={'chessminal': ['assets/*.json']},
    include_package_data=True,
    install_requires=[
        "chess",
        "python-chess",
        "stockfish",
        "requests",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "chessminal=chessminal.main:main",
        ],
    },
)
