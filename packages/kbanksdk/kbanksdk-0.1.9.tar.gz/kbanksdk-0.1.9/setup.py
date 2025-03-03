from setuptools import setup, find_packages
from src.kbanksdk.version import get_version

setup(
    name="kbanksdk",
    version=get_version(),
    author="nic wanavit",
    author_email="nwanavit@hatari.cc",
    description="KBank Payment Gateway SDK for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/villa-market/kbanksdk",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "requests>=2.25.1",
        "pydantic>=2.6.1",
        "dataclasses-json>=0.5.7",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
