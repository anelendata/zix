#!/usr/bin/env python
from setuptools import setup

VERSION = "0.1.3"

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="zixweb",
    version=VERSION,
    description="zix - Create your SaaS app quickly by adding plugins!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Daigo Tanaka, Anelen Co., LLC",
    url="https://github.com/anelendata/zix",

    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: Apache Software License",

        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",

        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    install_requires=[
        "Authlib==0.15.3",
        "fastapi==0.95.1",
        "httpx==0.27.2",
        "itsdangerous==2.1.2",
        "python-jose==3.3.0",
        "PyYAML==6.0",
        "requests==2.32.3",
        "six==1.16.0",
        "SQLAlchemy==2.0.33",
        "SQLAlchemy-Utils==0.41.2",
        "starlette_context==0.3.6",
        "uvicorn==0.22.0",
    ],

    entry_points="""
    [console_scripts]
    zix=zix:cli.entry_point
    """,
    packages=["zix"],
    package_data={
        # Use MANIFEST.ini
    },
    include_package_data=True
)
