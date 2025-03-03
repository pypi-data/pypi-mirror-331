from setuptools import setup, find_packages

setup(
    name="fireviz",
    version="0.1.3",
    author="Ann Naser Nabil",
    author_email="ann.naser@gmail.com",
    description="A quick and elegant visualization package for data analysis.",
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
    python_requires='>=3.6',
)
