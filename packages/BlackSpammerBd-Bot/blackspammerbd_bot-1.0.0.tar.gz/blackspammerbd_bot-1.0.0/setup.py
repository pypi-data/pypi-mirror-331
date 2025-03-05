from setuptools import setup, find_packages

setup(
    name="BlackSpammerBd_Bot",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'requests',
        'sqlite3',
        'termux-api',
    ],
    entry_points={
        'console_scripts': [
            'bsb = BlackSpammerBd_Bot.main:main',
        ],
    },
)
