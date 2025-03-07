from setuptools import setup, find_packages

setup(
    name="scraper_ignite",
    version="0.1.0",
    description="A simple Scraper template creator",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Nahom D",
    author_email="nahom@nahom.eu.org",
    url="https://github.com/nahom-d54/scraper-ignite",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["httpx", "bs4"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "scraper_ignite=scraper_ignite.scraper_template:main",
        ],
    },
)
