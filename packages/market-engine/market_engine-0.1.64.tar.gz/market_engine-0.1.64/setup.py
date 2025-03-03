from setuptools import setup, find_packages

setup(
    name='market-engine',
    version='0.1.64',
    description='Engine for easily getting the orders, statistics, and other stats from warframe.market.',
    author='Jacob McBride',
    author_email='jake55111@gmail.com',
    packages=find_packages(),
    install_requires=[
        'aiohttp~=3.9.3',
        'aiolimiter~=1.1.0',
        'redis~=5.0.3',
        'requests~=2.31.0',
        'beautifulsoup4~=4.12.2',
        'PyMySQL~=1.1.0',
        'fuzzywuzzy~=0.18.0',
        'pytz~=2023.3',
        'python-Levenshtein~=0.25.0',
        'beautifulsoup4~=4.12.2',
        'Markdown~=3.4.3',
        'cryptography~=42.0.5',
        'tenacity~=8.2.2',
        'pymysql-pool~=0.4.6'
    ],
)