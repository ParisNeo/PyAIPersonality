from pyaipersonality import PAPScript, AIPersonality
import urllib.parse
import urllib.request
import json
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from functools import partial
import sys

def format_url_parameter(value:str):
    encoded_value = value.strip().replace("\"","")
    print(encoded_value)
    return encoded_value

def extract_results(url, max_num):
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode

    # Set path to chromedriver executable (replace with your own path)
    chromedriver_path = ""

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

    # Detect that no outputs are found
    Not_found = soup.find("No results found")

    if Not_found : 
        return []    

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
        results = extract_results(f"https://duckduckgo.com/?q={format_url_parameter(query)}&t=h_&ia=web", self.personality._processor_cfg["num_results"])
        for result in results:
            title = result["title"]
            content = result["content"]
            link = result["link"]
            formatted_text += f"--\n# title:\n{title}\n# content:\n{content}\n[source]({link})\n--\n\n"

        print("Searchengine results : ")
        print(formatted_text)
        return formatted_text, results

    def run_workflow(self, generate_fn, prompt, previous_discussion_text="", step_callback=None):
        """
        Runs the workflow for processing the model input and output.

        This method should be called to execute the processing workflow.

        Args:
            generate_fn (function): A function that generates model output based on the input prompt.
                The function should take a single argument (prompt) and return the generated text.
            prompt (str): The input prompt for the model.
            previous_discussion_text (str, optional): The text of the previous discussion. Default is an empty string.

        Returns:
            None
        """
        bot_says = ""
        def process(text, bot_says):
            print(text,end="")
            sys.stdout.flush()
            bot_says = bot_says + text
            if self.personality.detect_antiprompt(bot_says):
                return False
            else:
                return True

        # 1 first ask the model to formulate a query
        prompt = f"### Instruction:\nGenerate an enhanced internet search query out of this prompt:\n{prompt}\n### Optimized search query:\n"
        print(prompt)
        search_query = format_url_parameter(generate_fn(prompt, self.personality._processor_cfg["max_query_size"], partial(process,bot_says=bot_says)))
        if step_callback is not None:
            step_callback(search_query, 1)
        search_result, results = self.internet_search(search_query)
        if step_callback is not None:
            step_callback(search_result, 2)
        prompt = f"### Instruction:\nUse Search engine output to answer Human question. \nquestion:\n{search_query}\n### Search results:\n{search_result}\n### Single paragraph summary:\n"
        print(prompt)
        output = generate_fn(prompt, self.personality._processor_cfg["max_summery_size"], partial(process, bot_says=bot_says))
        sources_text = "\n# Sources :\n"
        for result in results:
            link = result["link"]
            sources_text += f"[source : {link}]({link})\n\n"

        output = output+sources_text
        if step_callback is not None:
            step_callback(output, 3)

        return output



