from setuptools import setup 

setup(
    name='lcpv',
    version='0.1',
    package_dir={"": "lcpv"},
    url='https://github.com/valcarce01/lcpv',
    license='',
    author='Diego Valcarce Ríos,\
            Juan Ramón Rabuñal Dopico,\
            Juan Naves García-Rendueles,\
            José Anta Álvarez,\
            Sonia Seijo Conchado',
    author_email='d.valcarce@udc.es',
    description='Low cost (Rasperry-based) particle velociemtry',
    install_requires=[line.strip() for line in open("requirements.txt").readlines()],
    extras_require={
        "raspberry": ["picamera"],
    },
)
