

__author__ = "ParisNeo"
__github__ = "https://github.com/ParisNeo/PyAIPersonality"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"

import yaml
from pathlib import Path
from PIL import Image
from typing import Optional, List
import pkg_resources
from distutils.version import StrictVersion
import re
from datetime import datetime

class AIPersonality:

    # Extra 
    Conditionning_commands={
        "date_time": datetime.now().strftime("%A, %B %d, %Y %I:%M:%S %p"), # Replaces {{date}} with actual date
        "date": datetime.now().strftime("%A, %B %d, %Y"), # Replaces {{date}} with actual date
        "time": datetime.now().strftime("%H:%M:%S"), # Replaces {{time}} with actual time
    }
    
    def __init__(self, personality_package_path: str|Path = None):
        """
        Initialize an AIPersonality instance.

        Parameters:
        personality_package_path (str or Path): The path to the folder containing the personality package.

        Raises:
        ValueError: If the provided path is not a folder or does not contain a config.yaml file.
        """

        # First setup a default personality
        # Version
        self.version = pkg_resources.get_distribution('pyaipersonality').version

        #General information
        self.name: str = "gpt4all"
        self.user_name: str = "user"
        self.language: str = "en_XX"
        self.category: str = "General"

        # Conditionning
        self.personality_description: str = "This personality is a helpful and Kind AI ready to help you solve your problems"
        self.personality_conditioning: str = "GPT4All is a smart and helpful Assistant built by Nomic-AI. It can discuss with humans and assist them.\nDate: {{date}}"
        self.welcome_message: str = "Welcome! I am GPT4All A free and open assistant. What can I do for you today?"
        self.user_message_prefix: str = "### Human:"
        self.link_text: str = "\n"
        self.ai_message_prefix: str = "### Assistant:"
        self.anti_prompts:list = ["#","###","Human:","Assistant:"]

        # Extra
        self.dependencies: List[str] = []

        # Disclaimer
        self.disclaimer: str = ""

        
        # Default model parameters
        self.model_temperature: float = 0.8 # higher: more creative, lower more deterministic
        self.model_n_predicts: int = 1024 # higher: generates many words, lower generates
        self.model_top_k: int = 50
        self.model_top_p: float = 0.95
        self.model_repeat_penalty: float = 1.3
        self.model_repeat_last_n: int = 40

        self._logo: Optional[Image.Image] = None



        if personality_package_path is None:
            return
        else:
            self.personality_package_path = Path(personality_package_path)

            # Validate that the path exists
            if not self.personality_package_path.exists():
                raise ValueError("The provided path does not exist.")

            # Validate that the path format is OK with at least a config.yaml file present in the folder
            if not self.personality_package_path.is_dir():
                raise ValueError("The provided path is not a folder.")

            # Open and store the personality
            self.load_personality(personality_package_path)


    def load_personality(self, package_path:Path|str=None):
        """
        Load the personality data from a YAML file and set it as attributes of the class.

        Parameters:
        file_path (str or Path): The path to the YAML file containing the personality data. 
        If none, the current package path is used

        Returns:
        dict: A dictionary containing the personality data.
        """
        if package_path is None:
            package_path = self.personality_package_path
        else:
            package_path = Path(package_path)
        # Verify that there is at least a configuration file
        config_file = package_path / "config.yaml"
        if not config_file.exists():
            raise ValueError(f"The provided folder {package_path} does not exist.")


        with open(config_file, 'r', encoding='utf-8') as stream:
            config = yaml.safe_load(stream)

        # Set the personality attributes
        for key, value in config.items():
            setattr(self, key, value)

        # Rework the conditionning to add information
        self.personality_conditioning = self.replace_keys(self.personality_conditioning, self.Conditionning_commands)

        self.personality_package_path = package_path

        # Check for a logo file
        logo_path = self.personality_package_path / "assets" / "logo.png"
        if logo_path.is_file():
            self._logo = Image.open(logo_path)

        return config

    def save_personality(self, config, filepath=None):
        """
        Save the personality data to a YAML file.

        Parameters:
        config (dict): A dictionary containing the personality data.
        filepath (str or Path): The path to the file where the personality data will be saved.
            If None, the default file path will be used.
        """
        if filepath is None:
            filepath = self.personality_package_path / "config.yaml"
        with open(filepath, "w") as f:
            yaml.dump(config, f)

        # Create the assets folder if it doesn't exist
        assets_folder = self.personality_package_path / "assets"
        if not assets_folder.exists():
            assets_folder.mkdir()

        # Save the logo file if it exists
        logo_path = self.personality_package_path / "assets" / "logo.png"
        if hasattr(self, '_logo') and self._logo is not None:
            self._logo.save(logo_path)


    @property
    def logo(self):
        """
        Get the personality logo.

        Returns:
        PIL.Image.Image: The personality logo as a Pillow Image object.
        """
        if hasattr(self, '_logo'):
            return self._logo
        else:
            return None

    
    # Helper methods
    def detect_antiprompt(self, text:str) -> bool:
        """
        Detects if any of the antiprompts in self.anti_prompts are present in the given text.
        Used for the Hallucination suppression system

        Args:
            text (str): The text to check for antiprompts.

        Returns:
            bool: True if any antiprompt is found in the text (ignoring case), False otherwise.
        """
        for prompt in self.anti_prompts:
            if prompt.lower() in text.lower():
                return True
        return False

    def __str__(self):
        """
        Format the AIPersonality instance as a string.

        Returns:
        str: A string representation of the AIPersonality instance.
        """
        # Create a list of the personality attributes
        attributes = [f"{key}: {value}" for key, value in self.__dict__.items() if not key.startswith("_")]

        # Add the logo path if available
        logo_path = self.personality_package_path / "assets" / "logo.png"
        if logo_path.is_file():
            attributes.append(f"logo: {logo_path}")
        else:
            attributes.append(f"logo: This personality has no logo")
        # Format the attributes as a string
        attrs = ',\n  '.join(attributes)
        return f"AIPersonality:\n  {attrs}"
    

    # Helper functions
    @staticmethod
    def replace_keys(input_string, replacements):
        """
        Replaces all occurrences of keys in the input string with their corresponding
        values from the replacements dictionary.

        Args:
            input_string (str): The input string to replace keys in.
            replacements (dict): A dictionary of key-value pairs, where the key is the
                string to be replaced and the value is the replacement string.

        Returns:
            str: The input string with all occurrences of keys replaced by their
                corresponding values.
        """        
        pattern = r"\{\{(\w+)\}\}"
        # The pattern matches "{{key}}" and captures "key" in a group.
        # The "\w+" matches one or more word characters (letters, digits, or underscore).

        def replace(match):
            key = match.group(1)
            return replacements.get(key, match.group(0))

        output_string = re.sub(pattern, replace, input_string)
        return output_string
