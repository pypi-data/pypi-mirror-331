from setuptools import setup, find_packages

setup(
    name="metrixify",
    version="0.1.0",
    author="SSP",
    author_email="susmit.vssut@gmail.com",
    description="A Python library for automatic model evaluation",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/susmitsekhar/metrixify",  # Replace with your GitHub repo link
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "scikit-learn>=1.0.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
