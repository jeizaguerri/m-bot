import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Optional

def search_and_save_image(query: str) -> Optional[str]:
    """
    Searches for an image online using Bing and saves the first result to the 'example_data' folder.

    Args:
    query (str): The search query.

    Returns:
    Optional[str]: The path to the saved image, or None if an error occurred.
    """
    # Set the User-Agent header to mimic a browser request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    # Construct the search URL
    url = "https://www.bing.com/images/search"
    params = {"q": query}

    try:
        # Send a GET request to the search URL
        response = requests.get(url, headers=headers, params=params)

        # Check if the request was successful
        if response.status_code != 200:
            print(f"Failed to retrieve search results. Status code: {response.status_code}")
            return None

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the first image result
        image_result = soup.find("img", {"class": "mimg"})

        # Check if an image result was found
        if image_result is None:
            print("No image results found.")
            return None

        # Get the image URL
        image_url = image_result["src"]

        # Check if the image URL is relative or absolute
        if not bool(urlparse(image_url).netloc):
            image_url = urljoin(url, image_url)

        # Send a GET request to the image URL
        image_response = requests.get(image_url, headers=headers)

        # Check if the request was successful
        if image_response.status_code != 200:
            print(f"Failed to retrieve image. Status code: {image_response.status_code}")
            return None

        # Save the image to the 'example_data' folder
        image_path = os.path.join("example_data", f"{query}.jpg")
        with open(image_path, "wb") as file:
            file.write(image_response.content)

        return image_path

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

# Example usage:
search_query = "mountain"
print(search_and_save_image(search_query))