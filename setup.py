from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='lcpv',
    version="0.1",
    description="Low cost particle velocimetry",
    long_description=long_description,
    author="multiple",
    author_email="multiple",
    url="https://github.com/valcarce01/lcpv",
    package_dir={"": "lcpv"},
    # scripts=["lcpv/lcpv.py", "lcpv/lens_correction.py", "lcpv/unsharp_masking.py"],
    packages=find_packages(where=""),
    install_requires=[i.strip() for i in open("requirements.txt").readlines()],
)
