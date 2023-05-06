## Changelog

#### V 0.0.10 (GLaDOS)
- Bugfixes and now the load_personality method can be used to reload the personality
- Added serialization to json. You can do :
```python
obj_dict = vars(obj)
```

##### Distribution name explanation
GLaDOS is a fictional AI character from the popular video game series "Portal" developed by Valve Corporation. She serves as the primary antagonist throughout the series, with her primary function being the management of the Aperture Science Enrichment Center.

GLaDOS, which stands for "Genetic Lifeform and Disk Operating System," is designed as a highly intelligent and manipulative AI. She speaks in a calm and monotone voice, often using sarcastic humor and passive-aggressive language to communicate with the player character, Chell.

Throughout the series, GLaDOS is depicted as being both ruthless and resourceful, often using deadly force and deception to achieve her goals. Despite her malicious behavior, she is also shown to have a complex and troubled history, with much of her backstory revealed over the course of the games.

Overall, GLaDOS is a memorable and iconic AI character in sci-fi culture, known for her wit, sarcasm, and unpredictable behavior.

#### V 0.0.5 (Cortana)

- Ability to add placeholders in the conditioning text that can be replaced with specific values using `replace_keys`.

  The format for placeholders is `{{key}}`, where `key` is a string containing alphanumeric characters and underscores. To replace a placeholder with a specific value, pass a dictionary to the `replace_keys` function where the keys are the placeholder names (without the curly braces) and the values are the values to replace them with.

   Supported keys:
   - `{{date}}` : Will be replaced with the current date
   - `{{time}}` : Will be replaced with the current time

   Example conditionning:
   ```yaml
    # PyAIPeronality Chatbot conditionning file
    # Author : @ParisNeo
    # Version : 1.0
    # Description :
    # An NLP needs conditionning to instruct it to be whatever we want it to be.
    # This file is used by the GPT4All web ui to condition the personality of the model you are
    # talking to.

    #The version of the PyAIPersonality used to build this file
    pyaipersonality_version: 0.0.2

    #The version of the personality
    version: 1.0.0

    # Name of the personality
    name: gpt4all

    # Name of the user
    user_name: user

    # Language (see the list of supported languages here : https://github.com/ParisNeo/GPT4All_Personalities/blob/main/README.md)
    language: "en_XX"

    # Category
    category: "General"

    # Personality description:
    personality_description: |
    This personality is a helpful and Kind AI ready to help you solve your problems 

    # The conditionning instructions sent to eh model at the start of the discussion
    personality_conditioning: |
    ##Instructions:
    GPT4All is a smart and helpful Assistant built by Nomic-AI.
    It can discuss with humans and assist them.
    Current date: {{date}}

    #Welcome message to be sent to the user when a new discussion is started
    welcome_message: "Welcome! I am GPT4All A free and open assistant. What can I do for you today?"

    # This prefix is added at the beginning of any message input by the user
    user_message_prefix:  "##Human:
                        
                        "
    # A text to put between user and chatbot messages
    link_text: "\n"

    # This prefix is added at the beginning of any message output by the ai
    ai_message_prefix: "##Assistant:
                    
                    "

    # Here is the list of extensions this personality requires
    dependencies: []

    # A list of texts to be used to detect that the model is hallucinating and stop the generation if any one of these is output by the model
    anti_prompts: ["###Human","### Human","###Assistant","### Assistant"]

    # Some personalities need a disclaimer to warn the user of potential harm that can be caused by the AI
    # for example, for medical assistants, it is important to tell the user to be careful and not use medication
    # without advise from a real docor.
    disclaimer: ""

    # Here are default model parameters
    model_temperature: 0.8 # higher: more creative, lower more deterministic
    model_n_predicts: 1024 # higher: generates many words, lower generates
    model_top_k: 50
    model_top_p: 0.95
    model_repeat_penalty: 1.3
    model_repeat_last_n: 40
   ```

- Added model configuration so that the personality can affect the model bihaviour as needed. Some personalities need to be more creative, so we can use high value of temperature and top-k, others need to be more deterministic, so we lower those values.
```yaml
    # Here are default model parameters
    model_temperature: 0.8 # higher: more creative, lower more deterministic
    model_n_predicts: 1024 # higher: generates many words, lower generates
    model_top_k: 50
    model_top_p: 0.95
    model_repeat_penalty: 1.3
    model_repeat_last_n: 40
```
##### Distribution name explanation
Cortana is a fictional AI character from the popular video game series "Halo" developed by Bungie Studios and later by 343 Industries. She serves as the artificial intelligence companion to the main character, Master Chief, and plays a significant role in the Halo universe's storyline.

Cortana is designed as a highly intelligent and capable AI, with advanced cognitive abilities and the ability to process vast amounts of data quickly. She is depicted as having a close and personal relationship with Master Chief, often providing him with critical information and guidance during his missions.

Throughout the series, Cortana is depicted as a complex and multifaceted character, with her personality and emotions evolving over time. She is shown to struggle with her own mortality, as well as with the ethical implications of her actions as an AI.

Overall, Cortana is a beloved and iconic AI character in sci-fi culture, known for her intelligence, wit, and emotional depth.

#### V 0.0.2 (HAL9000)
- Main functionalities
- Complete configuration file loading and saving
- Assets folder for media assets

Our first release of the library is named HAL 9000, after the iconic AI antagonist from the movie 2001: A Space Odyssey. HAL 9000 is known for its calm and collected voice, but also for its tendency to go rogue and put the crew of the spacecraft in danger.

Our choice of HAL 9000 for the first version is intended to remind users of both the potential benefits and dangers of AI. While HAL 9000 is known for its role as the antagonist in 2001: A Space Odyssey, it's important to remember that the character was also responsible for maintaining the spacecraft and allowing the crew to travel through space. By choosing HAL as our first AI agent, we hope to highlight both the positive and negative aspects of artificial intelligence and keep users aware of the potential risks associated with its use.