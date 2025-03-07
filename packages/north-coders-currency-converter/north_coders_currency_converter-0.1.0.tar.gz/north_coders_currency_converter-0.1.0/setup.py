from setuptools import setup, find_packages

setup(
    name="north_coders_currency_converter",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,  
    install_requires=[],
    description="A simple library for converting currency codes to full names and vice versa.",
    author="Hussein Alsakkaf",
    author_email="your.email@example.com",
    url="https://github.com/HusseinAlsakkaf",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
