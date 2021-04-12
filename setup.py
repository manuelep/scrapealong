# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='scrapealong',
    version='0.1.0',
    description='Async scraping library',
    long_description=readme,
    author='Manuele Pesenti',
    author_email='manuele@inventati.org',
    url='https://github.com/manuelep/scrapealong',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires = [
        'aiohttp',
        'bs4',
        'price-parser',
        'pyppeteer',
        'nest_asyncio',
        'diskcache'
    ]
)
