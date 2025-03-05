from setuptools import setup, find_packages

setup(
    name="metrixify",
    version="0.3.0",
    author="Susmit Sekhar Panda",  # ✅ Use your actual name
    author_email="susmit.vssut@gmail.com",  # ✅ Your actual email
    description="A Python library for automatic model evaluation",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/susmitsekhar/metrixify",
    packages=find_packages(),  # ✅ This ensures the metrixify module is included
    include_package_data=True,  # ✅ Ensures additional files (README, LICENSE) are included
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


