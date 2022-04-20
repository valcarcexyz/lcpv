from setuptools import setup, find_packages

setup(
    name='lcpv',
    version='0.1',
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    url='https://github.com/valcarce01/lcpv',
    license='',
    author='Diego Valcarce et al',
    author_email='d.valcarce@udc.es',
    description='Low cost (Rasperry-based) particle velociemtry',
    install_requires=[line.strip() for line in open("requirements.txt").readlines()],
    # todo: add the tests
)
