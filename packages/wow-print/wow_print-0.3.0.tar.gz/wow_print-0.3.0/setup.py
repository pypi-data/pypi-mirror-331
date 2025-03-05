from setuptools import setup, find_packages

setup(
    name="wow-print",
    version="0.3.0",
    packages=find_packages(),
    install_requires=[],
    extras_require={
        "dev": [
            "pytest",
        ],
    },
    description="A package for colorizing text using ANSI escape codes",
    author="Ken",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6"
)
