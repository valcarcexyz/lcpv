from setuptools import setup, find_packages

setup(
    name='lcpv',
    version="0.1",
    description="Low cost particle velocimetry",
    author="multiple",
    author_email="multiple",
    package_dir={"": "lcpv"},
    packages=find_packages("lcpv"),
    install_requires=[i.strip() for i in open("requirements.txt").readlines()],
)
