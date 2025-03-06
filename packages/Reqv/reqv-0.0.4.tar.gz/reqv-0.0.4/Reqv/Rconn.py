
from .Rfetcher import Fetcher
from .Rparser import JSONParser

class Connect:
    def __init__(self, headers=None):
        self.fetcher = Fetcher(headers) 
        self.parser = JSONParser()  

    def fetch_data(self, url, params=None, keys=None):
        """
        Fetch data from a URL and optionally extract specific keys from the JSON response.
        """
        # Fetch the data (it will be in JSON format)
        data = self.fetcher.fetch_json(url, params)
        
        # If keys are provided, extract the specific keys from the data
        if keys:
            return self.parser.extract_keys(data, keys)
        
        # If no keys are provided, return the entire JSON data
        return data
