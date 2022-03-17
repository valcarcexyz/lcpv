from setuptools import setup, find_packages

setup(
    name="lpcv",
    version="0.1",
    description="Low cost particle velocimetry",
    author="multiple",
    author_email="multiple",
    license="TODO",
    url="TODO",
    packages=find_packages(),
    install_requires=[i.strip() for i in open("requirements.txt").readlines()],
    test_suit="tests"
)
