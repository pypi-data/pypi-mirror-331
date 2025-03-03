from setuptools import setup, find_packages

setup(
    name="dias-scraper",
    version="1.0.0",
    author="YGNT7777",
    url="https://github.com/YGNT7777/Dias-Scraper",
    description="A command line tool to check your grades for Ionian University",
    packages=find_packages(),
    install_requires=[
        "playwright",
        "colorama",
    ],
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'dias-scraper=dias_scraper:diasScraper',  # Ensure this points to the correct function
        ],
    },
    license="MIT",
    keywords=['Ionian University', 'Dias Scraper'],
)
