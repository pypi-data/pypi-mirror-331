from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tracecolor",
    version="0.1.0",
    author="Marco Del Pin",
    author_email="marco.delpin@gmail.com",
    description="A lightweight colorized logger with TRACE level support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/marcodelpin/mlog",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "colorlog>=6.0.0",
    ],
)