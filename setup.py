from pathlib import Path

import setuptools

setuptools.setup(
    name="census-rm-qid-batch-runner",
    version="0.0.1",
    description="Scripts to request qid pairs and generate print files",
    long_description=Path('README.md').read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/ONSdigital/census-rm-qid-batch-runner",
    packages=setuptools.find_packages(),
)
