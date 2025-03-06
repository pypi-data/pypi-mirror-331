
import httpx

class Fetcher:
    def __init__(self, headers=None):
        self.headers = headers if headers else {}

    def fetch_json(self, url, params=None):
        """
        Fetch JSON data from a URL using an HTTP GET request.

        Args:
            url (str): The URL to fetch data from.
            params (dict, optional): Query parameters for the GET request.

        Returns:
            dict: The JSON data from the response.
        """
        with httpx.Client() as client:
            response = client.get(url, params=params, headers=self.headers)
            response.raise_for_status()  # Raise an exception if the request fails
            return response.json()
