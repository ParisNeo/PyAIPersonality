import requests
from pyaipersonality import PAPScript

class Processor(PAPScript):
    """
    A class that processes model inputs and outputs.

    Inherits from PAPScript.
    """

    def __init__(self) -> None:
        super().__init__()

    def internet_search(self, query):
        """
        Perform an internet search using the provided query.

        Args:
            query (str): The search query.

        Returns:
            dict: The search result as a dictionary.
        """
        url = f"https://parisneo.pythonanywhere.com/search?&q={query}"
        response = requests.get(url)
        json_data = response.json()
        return json_data

    def process_model_input(self, text):
        """
        Process the model input.

        Currently, this method returns None.

        Args:
            text (str): The model input text.

        Returns:
            None: Currently, this method returns None.
        """
        return None

    def process_model_output(self, text):
        """
        Process the model output.

        If the output contains a search query, perform an internet search.

        Args:
            text (str): The model output text.

        Returns:
            dict or None: The search result as a dictionary if a search query is found,
                otherwise returns None.
        """
        sequence = "search_query:"
        index = text.find(sequence)
        if index != -1:
            query = text[index + len(sequence):]
            search_result = self.internet_search(query)
            return search_result
        else:
            return None
