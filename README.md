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
