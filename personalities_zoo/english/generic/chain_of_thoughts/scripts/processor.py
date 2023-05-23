import subprocess
from pathlib import Path
import os
import sys
sd_folder = Path(__file__).resolve().parent.parent / "sd"
sys.path.append(str(sd_folder))
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
import yaml
  
class Processor(PAPScript):
    """
    A class that processes model inputs and outputs.

    Inherits from PAPScript.
    """

    def __init__(self, personality: AIPersonality) -> None:
        super().__init__()
        self.personality = personality
        self.config = self.load_config_file()

    def load_config_file(self):
        """
        Load the content of config_local.yaml file.

        The function reads the content of the config_local.yaml file and returns it as a Python dictionary.

        Args:
            None

        Returns:
            dict: A dictionary containing the loaded data from the config_local.yaml file.
        """        
        path = Path(__file__).parent.parent / 'config_local.yaml'
        with open(path, 'r') as file:
            data = yaml.safe_load(file)
        return data

    def run_workflow(self, generate_fn, prompt, previous_discussion_text="", step_callback=None, word_callback=None):
        """
        Runs the workflow for processing the model input and output.

        This method should be called to execute the processing workflow.

        Args:
            generate_fn (function): A function that generates model output based on the input prompt.
                The function should take a single argument (prompt) and return the generated text.
            prompt (str): The input prompt for the model.
            previous_discussion_text (str, optional): The text of the previous discussion. Default is an empty string.
            step_callback
        Returns:
            None
        """
        bot_says = ""
        def process(text, bot_says):
            if word_callback is not None:
                word_callback(text)
            print(text,end="")
            sys.stdout.flush()
            bot_says = bot_says + text
            if self.personality.detect_antiprompt(bot_says):
                return False
            else:
                return True

        # 1 first ask the model to formulate a query
        thoughts = []
        judgement_prompt = f"prompt:\n{prompt}\n"
        for i in range(self.personality._processor_cfg["nb_samples_per_thought"]):
            print(f"\nThought {i+1}")
            thought_prompt = f"""### Instruction: Write a single short sentence to describe a useful thought about this prompt.
### Prompt:{prompt}
### Thought:"""
            thought = generate_fn(
                                thought_prompt, 
                                self.personality._processor_cfg["max_thought_size"], 
                                partial(process,bot_says=bot_says)
                                )
            thoughts.append(thought.strip())
            judgement_prompt += f"\n### Thought {i+1}:{thought}:\n"
            if step_callback is not None:
                step_callback(f"\n### Thought {i+1}:\n",0)
                step_callback(thought,0)
        judgement_prompt += "### Instruction: Judge the previous thoughts and rewrite the best one\n### Best Thought:"
        print(judgement_prompt)
        judgement_thought = generate_fn(
                                judgement_prompt, 
                                self.config["max_judgement_size"], 
                                partial(process,bot_says=bot_says)
                                )
        

        step_callback("### Best thought:\n",0)
        return judgement_thought


