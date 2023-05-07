

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
import importlib

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
        self._version = pkg_resources.get_distribution('pyaipersonality').version

        #General information
        self._author: str = "ParisNeo"
        self._name: str = "gpt4all"
        self._user_name: str = "user"
        self._language: str = "en_XX"
        self._category: str = "General"

        # Conditionning
        self._personality_description: str = "This personality is a helpful and Kind AI ready to help you solve your problems"
        self._personality_conditioning: str = "GPT4All is a smart and helpful Assistant built by Nomic-AI. It can discuss with humans and assist them.\nDate: {{date}}"
        self._welcome_message: str = "Welcome! I am GPT4All A free and open assistant. What can I do for you today?"
        self._user_message_prefix: str = "### Human:"
        self._link_text: str = "\n"
        self._ai_message_prefix: str = "### Assistant:"
        self._anti_prompts:list = ["###Human","###Assistant","### Human","### Assistant"]

        # Extra
        self._dependencies: List[str] = []

        # Disclaimer
        self._disclaimer: str = ""

        
        # Default model parameters
        self._model_temperature: float = 0.8 # higher: more creative, lower more deterministic
        self._model_n_predicts: int = 1024 # higher: generates many words, lower generates
        self._model_top_k: int = 50
        self._model_top_p: float = 0.95
        self._model_repeat_penalty: float = 1.3
        self._model_repeat_last_n: int = 40

        self._logo: Optional[Image.Image] = None
        self._processor = None



        if personality_package_path is None:
            self.config = {}
            self.assets_list = []
            self.personality_package_path = None
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


    def load_personality(self, package_path=None):
        """
        Load personality parameters from a YAML configuration file.

        Args:
            package_path (str or Path): The path to the package directory.

        Raises:
            ValueError: If the configuration file does not exist.
        """
        if package_path is None:
            package_path = self.personality_package_path
        else:
            package_path = Path(package_path)

        # Verify that there is at least a configuration file
        config_file = package_path / "config.yaml"
        if not config_file.exists():
            raise ValueError(f"The provided folder {package_path} does not exist.")

        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        # Load parameters from the configuration file
        self._version = config.get("version", self._version)
        self._author = config.get("author", self._author)
        self._name = config.get("name", self._name)
        self._user_name = config.get("user_name", self._user_name)
        self._language = config.get("language", self._language)
        self._category = config.get("category", self._category)
        self._personality_description = config.get("personality_description", self._personality_description)
        self._personality_conditioning = config.get("personality_conditioning", self._personality_conditioning)
        self._welcome_message = config.get("welcome_message", self._welcome_message)
        self._user_message_prefix = config.get("user_message_prefix", self._user_message_prefix)
        self._link_text = config.get("link_text", self._link_text)
        self._ai_message_prefix = config.get("ai_message_prefix", self._ai_message_prefix)
        self._anti_prompts = config.get("anti_prompts", self._anti_prompts)
        self._dependencies = config.get("dependencies", self._dependencies)
        self._disclaimer = config.get("disclaimer", self._disclaimer)
        self._model_temperature = config.get("model_temperature", self._model_temperature)
        self._model_n_predicts = config.get("model_n_predicts", self._model_n_predicts)
        self._model_top_k = config.get("model_top_k", self._model_top_k)
        self._model_top_p = config.get("model_top_p", self._model_top_p)
        self._model_repeat_penalty = config.get("model_repeat_penalty", self._model_repeat_penalty)
        self._model_repeat_last_n = config.get("model_repeat_last_n", self._model_repeat_last_n)

        #set package path
        self.personality_package_path = package_path

        # Check for a logo file
        logo_path = self.personality_package_path / "assets" / "logo.png"
        if logo_path.is_file():
            self._logo = Image.open(logo_path)

        # Get the assets folder path
        assets_path = self.personality_package_path / "assets"
        # Get the scripts folder path
        scripts_path = self.personality_package_path / "scripts"
        
        # If not exist recreate
        assets_path.mkdir(parents=True, exist_ok=True)

        # If not exist recreate
        scripts_path.mkdir(parents=True, exist_ok=True)

        # Search for any processor code
        file_name = "processor.py"
        file_path = scripts_path / file_name

        if file_path.exists():
            # If the file exists, import the Processor class
            try:
                spec = importlib.util.spec_from_file_location("processor_module", file_path)
                processor_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(processor_module)

                # Set the _processor parameter to an instance of the Processor class
                self._processor = processor_module.Processor()
            except ImportError:
                # Error occurred while importing the file or class
                self._processor = None
        else:
            # If the file doesn't exist, set _processor to None
            self._processor = None

        if file_path.exists():
            module_name = file_name[:-3]  # Remove the ".py" extension
            module_spec = importlib.util.spec_from_file_location(module_name, str(file_path))
            module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(module)
            if hasattr(module, "Processor"):
                self._processor = module.Processor()
            else:
                self._processor = None
        else:
            self._processor = None
        # Get a list of all files in the assets folder
        contents = [str(file) for file in assets_path.iterdir() if file.is_file()]

        self._assets_list = contents
        return config

    def save_personality(self, package_path=None):
        """
        Save the personality parameters to a YAML configuration file.

        Args:
            package_path (str or Path): The path to the package directory.
        """
        if package_path is None:
            package_path = self.personality_package_path
        else:
            package_path = Path(package_path)

        # Building output path
        config_file = package_path / "config.yaml"
        assets_folder = package_path / "assets"

        # Create assets folder if it doesn't exist
        if not assets_folder.exists():
            assets_folder.mkdir(exist_ok=True, parents=True)

        # Create the configuration dictionary
        config = {
            "author": self._author,
            "version": self._version,
            "name": self._name,
            "user_name": self._user_name,
            "language": self._language,
            "category": self._category,
            "personality_description": self._personality_description,
            "personality_conditioning": self._personality_conditioning,
            "welcome_message": self._welcome_message,
            "user_message_prefix": self._user_message_prefix,
            "link_text": self._link_text,
            "ai_message_prefix": self._ai_message_prefix,
            "anti_prompts": self._anti_prompts,
            "dependencies": self._dependencies,
            "disclaimer": self._disclaimer,
            "model_temperature": self._model_temperature,
            "model_n_predicts": self._model_n_predicts,
            "model_top_k": self._model_top_k,
            "model_top_p": self._model_top_p,
            "model_repeat_penalty": self._model_repeat_penalty,
            "model_repeat_last_n": self._model_repeat_last_n
        }

        # Save the configuration to the YAML file
        with open(config_file, "w") as f:
            yaml.dump(config, f)

    def as_dict(self):
        """
        Convert the personality parameters to a dictionary.

        Returns:
            dict: The personality parameters as a dictionary.
        """
        return {
            "author": self._author,
            "version": self._version,
            "name": self._name,
            "user_name": self._user_name,
            "language": self._language,
            "category": self._category,
            "personality_description": self._personality_description,
            "personality_conditioning": self._personality_conditioning,
            "welcome_message": self._welcome_message,
            "user_message_prefix": self._user_message_prefix,
            "link_text": self._link_text,
            "ai_message_prefix": self._ai_message_prefix,
            "anti_prompts": self._anti_prompts,
            "dependencies": self._dependencies,
            "disclaimer": self._disclaimer,
            "model_temperature": self._model_temperature,
            "model_n_predicts": self._model_n_predicts,
            "model_top_k": self._model_top_k,
            "model_top_p": self._model_top_p,
            "model_repeat_penalty": self._model_repeat_penalty,
            "model_repeat_last_n": self._model_repeat_last_n,
            "assets_list":self._assets_list
        }

    # ========================================== Properties ===========================================
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
    @property
    def version(self):
        """Get the version of the package."""
        return self._version

    @version.setter
    def version(self, value):
        """Set the version of the package."""
        self._version = value

    @property
    def author(self):
        """Get the author of the package."""
        return self._author

    @author.setter
    def author(self, value):
        """Set the author of the package."""
        self._author = value

    @property
    def name(self) -> str:
        """Get the name."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Set the name."""
        self._name = value

    @property
    def user_name(self) -> str:
        """Get the user name."""
        return self._user_name

    @user_name.setter
    def user_name(self, value: str):
        """Set the user name."""
        self._user_name = value

    @property
    def language(self) -> str:
        """Get the language."""
        return self._language

    @language.setter
    def language(self, value: str):
        """Set the language."""
        self._language = value

    @property
    def category(self) -> str:
        """Get the category."""
        return self._category

    @category.setter
    def category(self, value: str):
        """Set the category."""
        self._category = value

    @property
    def personality_description(self) -> str:
        """
        Getter for the personality description.

        Returns:
            str: The personality description of the AI assistant.
        """
        return self._personality_description

    @personality_description.setter
    def personality_description(self, description: str):
        """
        Setter for the personality description.

        Args:
            description (str): The new personality description for the AI assistant.
        """
        self._personality_description = description

    @property
    def personality_conditioning(self) -> str:
        """
        Getter for the personality conditioning.

        Returns:
            str: The personality conditioning of the AI assistant.
        """
        return self.replace_keys(self._personality_conditioning, self.Conditionning_commands)

    @personality_conditioning.setter
    def personality_conditioning(self, conditioning: str):
        """
        Setter for the personality conditioning.

        Args:
            conditioning (str): The new personality conditioning for the AI assistant.
        """
        self._personality_conditioning = conditioning

    @property
    def welcome_message(self) -> str:
        """
        Getter for the welcome message.

        Returns:
            str: The welcome message of the AI assistant.
        """
        return self.replace_keys(self._welcome_message, self.Conditionning_commands)

    @welcome_message.setter
    def welcome_message(self, message: str):
        """
        Setter for the welcome message.

        Args:
            message (str): The new welcome message for the AI assistant.
        """
        self._welcome_message = message

    @property
    def user_message_prefix(self) -> str:
        """
        Getter for the user message prefix.

        Returns:
            str: The user message prefix of the AI assistant.
        """
        return self._user_message_prefix

    @user_message_prefix.setter
    def user_message_prefix(self, prefix: str):
        """
        Setter for the user message prefix.

        Args:
            prefix (str): The new user message prefix for the AI assistant.
        """
        self._user_message_prefix = prefix

    @property
    def link_text(self) -> str:
        """
        Getter for the link text.

        Returns:
            str: The link text of the AI assistant.
        """
        return self._link_text

    @link_text.setter
    def link_text(self, text: str):
        """
        Setter for the link text.

        Args:
            text (str): The new link text for the AI assistant.
        """
        self._link_text = text    
    @property
    def ai_message_prefix(self):
        """
        Get the AI message prefix.

        Returns:
            str: The AI message prefix.
        """
        return self._ai_message_prefix

    @ai_message_prefix.setter
    def ai_message_prefix(self, prefix):
        """
        Set the AI message prefix.

        Args:
            prefix (str): The AI message prefix to set.
        """
        self._ai_message_prefix = prefix

    @property
    def anti_prompts(self):
        """
        Get the anti-prompts list.

        Returns:
            list: The anti-prompts list.
        """
        return self._anti_prompts

    @anti_prompts.setter
    def anti_prompts(self, prompts):
        """
        Set the anti-prompts list.

        Args:
            prompts (list): The anti-prompts list to set.
        """
        self._anti_prompts = prompts


    @property
    def dependencies(self) -> List[str]:
        """Getter method for the dependencies attribute.

        Returns:
            List[str]: The list of dependencies.
        """
        return self._dependencies

    @dependencies.setter
    def dependencies(self, dependencies: List[str]):
        """Setter method for the dependencies attribute.

        Args:
            dependencies (List[str]): The list of dependencies.
        """
        self._dependencies = dependencies

    @property
    def disclaimer(self) -> str:
        """Getter method for the disclaimer attribute.

        Returns:
            str: The disclaimer text.
        """
        return self._disclaimer

    @disclaimer.setter
    def disclaimer(self, disclaimer: str):
        """Setter method for the disclaimer attribute.

        Args:
            disclaimer (str): The disclaimer text.
        """
        self._disclaimer = disclaimer

    @property
    def model_temperature(self) -> float:
        """Get the model's temperature."""
        return self._model_temperature

    @model_temperature.setter
    def model_temperature(self, value: float):
        """Set the model's temperature.

        Args:
            value (float): The new temperature value.
        """
        self._model_temperature = value

    @property
    def model_n_predicts(self) -> int:
        """Get the number of predictions the model generates."""
        return self._model_n_predicts

    @model_n_predicts.setter
    def model_n_predicts(self, value: int):
        """Set the number of predictions the model generates.

        Args:
            value (int): The new number of predictions value.
        """
        self._model_n_predicts = value

    @property
    def model_top_k(self) -> int:
        """Get the model's top-k value."""
        return self._model_top_k

    @model_top_k.setter
    def model_top_k(self, value: int):
        """Set the model's top-k value.

        Args:
            value (int): The new top-k value.
        """
        self._model_top_k = value

    @property
    def model_top_p(self) -> float:
        """Get the model's top-p value."""
        return self._model_top_p

    @model_top_p.setter
    def model_top_p(self, value: float):
        """Set the model's top-p value.

        Args:
            value (float): The new top-p value.
        """
        self._model_top_p = value

    @property
    def model_repeat_penalty(self) -> float:
        """Get the model's repeat penalty value."""
        return self._model_repeat_penalty

    @model_repeat_penalty.setter
    def model_repeat_penalty(self, value: float):
        """Set the model's repeat penalty value.

        Args:
            value (float): The new repeat penalty value.
        """
        self._model_repeat_penalty = value

    @property
    def model_repeat_last_n(self) -> int:
        """Get the number of words to consider for repeat penalty."""
        return self._model_repeat_last_n

    @model_repeat_last_n.setter
    def model_repeat_last_n(self, value: int):
        """Set the number of words to consider for repeat penalty.

        Args:
            value (int): The new number of words value.
        """
        self._model_repeat_last_n = value


    @property
    def assets_list(self) -> list:
        """Get the number of words to consider for repeat penalty."""
        return self._assets_list

    @assets_list.setter
    def assets_list(self, value: list):
        """Set the number of words to consider for repeat penalty.

        Args:
            value (int): The new number of words value.
        """
        self._assets_list = value

    @property
    def processor(self) -> list:
        """Get the number of words to consider for repeat penalty."""
        return self._processor

    @processor.setter
    def processor(self, value: list):
        """Set the number of words to consider for repeat penalty.

        Args:
            value (int): The new number of words value.
        """
        self._processor = value




    # ========================================== Helper methods ==========================================
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
        Return a string representation of the class with all its parameters.
        """
        params = [
            f"Version: {self._version}",
            f"Name: {self._name}",
            f"User Name: {self._user_name}",
            f"Language: {self._language}",
            f"Category: {self._category}",
            f"Personality Description: {self._personality_description}",
            f"Personality Conditioning: {self._personality_conditioning}",
            f"Welcome Message: {self._welcome_message}",
            f"User Message Prefix: {self._user_message_prefix}",
            f"Link Text: {self._link_text}",
            f"AI Message Prefix: {self._ai_message_prefix}",
            f"Anti Prompts: {self._anti_prompts}",
            f"Dependencies: {self._dependencies}",
            f"Disclaimer: {self._disclaimer}",
            f"Model Temperature: {self._model_temperature}",
            f"Model N Predicts: {self._model_n_predicts}",
            f"Model Top K: {self._model_top_k}",
            f"Model Top P: {self._model_top_p}",
            f"Model Repeat Penalty: {self._model_repeat_penalty}",
            f"Model Repeat Last N: {self._model_repeat_last_n}",
        ]

        return "\n".join(params)



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


class PAPScript:
    """
    Template class for implementing personality processor classes in the PAPScript framework.

    This class provides a basic structure and placeholder methods for processing model inputs and outputs.
    Personality-specific processor classes should inherit from this class and override the necessary methods.

    Methods:
        process_model_input(text): Process the model input.
        process_model_output(text): Process the model output.
    """
    def __init__(self) -> None:
        pass

    def process_model_input(self, text):
        """
        Process the model input.

        This method should be overridden in the personality-specific processor class to define
        the desired behavior for processing the model input.

        Args:
            text (str): The model input text.

        Returns:
            Any: The processed model input.
        """
        return None

    def process_model_output(self, text):
        """
        Process the model output.

        This method should be overridden in the personality-specific processor class to define
        the desired behavior for processing the model output.

        Args:
            text (str): The model output text.

        Returns:
            Any: The processed model output.
        """
        return None

