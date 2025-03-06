from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="image_processing-nathcsm",
    version="0.0.1",
    author="Nathalia",
    author_email="nathalia.pcosim@gmail.com",
    description="Pacote image_processing-nathcsm",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nathaliacosim/image-processing-package",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
)
