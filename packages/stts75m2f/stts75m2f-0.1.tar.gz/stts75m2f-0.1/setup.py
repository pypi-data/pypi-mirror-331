from setuptools import setup, find_packages

setup(
    name='stts75m2f',
    version='0.1',
    packages=find_packages(),
    install_requires=['smbus2'],
    author='Dariusz Kowalczyk',
    author_email='darton.dariusz.kowalczyk@gmail.com',
    description='Pythona library for STTS75M2F temperature sensor',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/darton/stts75m2f',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
