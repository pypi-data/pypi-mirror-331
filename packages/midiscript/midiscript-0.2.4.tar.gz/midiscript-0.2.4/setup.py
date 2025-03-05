from setuptools import setup, find_packages

setup(
    name="midiscript",
    version="0.2.4",
    author="arsnovo",
    description="A programming language for musicians",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "midiutil>=1.2.1",
    ],
    entry_points={
        "console_scripts": [
            "midiscript=midiscript.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: MIDI",
        "Topic :: Software Development :: Compilers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)