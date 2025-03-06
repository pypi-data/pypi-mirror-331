from setuptools import setup, find_packages

setup(
    name="project_euler_utils",
    author="Shlok Kothari",
    description="Utility functions to solve project-euler and math problems",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    version="0.2.1",
    install_requires=["numpy>=2.0"],
    python_requires=">=3.1",
    long_description=open("README.md", encoding="utf-8").read(),  # Read from README.md
    long_description_content_type="text/markdown",  # Specifies Markdown format
)
