# setup.py

from setuptools import setup, find_packages

setup(
    name='feature-lists-omkar130',  # Name of the library
    version='0.1.0',  # Version of your library
    packages=find_packages(),  # Automatically find all packages
    install_requires=[],  # List any dependencies (e.g., Django)
    description='A simple video bookmarking and rating system for Django.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Omkar Mahajan',
    author_email='mahajanomkar86@gmail.com',
    url='https://github.com/omkar130/feature_lists.git',  # Update with your GitHub repo URL
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
