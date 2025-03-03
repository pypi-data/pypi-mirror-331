# setup.py
from setuptools import setup, find_packages

setup(
    name='tidyflow',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'scikit-learn'
    ],
    author='Ann Naser Nabil',
    author_email='ann.n.nabil@gmail.com',
    description='A lightweight data preprocessing toolbox',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/AnnNaser/tidyflow',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
