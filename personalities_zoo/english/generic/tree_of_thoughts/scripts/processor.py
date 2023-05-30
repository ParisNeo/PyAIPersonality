from pathlib import Path
from pyaipersonality import PAPScript, AIPersonality
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
        if self.word_callback is not None:
            self.word_callback(text)
        print(text,end="")
        sys.stdout.flush()
        self.bot_says = self.bot_says + text
        if self.personality.detect_antiprompt(self.bot_says):
            print("Detected hallucination")
            return False
        else:
            return True

    def generate(self, prompt):
        self.bot_says = ""
        return self.generate_fn(
                                prompt, 
                                self.config["max_judgement_size"], 
                                self.process
                                ).strip()        

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
        self.generate_fn = generate_fn
        self.word_callback = word_callback
        self.bot_says = ""

        # 1 first ask the model to formulate a query
        final_thoughts = []
        summary_prompt = ""
        for j in range(self.config["nb_thoughts"]):
            print(f"============= Starting level {j} of the tree =====================")
            local_thoughts=[]
            judgement_prompt = f"## Subject:\n{prompt.strip()}\n"
            for i in range(self.config["nb_samples_per_thought"]):
                print(f"\nThought {i+1}")
                thought_prompt = f"""### Prompt:
{prompt}
### Previous thoughts:
{final_thoughts.strip()}
### Instruction: 
Write the next thought. Please give a single thought. 
### Thought:"""
                thought = self.generate(thought_prompt)
                local_thoughts.append(thought.strip())
                judgement_prompt += f"\n### Thought {i}:{thought.strip()}\n"
                if step_callback is not None:
                    step_callback(f"\n### Thought {i+1}:\n"+thought,1)
            prompt_ids = ",".join([str(i) for i in range(self.config["nb_samples_per_thought"])])
            judgement_prompt += f"### Instruction: Which thought seems the most approcpriate. Answer the question by giving the best thought number without explanations.\nWhat is the best thought number {prompt_ids}?\n"
            print(judgement_prompt)
            self.bot_says = ""
            best_local_thought = self.generate(judgement_prompt).strip()
            number, index = find_matching_number([i for i in range(self.config["nb_samples_per_thought"])], best_local_thought)
            if index is not None:
                final_thoughts.append(local_thoughts[number]) 
                if step_callback is not None:
                    step_callback(f"### Best local thought:\n{best_local_thought}",1)
            else:
                print("Warning, the model made a wrong answer, taking random thought as the best")
                final_thoughts.append(local_thoughts[random.randint(0, self.config["nb_samples_per_thought"])]) 
                if step_callback is not None:
                    step_callback(f"### Best local thought:\n{best_local_thought}",1)

        summary_prompt += "### Instructions:\nCombine these thoughts in a comprihensive essai.\n"
        for thought in final_thoughts:
            summary_prompt += f"### Thought: {thought}\n"
        summary_prompt += "### Thoughts summary:\n"
        print(summary_prompt)
        best_local_thought = self.generate(summary_prompt)
        return best_local_thought


