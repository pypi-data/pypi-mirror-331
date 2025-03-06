from setuptools import setup, find_packages

setup(
    name='svg_sampler',
    version='0.1.1',
    description='A package for sampling points from SVG files with overlap resolution and normalization options.',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/LuggiStruggi/SVGSampler',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy",
        "shapely",
        "svgpathtools",
        "matplotlib",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
