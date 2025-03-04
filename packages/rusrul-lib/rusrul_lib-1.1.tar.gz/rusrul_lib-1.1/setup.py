from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf_8")

setup(
    name="rusrul_lib",
    version="1.1",
    packages=find_packages(),
    install_requires=[],
    long_description=long_description,
    long_description_content_type='text/markdown'
)