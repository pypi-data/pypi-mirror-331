from setuptools import setup, find_packages

setup(
    name="BlackSpammerBd_Bot",
    version="0.1",
    description="A tool to send updates via Telegram based on device logs.",
    author="Shawpon Sp",
    author_email="shawponsp6@gmail.com",
    url="https://github.com/BlackSpammerBd/NETSHIFT",
    packages=find_packages(),
    install_requires=[
        "requests",
        "sqlite3",
        "argparse",
    ],
    entry_points={
        'console_scripts': [
            'bsb=blackspammerbd_bot.main:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
