from setuptools import setup, find_packages # type: ignore

setup(
    name="tutorial_factorial",
    version="0.1",
    packages=find_packages(),
    install_requires=[],  # Add dependencies if any
    entry_points={
        'console_scripts': [
            'tutorial_factorial=tutorial_factorial:main',  # If you want this to be a command-line tool
        ],
    },
)
