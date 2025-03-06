from setuptools import setup, find_packages

setup(
    name="z3kural",  
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    description="A Python package to fetch Thirukkural verses",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Z3Connect",
    author_email="z3connect.z3connect@gmail.com",  
    url="https://github.com/z3connect/z3kural",  
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
