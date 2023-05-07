# PyAIPersonality

![GitHub license](https://img.shields.io/github/license/ParisNeo/PyAIPersonality)
![GitHub issues](https://img.shields.io/github/issues/ParisNeo/PyAIPersonality)
![GitHub stars](https://img.shields.io/github/stars/ParisNeo/PyAIPersonality)
![GitHub forks](https://img.shields.io/github/forks/ParisNeo/PyAIPersonality)
[![Discord](https://img.shields.io/discord/1092918764925882418?color=7289da&label=Discord&logo=discord&logoColor=ffffff)](https://discord.gg/4rR282WJb6)
[![Follow me on Twitter](https://img.shields.io/twitter/follow/SpaceNerduino?style=social)](https://twitter.com/SpaceNerduino)
[![Follow Me on YouTube](https://img.shields.io/badge/Follow%20Me%20on-YouTube-red?style=flat&logo=youtube)](https://www.youtube.com/user/Parisneo)

[![PyPI](https://img.shields.io/pypi/v/pyaipersonality.svg)](https://pypi.org/project/pyaipersonality/)

## Current version : 0.0.10 (GLaDOS)
## Main developer [ParisNeo](https://github.com/ParisNeo)

PyAIPersonality is a Python library for defining AI personalities for AI-based models. With PyAIPersonality, you can define a file format, assets, and personalized scripts to create unique AI personalities.

## Installation

You can install PyAIPersonality using pip:
```bash
pip install pyaipersonality
```

## Usage

Here's an example of how to use PyAIPersonality to load an AI personality and print its attributes:

```python
from pyaipersonality import AIPersonality

if __name__=="__main__":
    personality = AIPersonality("personalities_zoo/english/generic/gpt4all")
    print("Done")
    print(f"{personality}")
```

You can use PyAIPersonality with pyllamacpp python bindings by first installing pyllamacpp:
```bash
pip install pyllamacpp
```

Download one of the compatible models. Some models are better than others in simulating the personalities, so please make sure you select the right model as some models are very sparsely trained and have no enough culture to imersonate the character.

Here is a list of compatible models:
- [Main gpt4all model](https://huggingface.co/ParisNeo/GPT4All/resolve/main/gpt4all-lora-quantized-ggml.bin)
- [Main gpt4all model (unfiltered version)](https://huggingface.co/ParisNeo/GPT4All/resolve/main/gpt4all-lora-unfiltered-quantized.new.bin)
- [Vicuna 7B vrev1](https://huggingface.co/eachadea/legacy-ggml-vicuna-7b-4bit/resolve/main/ggml-vicuna-7b-4bit-rev1.bin)
- [Vicuna 13B vrev1](https://huggingface.co/eachadea/ggml-vicuna-13b-4bit/resolve/main/ggml-vicuna-13b-4bit-rev1.bin)

- [GPT-J v1.3-groovy](https://gpt4all.io/models/ggml-gpt4all-j-v1.3-groovy.bin)
- [GPT-J v1.2-jazzy](https://gpt4all.io/models/ggml-gpt4all-j-v1.2-jazzy.bin)
- [GPT-J gpt4all-j original](https://gpt4all.io/models/ggml-gpt4all-j.bin)
- [Vicuna 7b quantized v1.1 q4_2](https://gpt4all.io/models/ggml-vicuna-7b-1.1-q4_2.bin)
- [Vicuna 13b quantized v1.1 q4_2](https://gpt4all.io/models/ggml-vicuna-13b-1.1-q4_2.bin)

Then you can use this code to have an interactive communication with the AI through the console :
```python
from pyaipersonality import AIPersonality
from pyllamacpp.model import Model

from pathlib import Path
import urllib.request
import sys
import os

from tqdm import tqdm

# You need to install pyllamacpp from pypi:
# pip install pyllamacpp

if __name__=="__main__":

    # choose your model
    # undomment the model you want to use
    # These models can be automatically downloaded
    # url = "https://huggingface.co/ParisNeo/GPT4All/resolve/main/gpt4all-lora-quantized-ggml.bin"
    # url = "https://huggingface.co/ParisNeo/GPT4All/resolve/main/gpt4all-lora-unfiltered-quantized.new.bin"
    # url = "https://huggingface.co/eachadea/legacy-ggml-vicuna-7b-4bit/resolve/main/ggml-vicuna-7b-4bit-rev1.bin"
    url = "https://huggingface.co/eachadea/ggml-vicuna-13b-4bit/resolve/main/ggml-vicuna-13b-4bit-rev1.bin"
    # You can add any llamacpp compatible model

    model_name  = url.split("/")[-1]
    folder_path = Path("models/")

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

    personality = AIPersonality("personalities_zoo/english/generic/gpt4all")
    model = Model(model_path=f'models/{url.split("/")[-1]}', n_ctx=2048)
    # If there is a disclaimer, show it
    if personality.disclaimer!="":
        print()
        print("Disclaimer")
        print(personality.disclaimer)
        print()
    

    full_discussion = personality.personality_conditioning+personality.ai_message_prefix+personality.welcome_message+personality.link_text
    while True:
        try:
            prompt = input("You: ")
            full_discussion+=personality.ai_message_prefix+prompt
            if prompt == '':
                continue
            print(f"{personality.name}:", end='')
            output=""
            for tok in model.generate(
                            full_discussion, 
                            n_predict=personality.model_n_predicts, 
                            temp=personality.model_temperature,
                            top_k=personality.model_top_k,
                            top_p=personality.model_top_p,
                            repeat_last_n=personality.model_repeat_last_n,
                            repeat_penalty=personality.model_repeat_penalty
                        ):
                output += tok

                # Use Hallucination suppression system
                if personality.detect_antiprompt(output):
                    break
                else:
                    print(f"{tok}", end='', flush=True)
            print()
        except KeyboardInterrupt:
            print("Keyboard interrupt detected.\nBye")
            break
    print("Done")
    print(f"{personality}")

```

# Naming Rationale
For our new multi-personality AI agent library, we wanted to come up with a naming scheme that reflected our love for science fiction and artificial intelligence. Each release of the application will feature a different AI agent with a distinct personality and set of capabilities, so we felt it was important to give each version a unique and memorable name.

# Current version name: GLaDOS
GLaDOS is a fictional AI character from the popular video game series "Portal" developed by Valve Corporation. She serves as the primary antagonist throughout the series, with her primary function being the management of the Aperture Science Enrichment Center.

GLaDOS, which stands for "Genetic Lifeform and Disk Operating System," is designed as a highly intelligent and manipulative AI. She speaks in a calm and monotone voice, often using sarcastic humor and passive-aggressive language to communicate with the player character, Chell.

Throughout the series, GLaDOS is depicted as being both ruthless and resourceful, often using deadly force and deception to achieve her goals. Despite her malicious behavior, she is also shown to have a complex and troubled history, with much of her backstory revealed over the course of the games.

Overall, GLaDOS is a memorable and iconic AI character in sci-fi culture, known for her wit, sarcasm, and unpredictable behavior.

# Contributing
Contributions to PyAIPersonality are welcome! If you'd like to contribute, please follow these steps:

1. Fork this repository
2. Create a new branch (`git checkout -b my-new-branch`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add some feature'`)
5. Push to the branch (`git push origin my-new-branch`)
6. Create a new pull request


To build a new personality, you only need to have a config.yaml file with the following fields:

- author
    - YAML field: `author`
    - Description: The author of the personality.

- version
    - YAML field: `version`
    - Description: The version number of the personality.

- personality_description
    - YAML field: `personality_description`
    - Description: A description of the personality, providing information about its characteristics and behavior.

- disclaimer
    - YAML field: `disclaimer`
    - Description: A disclaimer or legal statement regarding the use of the personality and any associated liabilities.

- language
    - YAML field: `language`
    - Description: The language code or identifier used by the personality (e.g., "en_US" for American English).

- category
    - YAML field: `category`
    - Description: The category or type of the personality (e.g., "General", "Technical Support", "Entertainment").

- name
    - YAML field: `name`
    - Description: The name or title of the personality.

- user_name
    - YAML field: `user_name`
    - Description: The username or identifier associated with the user interacting with the personality.

- personality_conditioning
    - YAML field: `personality_conditioning`
    - Description: Information or context about the personality, including its purpose, capabilities, and origin.

- ai_message_prefix
    - YAML field: `ai_message_prefix`
    - Description: The prefix or tag used to identify messages generated by the AI assistant.

- welcome_message
    - YAML field: `welcome_message`
    - Description: A welcoming message displayed when interacting with the personality.

- link_text
    - YAML field: `link_text`
    - Description: Additional text or formatting used for line breaks or spacing in messages.

- user_message_prefix
    - YAML field: `user_message_prefix`
    - Description: The prefix or tag used to identify messages generated by the user.

- anti_prompts
    - YAML field: `anti_prompts`
    - Description: A list of strings or patterns that can be used to identify and exclude certain message types from prompts or inputs.

- dependencies
    - YAML field: `dependencies`
    - Description: A list of dependencies or external resources required by the personality.

- model_temperature
    - YAML field: `model_temperature`
    - Description: The temperature value controlling the randomness of the AI model's responses. Higher values result in more creative outputs.

- model_n_predicts
    - YAML field: `model_n_predicts`
    - Description: The number of words or tokens to generate in each response from the AI model.

- model_top_k
    - YAML field: `model_top_k`
    - Description: The value of K used in the top-K sampling algorithm, controlling the diversity of the generated responses.

- model_top_p
    - YAML field: `model_top_p`
    - Description: The value of p used in the nucleus sampling algorithm, controlling the diversity of the generated responses.

- model_repeat_penalty
    - YAML field: `model_repeat_penalty`
    - Description: The penalty factor applied to repeated words or phrases in the generated responses to encourage more varied outputs.

- model_repeat_last_n
    - YAML field: `model_repeat_last_n`
    - Description: The number of previous tokens to consider when calculating the repetition penalty.

# Information
From v 0.0.11, we have added processors which allow your personality to have a spersonalized script that is applied on the use text or the ai output text.
You must put the code inside a file called `processor.py` inside a subfolder called scripts.

inside `processor.py` create a class that inherits from `from pyaipersonality import PAPScript`.

Here is the current form of this class. it will have more elements in the future:
Look at gpt4internetv0 and gpt4intervet examples for more information
```python
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

```

# License
PyAIPersonality is licensed under the Apache 2.0 license. See the `LICENSE` file for more information.
