from setuptools import setup, find_packages

setup(
    name="fireviz",
    version="0.1.0",
    author="Ann Naser Nabil",
    author_email="ann.n.nabil@gmail.com",
    description="A simple package for quick data visualization",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AnnNaserNabil/fireviz",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "matplotlib",
        "seaborn",
        "plotly",
        "networkx",
        "squarify",
        "numpy",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
