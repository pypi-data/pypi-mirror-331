from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()
    
setup(
    name="Latex_toolkit",
    version=0.1,
    packages=find_packages(),
    install_requires=[
    
    ],
    entry_points={
        "console_scripts": [
            "Latex_toolkit = Latex_toolkit.main:main",
        ],
    },
    long_description = description,
    long_description_content_type = "text/markdown",
)