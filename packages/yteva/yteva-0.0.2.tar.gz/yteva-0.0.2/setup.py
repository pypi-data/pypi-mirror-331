from setuptools import setup, find_packages

setup(
    name="yteva",
    version="0.0.2",
    packages=find_packages(),
    install_requires=[
        "requests",
        "httpx==0.25.0",
        "pyrofork"
    ],
    author="Eslam",
    author_email="your_email@example.com",
    description="A simple library to fetch and download audio.",
    url="https://t.me/sourceeva",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
