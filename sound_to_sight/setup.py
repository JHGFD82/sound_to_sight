from setuptools import setup, find_packages

setup(
    name='Sound to Sight',
    version='0.1.0',
    author='Jeff Heller (JHGFD)',
    author_email='jeffheller@jhgfd.com',
    packages=find_packages(),
    install_requires=['pandas', 'BPMtoFPS'],
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
        "Operating System :: OS Independent",
        "Topic :: Artistic Software",
        "Topic :: Multimedia :: Sound/Audio :: MIDI",
        "Topic :: Multimedia :: Video"
    ],
    python_requires='>=3.6',
    include_package_data=True
)
