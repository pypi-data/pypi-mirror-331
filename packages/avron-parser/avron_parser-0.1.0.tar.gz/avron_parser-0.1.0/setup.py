from setuptools import setup, find_packages

setup(
    name="avron-parser",
    version="0.1.0",
    description="A parser for AVRON (A Very Readable Object Notation)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Kohan Mathers",
    author_email="mathers.kohan@gmail.com",
    url="https://github.com/kohanmathers/avron-parser",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
