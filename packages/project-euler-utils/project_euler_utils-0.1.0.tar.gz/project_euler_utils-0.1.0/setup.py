from setuptools import setup, find_packages

setup(
    name="project-euler-utils",
    author="Shlok Kothari",
    description="Utility functions to solve project-euler and math problems on computer",
    packages= find_packages(),
    version="0.1.0",
    install_requires=["numpy>=2.0"],
    python_requires=">=3.8",
)
