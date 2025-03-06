from setuptools import setup, find_packages

setup(
    name="karta_benchmarks",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    author="GetKart.ai",
    author_email="developers@getkart.ai",
    description="A collection of datasets, tools and tasks to evaluate AI agents for multiple domains",
    long_description=open("readme.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/getkarta/KartaBenchmarkCaseDetails",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)