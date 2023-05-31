######
# Project       : GPT4ALL-UI
# File          : binding.py
# Author        : ParisNeo with the help of the community
# Underlying binding : Abdeladim's pygptj binding
# Supported by Nomic-AI
# license       : Apache 2.0
# Description   : 
# This is an interface class for GPT4All-ui bindings.

# This binding is a wrapper to marella's binding
# Follow him on his github project : https://github.com/marella/gpt4all-j 

######
from pathlib import Path
from typing import Callable
from gpt4allj import Model
from pyaipersonality.binding import LLMBinding
import yaml

__author__ = "parisneo"
__github__ = "https://github.com/ParisNeo/gpt4all-ui"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"

binding_name = "GPTJ"
binding_folder_name = "gpt_j_m"

class GPTJ(LLMBinding):
    file_extension='*.bin'
    def __init__(self, config:dict) -> None:
        """Builds a LLAMACPP binding

        Args:
            config (dict): The configuration file
        """
        super().__init__(config, False)
        
        self.model = Model(
                model=f"./models/{binding_folder_name}/{self.config['model']}", avx2 = self.config["use_avx2"]
                )
    def tokenize(self, prompt):
        """
        Tokenizes the given prompt using the model's tokenizer.

        Args:
            prompt (str): The input prompt to be tokenized.

        Returns:
            list: A list of tokens representing the tokenized prompt.
        """
        return None

    def detokenize(self, tokens_list):
        """
        Detokenizes the given list of tokens using the model's tokenizer.

        Args:
            tokens_list (list): A list of tokens to be detokenized.

        Returns:
            str: The detokenized text as a string.
        """
        return None
    def generate(self, 
                 prompt:str,                  
                 n_predict: int = 128,
                 new_text_callback: Callable[[str], None] = bool,
                 verbose: bool = False,
                 **gpt_params ):
        """Generates text out of a prompt

        Args:
            prompt (str): The prompt to use for generation
            n_predict (int, optional): Number of tokens to prodict. Defaults to 128.
            new_text_callback (Callable[[str], None], optional): A callback function that is called everytime a new text element is generated. Defaults to None.
            verbose (bool, optional): If true, the code will spit many informations about the generation process. Defaults to False.
        """
        try:
            self.model.reset()
            output = ""
            for tok in self.model.generate(
                                            prompt, 
                                            seed=self.config['seed'],
                                            n_threads=self.config['n_threads'],
                                            n_predict=n_predict,
                                            top_k=gpt_params['top_k'],
                                            top_p=gpt_params['top_p'],
                                            temp=gpt_params["temperature"],
                                            repeat_penalty=gpt_params['repeat_penalty'],
                                            repeat_last_n=self.config['repeat_last_n'],
                                            n_batch=8,
                                            reset=True,
                                           ):
                output += tok
                if new_text_callback is not None:
                    if not new_text_callback(tok):
                        return output
        except Exception as ex:
            print(ex)
        return output
    @staticmethod
    def get_available_models():
        # Create the file path relative to the child class's directory
        binding_path = Path(__file__).parent
        file_path = binding_path/"models.yaml"

        with open(file_path, 'r') as file:
            yaml_data = yaml.safe_load(file)
        
        return yaml_data