

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


class AIPersonality:
    version = pkg_resources.get_distribution('pyaipersonality').version
    name: str = "gpt4all"
    user_name: str = "user"
    language: str = "en_XX"
    category: str = "General"
    personality_description: str = "This personality is a helpful and Kind AI ready to help you solve your problems"
    personality_conditioning: str = "GPT4All is a smart and helpful Assistant built by Nomic-AI. It can discuss with humans and assist them."
    welcome_message: str = "Welcome! I am GPT4All A free and open assistant. What can I do for you today?"
    user_message_prefix: str = "### Human:"
    link_text: str = "\n"
    ai_message_prefix: str = "### Assistant:"
    dependencies: List[str] = []
    disclaimer: str = ""
    _logo: Optional[Image.Image] = None
    
    def __init__(self, personality_package_path: str|Path = None):
        """
        Initialize an AIPersonality instance.

        Parameters:
        personality_package_path (str or Path): The path to the folder containing the personality package.

        Raises:
        ValueError: If the provided path is not a folder or does not contain a config.yaml file.
        """
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

            # Verify that there is at least a configuration file
            config_file = self.personality_package_path / "config.yaml"
            if not config_file.is_file():
                raise ValueError("The provided folder does not contain a config.yaml file.")

            # Open and store the personality
            self.load_personality(config_file)


    def load_personality(self, file_path):
        """
        Load the personality data from a YAML file and set it as attributes of the class.

        Parameters:
        file_path (str or Path): The path to the YAML file containing the personality data.

        Returns:
        dict: A dictionary containing the personality data.
        """
        with open(file_path, 'r', encoding='utf-8') as stream:
            config = yaml.safe_load(stream)

        # Set the personality attributes
        for key, value in config.items():
            setattr(self, key, value)

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