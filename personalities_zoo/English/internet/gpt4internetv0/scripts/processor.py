from pyaipersonality import PAPScript, AIPersonality
import urllib.parse
import urllib.request
import json

from googleapiclient.discovery import build

def search_with_google_api(api_key, query, num_results):
    # Create a service object for the Google Search API
    service = build("customsearch", "v1", developerKey=api_key)
    
    # Perform the search
    response = service.cse().list(
        cx='GPT4Internet',  # Paris neo custom search engine id
        q=query,  # The search query
        num=num_results  # The number of results to retrieve
    ).execute()
    
    # Return the JSON response
    return response

    
class Processor(PAPScript):
    """
    A class that processes model inputs and outputs.

    Inherits from PAPScript.
    """

    def __init__(self, personality: AIPersonality) -> None:
        super().__init__()
        self.personality = personality
        # Verify your parameters
        if not "Google_Search_Key" in self.personality._processor_cfg.keys() or self.personality._processor_cfg["Google_Search_Key"]==0:
            print("No google search key is present. I won't be able to use internet search. Please set this in your personality parameters")



    def internet_search(self, query):
        """
        Perform an internet search using the provided query.

        Args:
            query (str): The search query.

        Returns:
            dict: The search result as a dictionary.
        """
        return search_with_google_api(
                                    self.personality.processor_cfg["Google_Search_Key"],
                                    query, 
                                    self.personality.processor_cfg["num_results"])

    def process_model_input(self, text):
        """
        Process the model input.

        Currently, this method returns None.

        Args:
            text (str): The model input text.

        Returns:
            None: Currently, this method returns None.
        """

        return "Summerize :\n" + str(self.internet_search(text))

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
        return None
