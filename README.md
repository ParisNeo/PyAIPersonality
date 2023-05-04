# PyAIPersonality

## Current version : 0.0.4 (HAL9000)
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

    personality = AIPersonality("personalities_zoo/english/general/gpt4all_chat_bot")
    model = Model(ggml_model=r'<Your path to the ggml compatibe model>',
                  prompt_context=personality.personality_conditioning+
                  personality.link_text+
                  personality.ai_message_prefix+
                  personality.welcome_message,
                  prompt_prefix=personality.link_text + personality.user_message_prefix + personality.link_text,
                  prompt_suffix=personality.link_text + personality.ai_message_prefix + personality.link_text,
                  anti_prompts=[personality.user_message_prefix, personality.ai_message_prefix])
    print(personality.welcome_message)
    while True:
        try:
            prompt = input("You: ")
            if prompt == '':
                continue
            print(f"{personality.name}:", end='')
            output=""
            for tok in model.generate(
                            prompt, 
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

# Current version name: HAL 9000
Our first release of the library is named HAL 9000, after the iconic AI antagonist from the movie 2001: A Space Odyssey. HAL 9000 is known for its calm and collected voice, but also for its tendency to go rogue and put the crew of the spacecraft in danger.

Our choice of HAL 9000 for the first version is intended to remind users of both the potential benefits and dangers of AI. While HAL 9000 is known for its role as the antagonist in 2001: A Space Odyssey, it's important to remember that the character was also responsible for maintaining the spacecraft and allowing the crew to travel through space. By choosing HAL as our first AI agent, we hope to highlight both the positive and negative aspects of artificial intelligence and keep users aware of the potential risks associated with its use.

# Contributing
Contributions to PyAIPersonality are welcome! If you'd like to contribute, please follow these steps:

1. Fork this repository
2. Create a new branch (`git checkout -b my-new-branch`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add some feature'`)
5. Push to the branch (`git push origin my-new-branch`)
6. Create a new pull request


# License
PyAIPersonality is licensed under the Apache 2.0 license. See the `LICENSE` file for more information.
