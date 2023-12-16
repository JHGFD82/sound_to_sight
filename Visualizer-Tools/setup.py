from setuptools import setup, find_packages

setup(
    name='Visualizer Tools',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'Visualizer-Tools = Visualizer-Tools.main:main',
        ],
    },
    # ... other setup parameters ...
)