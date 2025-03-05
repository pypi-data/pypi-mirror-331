from setuptools import setup, find_packages


long_description = "A project for image processing from hot stage microscope using python."

setup(
    name="HSMTools",
    version="0.1.3",
    author="Manuel Leuchtenmüller",
    author_email="leichti@gmail.com",
    description="A project for image processing from hot stage microscope using python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leichti/hsmtools",
    packages=find_packages(),  
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.21.0",
        "opencv-python>=4.5.0",
        "polars>=0.18.0",
        "matplotlib>=3.1.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "hsmprocessor=HSMTools.data_preparation.cli:easycli",
        ],
    },
)