# setup.py
from setuptools import setup, find_packages

setup(
    name="api-wg-simple",
    version="0.9",
    packages=find_packages(),
    install_requires=[
        "aiohttp",
        "pydantic"
    ],
    author="Alexandr",
    author_email="sander.sisoev@gmil.com",
    description="A simple API connector for interacting with WireGuard API",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/beardrubyblue/api-wg-simple",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
