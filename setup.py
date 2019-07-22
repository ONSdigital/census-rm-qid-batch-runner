from pathlib import Path

import setuptools

setuptools.setup(
    name="census_rm_qid_batch_runner",
    version="1.0.0",
    description="Scripts to request qid pairs and generate print files",
    long_description=Path('README.md').read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/ONSdigital/census-rm-qid-batch-runner",
    packages=setuptools.find_packages(),
)
