######
# Project       : GPT4ALL-UI
# File          : binding.py
# Author        : ParisNeo with the help of the community
# Supported by Nomic-AI
# license       : Apache 2.0
# Description   : 
# This is an interface class for GPT4All-ui bindings.


# This binding is a wrapper to gpt4all's official binding
# Follow him on his github project : https://github.com/ParisNeo/gpt4all

######
from pathlib import Path
from typing import Callable
from gpt4all import GPT4All
from pyaipersonality.binding import LLMBinding
from pyaipersonality  import MSG_TYPE
import yaml

__author__ = "parisneo"
__github__ = "https://github.com/ParisNeo/gpt4all-ui"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"

binding_name = "GPT4ALL"
binding_folder_name = "gpt_4all"


class GPT4ALL(LLMBinding):
    file_extension='*.bin'
    
    def __init__(self, config:dict) -> None:
        """Builds a GPT4ALL binding

        Args:
            config (dict): The configuration file
        """
        super().__init__(config, False)
        self.model = GPT4All.get_model_from_name(self.config['model'])
        self.model.load_model(
                model_path=f"./models/{binding_folder_name}/{self.config['model']}"
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
                 callback: Callable[[str], None] = bool,
                 verbose: bool = False,
                 **gpt_params ):
        """Generates text out of a prompt

        Args:
            prompt (str): The prompt to use for generation
            n_predict (int, optional): Number of tokens to predict. Defaults to 128.
            callback (Callable[[str], None], optional): A callback function that is called every time a new text element is generated. Defaults to None.
            verbose (bool, optional): If true, the code will spit many information about the generation process. Defaults to False.
            **gpt_params: Additional parameters for GPT generation.
                temperature (float, optional): Controls the randomness of the generated text. Higher values (e.g., 1.0) make the output more random, while lower values (e.g., 0.2) make it more deterministic. Defaults to 0.7 if not provided.
                top_k (int, optional): Controls the diversity of the generated text by limiting the number of possible next tokens to consider. Defaults to 0 (no limit) if not provided.
                top_p (float, optional): Controls the diversity of the generated text by truncating the least likely tokens whose cumulative probability exceeds `top_p`. Defaults to 0.0 (no truncation) if not provided.
                repeat_penalty (float, optional): Adjusts the penalty for repeating tokens in the generated text. Higher values (e.g., 2.0) make the model less likely to repeat tokens. Defaults to 1.0 if not provided.

        Returns:
            str: The generated text based on the prompt
        """
        default_params = {
            'temperature': 0.7,
            'top_k': 50,
            'top_p': 0.0,
            'repeat_penalty': 1.3,
            'repeat_last_n': 10
        }
        gpt_params = {**default_params, **gpt_params}
        try:
            response_text = []
            def local_callback(token_id, response):
                decoded_word = response.decode('utf-8')
                response_text.append( decoded_word )
                if callback is not None:
                    if not callback(decoded_word, MSG_TYPE.MSG_TYPE_CHUNK):
                        return False

                # Do whatever you want with decoded_token here.

                return True
            self.model._response_callback = local_callback
            self.model.generate(prompt, 
                                           n_predict=n_predict,                                           
                                            temp=gpt_params["temperature"],
                                            top_k=gpt_params['top_k'],
                                            top_p=gpt_params['top_p'],
                                            repeat_penalty=gpt_params['repeat_penalty'],
                                            repeat_last_n = self.config['repeat_last_n'],
                                            # n_threads=self.config['n_threads'],
                                            streaming=False,
                                           )
        except Exception as ex:
            print(ex)
        return ''.join(response_text)

    @staticmethod
    def get_available_models():
        # Create the file path relative to the child class's directory
        binding_path = Path(__file__).parent
        file_path = binding_path/"models.yaml"

        with open(file_path, 'r') as file:
            yaml_data = yaml.safe_load(file)
        
        return yaml_data