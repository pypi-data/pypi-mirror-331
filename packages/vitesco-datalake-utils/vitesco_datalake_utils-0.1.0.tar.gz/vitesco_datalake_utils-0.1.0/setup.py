from setuptools import setup, find_packages

setup(
    name="vitesco-datalake-utils",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "boto3",
        "requests",
        "aws-lambda-powertools",
        "mypy-boto3-s3",
    ],
    author="Adrian Birnea",
    author_email="adrian-ionut.birnea@vitesco.com",
    description="A package for interacting with the datalake API",
    url="https://github.vitesco.io/AI-Manufacturing-Support/labeling",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
