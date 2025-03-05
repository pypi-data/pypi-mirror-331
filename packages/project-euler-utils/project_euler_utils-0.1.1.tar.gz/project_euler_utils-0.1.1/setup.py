from setuptools import setup, find_packages

setup(
    name="project-euler-utils",
    author="Shlok Kothari",
    description="Utility functions to solve project-euler and math problems",
    packages= find_packages(),
    version="0.1.1",
    install_requires=["numpy>=2.0"],
    python_requires=">=3.8",
    long_description=open("README.md", encoding="utf-8").read(),  # Read from README.md
    long_description_content_type="text/markdown",  # Specifies Markdown format
)
