# setup.py

from setuptools import setup, find_packages
from pathlib import Path

# Lange Beschreibung aus der README.md lesen
here = Path(__file__).parent
long_description = (here / "README.md").read_text(encoding='utf-8')

setup(
    name='mYBotAPI',
    version='0.1.3',
    packages=find_packages(),
    description='Ein Modul für den Zugriff auf die mYBot-API.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Yannic Basin',
    author_email='yannicbasin@gmail.com',
    url='https://mYBot.yb-tech.de',
    install_requires=[
        'requests',  # Abhängigkeiten hier hinzufügen
    ],
)

