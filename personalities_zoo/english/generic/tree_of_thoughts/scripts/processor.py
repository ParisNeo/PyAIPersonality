import subprocess
from pathlib import Path
import os
import sys
sd_folder = Path(__file__).resolve().parent.parent / "sd"
sys.path.append(str(sd_folder))
from pyaipersonality import PAPScript, AIPersonality, MSG_TYPE
import urllib.parse
import urllib.request
import json
import time

from functools import partial
import sys
import yaml
import re
import random

def find_matching_number(numbers, text):
    for index, number in enumerate(numbers):
        number_str = str(number)
        pattern = r"\b" + number_str + r"\b"  # Match the whole word
        match = re.search(pattern, text)
        if match:
            return number, index
    return None, None  # No matching number found
  
class Processor(PAPScript):
    """
    A class that processes model inputs and outputs.

    Inherits from PAPScript.
    """

    def __init__(self, personality: AIPersonality) -> None:
        super().__init__()
        self.personality = personality
        self.word_callback = None
        self.generate_fn = None
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
    

    def process(self, text):
        bot_says = self.bot_says + text
        if self.personality.detect_antiprompt(bot_says):
            print("Detected hallucination")
            return False
        else:
            self.bot_says = bot_says
            return True

    def generate(self, prompt, max_size):
        self.bot_says = ""
        return self.personality.model.generate(
                                prompt, 
                                max_size, 
                                self.process,
                                temperature=self.personality.model_temperature,
                                top_k=self.personality.model_top_k,
                                top_p=self.personality.model_top_p,
                                repeat_penalty=self.personality.model_repeat_penalty,
                                ).strip()    
        

    def run_workflow(self, prompt, previous_discussion_text="", callback=None):
        """
        Runs the workflow for processing the model input and output.

        This method should be called to execute the processing workflow.

        Args:
            generate_fn (function): A function that generates model output based on the input prompt.
                The function should take a single argument (prompt) and return the generated text.
            prompt (str): The input prompt for the model.
            previous_discussion_text (str, optional): The text of the previous discussion. Default is an empty string.
            callback a callback function that gets called each time a new token is received
        Returns:
            None
        """
        self.word_callback = callback
        self.bot_says = ""

        # 1 first ask the model to formulate a query
        final_ideas = []
        summary_prompt = ""
        for j in range(self.config.get("nb_ideas",3)):
            print(f"============= Starting level {j} of the tree =====================")
            local_ideas=[]
            judgement_prompt = f"### prompt:\n{prompt}\n"
            for i in range(self.config["nb_samples_per_idea"]):
                print(f"\nIdea {i+1}")
                if len(final_ideas)>0:
                    final_ideas_text = [f'Idea {n}:{i}' for n,i in enumerate(final_ideas)]
                    idea_prompt = f"""### Instruction: 
Write the next idea. Please give a single idea. 
### Prompt:
{prompt}
### Previous ideas:
{final_ideas_text}
### Idea:To"""
                else:
                    idea_prompt = f"""### Instruction: 
Write the next idea. Please give a single idea. 
### Prompt:
{prompt}
### Idea:"""
                print(idea_prompt)
                idea = self.generate(idea_prompt)
                local_ideas.append(idea.strip())
                judgement_prompt += f"\n### Idea {i}:{idea}\n"
                if callback is not None:
                    callback(f"\n### Idea {i+1}:\n"+idea, MSG_TYPE.MSG_TYPE_FULL)
            prompt_ids = ",".join([str(i) for i in range(self.config["nb_samples_per_idea"])])
            judgement_prompt += f"### Instructions:\nWhich idea seems the most approcpriate. Answer the question by giving the best idea number without explanations.\nWhat is the best idea number {prompt_ids}?\n"
            print(judgement_prompt)
            self.bot_says = ""
            best_local_idea = self.generate(judgement_prompt).strip()
            number, index = find_matching_number([i for i in range(self.config["nb_samples_per_idea"])], best_local_idea)
            if index is not None:
                print(f"Chosen thoght n:{number}")
                final_ideas.append(local_ideas[number]) 
                if callback is not None:
                    callback(f"### Best local idea:\n{best_local_idea}", MSG_TYPE.MSG_TYPE_FULL)
            else:
                print("Warning, the model made a wrond answer, taking random idea as the best")
                number = random.randint(0,self.config["nb_samples_per_idea"])-1
                print(f"Chosen thoght n:{number}")
                final_ideas.append(local_ideas[number]) 
                if callback is not None:
                    callback(f"### Best local idea:\n{best_local_idea}", MSG_TYPE.MSG_TYPE_FULL)

        summary_prompt += "### Instructions:\nCombine these ideas in a comprihensive essai.\n"
        for idea in final_ideas:
            summary_prompt += f"### Idea: {idea}\n"
        summary_prompt += "### Ideas summary:\n"
        print(summary_prompt)
        best_local_idea = self.generate(summary_prompt)
        return best_local_idea


