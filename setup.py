from setuptools import setup, find_packages

setup(
    name='lcpv',
    version="0.1",
    description="Low cost particle velocimetry",
    author="multiple",
    author_email="multiple",
    package_dir={"": "lcpv"},
    scripts=["lcpv/lcpv.py", "lcpv/lens_correction.py", "lcpv/unsharp_masking.py"],
    install_requires=[i.strip() for i in open("requirements.txt").readlines()],
)
