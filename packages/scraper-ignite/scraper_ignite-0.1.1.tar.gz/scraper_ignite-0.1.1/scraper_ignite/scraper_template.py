"""
This script creates a folder structure for a web scraper project and populates it with a generic scraper template.
Run this script in the desired project directory to set up the structure.
After running, customize '<project_name>/app/scrapers/scraper_template.py' for your specific scraping needs.

Usage:
    python script.py --project my_scraper_project
"""

from pathlib import Path
import argparse
import os

# Define the scraper template code as a string
SCRAPER_TEMPLATE_CODE = """
import httpx
from bs4 import BeautifulSoup as bs
from typing import Dict, List, Any

class Scraper:
    \"\"\"
    A generic scraper template.
    Subclasses should implement parse_page, process_item, and run methods.
    \"\"\"
    def __init__(self, base_url: str, headers: Dict[str, str] = None):
        \"\"\"
        Initialize the scraper with a base URL and optional headers.

        Args:
            base_url (str): The starting URL to scrape.
            headers (Dict[str, str], optional): HTTP headers for requests.
        \"\"\"
        self.base_url = base_url
        self.headers = headers or {}
        self.client = httpx.Client(follow_redirects=True, timeout=30, headers=self.headers)

    def get_page(self, url: str, params: Dict[str, Any] = None) -> str:
        \"\"\"
        Fetch the HTML content of a page.

        Args:
            url (str): The URL to fetch.
            params (Dict[str, Any], optional): Query parameters for the request.

        Returns:
            str: HTML content if successful, empty string otherwise.
        \"\"\"
        try:
            response = self.client.get(url, params=params)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Failed to fetch {url}: {response.status_code}")
                return ""
        except httpx.HTTPStatusError as e:
            print(f"Error fetching {url}: {e}")
            return ""

    def parse_page(self, html_content: str) -> List[Dict[str, Any]]:
        \"\"\"
        Parse the HTML content to extract items.
        Must be implemented by subclasses.

        Args:
            html_content (str): HTML content to parse.

        Returns:
            List[Dict[str, Any]]: List of extracted items.
        \"\"\"
        raise NotImplementedError("Subclasses must implement this method")

    def process_item(self, item: Dict[str, Any]) -> bool:
        \"\"\"
        Process an individual item.
        Must be implemented by subclasses.

        Args:
            item (Dict[str, Any]): The item to process.

        Returns:
            bool: True if processed successfully, False otherwise.
        \"\"\"
        raise NotImplementedError("Subclasses must implement this method")

    def run(self):
        \"\"\"
        Run the scraper.
        Must be implemented by subclasses to define the scraping logic.
        \"\"\"
        raise NotImplementedError("Subclasses must implement this method")

    def __del__(self):
        \"\"\"Close the HTTP client when the scraper is destroyed.\"\"\"
        self.client.close()

class ExampleScraper(Scraper):
    \"\"\"
    An example subclass of Scraper.
    Customize this for a specific website by implementing the methods below.
    \"\"\"
    def parse_page(self, html_content: str) -> List[Dict[str, Any]]:
        \"\"\"
        Example parsing logic.
        Replace with actual parsing code for the target website.

        Args:
            html_content (str): HTML content to parse.

        Returns:
            List[Dict[str, Any]]: List of extracted items.
        \"\"\"
        soup = bs(html_content, "html.parser")
        items = []
        # TODO: Implement parsing logic here
        # Example:
        # for element in soup.find_all("div", class_="item"):
        #     item = {
        #         "name": element.find("span", class_="name").text,
        #         "price": element.find("span", class_="price").text
        #     }
        #     items.append(item)
        return items

    def process_item(self, item: Dict[str, Any]) -> bool:
        \"\"\"
        Example item processing.
        Replace with actual processing logic (e.g., save to DB, send to queue).

        Args:
            item (Dict[str, Any]): The item to process.

        Returns:
            bool: True if processed successfully.
        \"\"\"
        print(f"Processing item: {item}")
        # TODO: Implement processing logic here
        return True

    def run(self):
        \"\"\"
        Example run logic assuming pagination with a "page" parameter.
        Scrapes pages until no more items are found.
        \"\"\"
        page = 1
        while True:
            html_content = self.get_page(self.base_url, params={"page": page})
            if not html_content:
                break
            items = self.parse_page(html_content)
            if not items:
                break
            for item in items:
                self.process_item(item)
            page += 1

class LocalExampleScraper(ExampleScraper):
    \"\"\"
    A subclass for local testing, collecting items in a list.
    \"\"\"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.all_items = []

    def process_item(self, item: Dict[str, Any]) -> bool:
        \"\"\"
        Collect items in a list for testing purposes.

        Args:
            item (Dict[str, Any]): The item to process.

        Returns:
            bool: True if added successfully.
        \"\"\"
        self.all_items.append(item)
        return True

if __name__ == "__main__":
    # Example usage:
    # 1. Specify the URL to scrape
    url = "https://example.com/items"
    # 2. Create an instance of the scraper
    scraper = LocalExampleScraper(url)
    # 3. Run the scraper
    scraper.run()
    # 4. Access the scraped items
    print(f"Scraped {len(scraper.all_items)} items")
    # Note: For production, implement 'process_item' in a subclass
"""


def create_structure(base_dir: str, project_name: str):
    """
    Create the folder structure and populate files for the scraper template.

    Args:
        base_dir (str): The base directory where the project will be created.
        project_name (str): The name of the project directory.
    """
    errors = []
    base_path = Path(base_dir) / project_name

    directories = [
        base_path / "app" / "scrapers",
        base_path / "app" / "services",
        base_path / "tests" / "scrapers",
    ]
    files = {
        base_path / "app" / "scrapers" / "__init__.py": "",
        base_path / "app" / "scrapers" / "scraper_template.py": SCRAPER_TEMPLATE_CODE,
        base_path
        / "requirements.txt": "httpx\nbeautifulsoup4\n",  # Corrected to match import
    }

    # Create directories
    for directory in directories:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {directory}")
        except Exception as e:
            errors.append(f"Error creating directory {directory}: {e}")

    # Create files
    for file_path, content in files.items():
        try:
            file_path.write_text(content)
            print(f"Created file: {file_path}")
        except Exception as e:
            errors.append(f"Error creating file {file_path}: {e}")

    # Provide summary
    if errors:
        print("Some errors occurred during structure creation:")
        for error in errors:
            print(error)
    else:
        print(f"Structure for '{project_name}' created successfully in {base_dir}.")


def main():
    """Create the project structure based on command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a web scraper project structure."
    )
    parser.add_argument(
        "--project",
        type=str,
        default="scraper_project",
        help="Name of the project directory (default: scraper_project)",
    )
    args = parser.parse_args()

    # Use the current working directory as the base and create the project folder
    base_dir = os.getcwd()
    create_structure(base_dir, args.project)


if __name__ == "__main__":
    main()
