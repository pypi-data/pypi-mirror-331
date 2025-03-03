from setuptools import setup, find_packages

setup(
    name="uniseq",  
    version="0.0.1",
    license="MIT",
    description="A Python package to fetch protein sequences from UniProtKB using its REST API.",
    author="Sumon Basak",
    author_email="b.sumon@outlook.com",
    packages=find_packages(),
    install_requires=[
        "requests",
        "biopython"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
