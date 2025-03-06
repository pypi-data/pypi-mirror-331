
class JSONParser:
    def __init__(self):
        pass

    def extract_keys(self, data, keys):
        """
        Extract specific keys from a JSON object.

        Args:
            data (dict or list): The JSON data to parse.
            keys (list): A list of keys to extract from the JSON data.

        Returns:
            list: A list of dictionaries containing the specified keys.
        """
        if isinstance(data, list):
            return [{key: item.get(key) for key in keys} for item in data]
        else:
            return {key: data.get(key) for key in keys}
