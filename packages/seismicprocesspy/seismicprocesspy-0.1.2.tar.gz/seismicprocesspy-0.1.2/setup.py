from setuptools import setup, find_packages

setup(
    name='seismicprocesspy',
    version='0.1.2',
    description='A Python package for probabilistic seismic hazard analysis (PSHA)',
    author='Albert Pamonag',
    author_email='albert@apeconsultancy.net',
    url='https://github.com/albertp16/apec-py-psha',
    packages=find_packages(),
    install_requires=[
        'pandas','matplotlib'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    company='Albert Pamonag Engineering Consultancy',
)
