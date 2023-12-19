from setuptools import setup, find_packages

setup(
    name='Visualizer Tools',
    version='0.1.0',
    author='Jeff Heller (JHGFD)',
    author_email='jeffheller@jhgfd.com',
    packages=find_packages(),
    install_requires=['pandas'],
    entry_points={
        'console_scripts': [
            'Visualizer-Tools = Visualizer-Tools.main:main',
        ],
    },
    url="https://github.com/JHGFD82/Visualizer-Tools",
    description="Tools to assist in the process of turning music data into video projects.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Artistic Software",
        "Topic :: Multimedia :: Sound/Audio :: MIDI",
        "Topic :: Multimedia :: Video"
    ],
    python_requires='>=3.6',
    include_package_data=True
)
