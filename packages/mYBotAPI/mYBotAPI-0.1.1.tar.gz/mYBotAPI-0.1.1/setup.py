# setup.py

from setuptools import setup, find_packages

setup(
    name='mYBotAPI',
    version='0.1.1',
    packages=find_packages(),
    description='Ein Modul für den Zugriff auf die mYBot-API.',
    author='Yannic Basin',
    author_email='yannicbasin@gmail.com',
    url='https://mYBot.yb-tech.de',
    install_requires=[
        'requests',  # Abhängigkeiten hier hinzufügen
    ],
)

