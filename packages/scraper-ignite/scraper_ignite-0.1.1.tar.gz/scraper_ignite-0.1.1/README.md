# Scraper Ignite

A simple web scraper project creator that automatically generates a basic project structure including extractors, parsers, pipelines, configuration, and more.

## Getting Started

This repository contains a utility package that, once installed, provides a CLI command to create a web scraper project structure automatically. The command is registered as a console script named `scraper-ignite`.

## Prerequisites

- Python 3.7 or higher
- [Requests](https://pypi.org/project/requests/)
- [BeautifulSoup](https://pypi.org/project/beautifulsoup4/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

## Setup and Usage

1. **Clone the Repository**

   Clone this repository to your local machine.

2. **Install the Package**

   From the root of the repository, install the package locally:

   ```sh
   pip install scraper-ignite
   ```

3. **Run the Project Setup Command**

   Execute the following command to generate the scraper project structure:

   ```sh
   scraper-ignite --project <your_project_name> # defaults to scraper_app
   ```

4. **Next Steps**

   After generating the project, follow these steps:

   - Navigate into the generated project directory:

     ```sh
     cd scraper_app
     ```

   - Create a virtual environment:

     ```sh
     python -m venv venv
     ```

   - Activate the virtual environment:

     - **Windows:**
       ```sh
       venv\Scripts\activate
       ```
     - **Mac/Linux:**
       ```sh
       source venv/bin/activate
       ```

   - Install the project dependencies:

     ```sh
     pip install -r requirements.txt
     ```

   - Run the scraper:

     ```sh
     python run.py
     ```

## License

This project is licensed under the MIT License.

## Author

Nahom D  
Email: nahom@nahom.eu.org
