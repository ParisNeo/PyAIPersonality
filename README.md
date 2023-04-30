# PyAIPersonality

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

if __name__ == "__main__":
    personality = AIPersonality("personalities_zoo/english/general/gpt4all_chat_bot")
    print("Done")
    print(f"{personality}")
```

You can use PyAIPersonality with pyllamacpp python bindings by first installing pyllamacpp:
```bash
pip install pyllamacpp
```
Then you can use this code to have an interactive communication with the AI through the console
```python
from pyaipersonality import AIPersonality
from pyllamacpp.model import Model
# You need to install pyllamacpp from pypi:

if __name__=="__main__":

    personality = AIPersonality("personalities_zoo/english/general/gpt4all_chat_bot")
    model = Model(ggml_model=r'C:\Users\aloui\Documents\ai\GPT4ALL-ui\GPT4All\models\llama_cpp/gpt4all-lora-quantized-ggml.bin',
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
            print(f"AI:", end='')
            for tok in model.generate(prompt):
                print(f"{tok}", end='', flush=True)
            print()
        except KeyboardInterrupt:
            break
    print("Done")
    print(f"{personality}")
```

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
