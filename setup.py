import os
import sys
from setuptools import setup, find_packages


version = 0.2


with open('README.md', 'rt') as f:
    long_description = f.read()


with open('requirements.txt', 'rt') as f:
    requirements = tuple(f.read().split())


setup(
    name = 'gateaux',
    version = str(version),
    url = 'https://github.com/meeb/gateaux',
    author = 'https://github.com/meeb',
    author_email = 'meeb@meeb.org',
    description = 'Typed data structures for FoundationDB.',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    license = 'MIT',
    include_package_data = True,
    install_requires = requirements,
    packages = find_packages(),
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords = ('gateaux', 'foundationdb', 'fdb', 'data', 'structure', 'structures',
                'typed', 'typing'),
)
