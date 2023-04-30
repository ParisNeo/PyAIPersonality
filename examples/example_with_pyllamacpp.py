from pyaipersonality import AIPersonality
from pyllamacpp.model import Model
# You need to install pyllamacpp from pypi:
# pip install pyllamacpp

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