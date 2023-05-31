######
# Project       : GPT4ALL-UI
# File          : binding.py
# Author        : ParisNeo with the help of the community
# Supported by Nomic-AI
# license       : Apache 2.0
# Description   : 
# This is an interface class for GPT4All-ui bindings.
######
from pathlib import Path
from typing import Callable
import inspect
import yaml
import sys
from tqdm import tqdm
import urllib

__author__ = "parisneo"
__github__ = "https://github.com/ParisNeo/gpt4all-ui"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"


import yaml

DEFAULT_CONFIG = {
    "version": 5,
    "user_name": "user",
    "config": "default",
    "ctx_size": 2048,
    "n_gpu_layers": 20,
    "db_path": "databases/database.db",
    "debug": False,
    "n_threads": 8,
    "host": "localhost",
    "language": "en-US",
    "binding": "gpt_4all",
    "model": None,
    "n_predict": 1024,
    "nb_messages_to_remember": 5,
    "personality_language": "english",
    "personality_category": "default",
    "personality": "gpt4all",
    "port": 9600,
    "repeat_last_n": 40,
    "repeat_penalty": 1.2,
    "seed": -1,
    "temperature": 0.9,
    "top_k": 50,
    "top_p": 0.95,
    "use_gpu": False,
    "auto_read": False,
    "use_avx2": True,
    "override_personality_model_parameters": False
}


class BindingConfig:
    def __init__(self, file_path=None):
        self.file_path = Path(file_path)
        self.config = None
        
        if file_path is not None:
            self.load_config(file_path)
        else:
            self.config = DEFAULT_CONFIG.copy()

    def check_model_existance(self):
        model_path = Path("models")/self.binding/self.model
        return model_path.exists()
    
    def download_model(self, url):
        folder_path = Path("models")/self.binding
        model_name  = url.split("/")[-1]
        model_full_path = (folder_path / model_name)

        # Check if file already exists in folder
        if model_full_path.exists():
            print("File already exists in folder")
        else:
            # Create folder if it doesn't exist
            folder_path.mkdir(parents=True, exist_ok=True)
            progress_bar = tqdm(total=None, unit="B", unit_scale=True, desc=f"Downloading {url.split('/')[-1]}")
            # Define callback function for urlretrieve
            def report_progress(block_num, block_size, total_size):
                progress_bar.total=total_size
                progress_bar.update(block_size)
            # Download file from URL to folder
            try:
                urllib.request.urlretrieve(url, folder_path / url.split("/")[-1], reporthook=report_progress)
                print("File downloaded successfully!")
            except Exception as e:
                print("Error downloading file:", e)
                sys.exit(1)

    def __getitem__(self, key):
        if self.config is None:
            raise ValueError("No configuration loaded.")
        return self.config[key]

    def __getattr__(self, key):
        if self.config is None:
            raise ValueError("No configuration loaded.")
        return self.config[key]


    def __setattr__(self, key, value):
        if key in ["file_path", "config"]:
            super().__setattr__(key, value)
        else:
            if self.config is None:
                raise ValueError("No configuration loaded.")
            self.config[key] = value

    def __setitem__(self, key, value):
        if self.config is None:
            raise ValueError("No configuration loaded.")
        self.config[key] = value
    
    def __contains__(self, item):
        if self.config is None:
            raise ValueError("No configuration loaded.")
        return item in self.config

    def load_config(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as stream:
            self.config = yaml.safe_load(stream)

    def save_config(self, file_path):
        if self.config is None:
            raise ValueError("No configuration loaded.")
        with open(file_path, "w") as f:
            yaml.dump(self.config, f)


class LLMBinding:
   
    file_extension='*.bin'
    binding_path = Path(__file__).parent
    def __init__(self, config:BindingConfig, inline:bool) -> None:
        self.config = config
        self.inline = inline


    def generate(self, 
                 prompt:str,                  
                 n_predict: int = 128,
                 new_text_callback: Callable[[str], None] = None,
                 verbose: bool = False,
                 **gpt_params ):
        """Generates text out of a prompt
        This should ber implemented by child class

        Args:
            prompt (str): The prompt to use for generation
            n_predict (int, optional): Number of tokens to prodict. Defaults to 128.
            new_text_callback (Callable[[str], None], optional): A callback function that is called everytime a new text element is generated. Defaults to None.
            verbose (bool, optional): If true, the code will spit many informations about the generation process. Defaults to False.
        """
        pass
    def tokenize(self, prompt):
        """
        Tokenizes the given prompt using the model's tokenizer.

        Args:
            prompt (str): The input prompt to be tokenized.

        Returns:
            list: A list of tokens representing the tokenized prompt.
        """
        pass

    def detokenize(self, tokens_list):
        """
        Detokenizes the given list of tokens using the model's tokenizer.

        Args:
            tokens_list (list): A list of tokens to be detokenized.

        Returns:
            str: The detokenized text as a string.
        """
        pass

    @staticmethod
    def list_models(config:dict):
        """Lists the models for this binding
        """
        models_dir = Path('./models')/config["binding"]  # replace with the actual path to the models folder
        return [f.name for f in models_dir.glob(LLMBinding.file_extension)]
    
    @staticmethod
    def get_available_models():
        # Create the file path relative to the child class's directory
        binding_path = Path(__file__).parent
        file_path = binding_path/"models.yaml"

        with open(file_path, 'r') as file:
            yaml_data = yaml.safe_load(file)
        
        return yaml_data

