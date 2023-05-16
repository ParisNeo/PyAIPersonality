from pyaipersonality import PAPScript, AIPersonality
import urllib.parse
import urllib.request
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def extract_results(url, max_num):
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode

    # Set path to chromedriver executable (replace with your own path)
    chromedriver_path = "path/to/chromedriver"

    # Create a new Chrome webdriver instance
    driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)

    # Load the webpage
    driver.get(url)

    # Wait for JavaScript to execute and get the final page source
    html_content = driver.page_source

    # Close the browser
    driver.quit()

    # Parse the HTML content
    soup = BeautifulSoup(html_content, "html.parser")

    # Find the <ol> tag with class="react-results--main"
    ol_tag = soup.find("ol", class_="react-results--main")

    # Initialize an empty list to store the results
    results_list = []

    # Find all <li> tags within the <ol> tag
    li_tags = ol_tag.find_all("li")

    # Loop through each <li> tag, limited by max_num
    for index, li_tag in enumerate(li_tags):
        if index > max_num:
            break

        try:
            # Find the three <div> tags within the <article> tag
            div_tags = li_tag.find_all("div")

            # Extract the link, title, and content from the <div> tags
            links = div_tags[0].find_all("a")
            span = links[1].find_all("span")
            link = span[0].text.strip()

            title = div_tags[2].text.strip()
            content = div_tags[3].text.strip()

            # Add the extracted information to the list
            results_list.append({
                "link": link,
                "title": title,
                "content": content
            })
        except Exception:
            pass

    return results_list

   
class Processor(PAPScript):
    """
    A class that processes model inputs and outputs.

    Inherits from PAPScript.
    """

    def __init__(self, personality: AIPersonality) -> None:
        super().__init__()
        self.personality = personality

    
    def internet_search(self, query):
        """
        Perform an internet search using the provided query.

        Args:
            query (str): The search query.

        Returns:
            dict: The search result as a dictionary.
        """
        formatted_text = ""
        results = extract_results(f"https://duckduckgo.com/?q={query}&t=h_&ia=web", self.personality._processor_cfg["num_results"])
        for result in results:
            title = result["title"]
            content = result["content"]
            link = result["link"]
            formatted_text += f"- {title}: {content}\n{link}\n\n"

        print("Searchengine results : ")
        print(formatted_text)
        return formatted_text

    def process_model_input(self, text):
        """
        Process the model input.

        Currently, this method returns None.

        Args:
            text (str): The model input text.

        Returns:
            None: Currently, this method returns None.
        """

        return "### Search engine:\n"+str(self.internet_search(text))+"### Human:\n"+text

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
