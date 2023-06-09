from pyaipersonality import AIPersonality
from pyaipersonality.binding import BindingConfig
import bindings_zoo.llama_cpp_official as llm_binding
import bindings_zoo.llama_cpp_official.install as llm_binding_installer

import os

from tqdm import tqdm
import random

# Install binding if not installed yet 


def build_model(cfg: BindingConfig):
    llm_binding_installer.Install()
    model = llm_binding.LLAMACPP(cfg)
    return model

# You need to install llama-cpp-python from pypi:
# pip install llama-cpp-python

if __name__=="__main__":

    # choose your model
    # undomment the model you want to use
    # These models can be automatically downloaded
    url = "https://huggingface.co/CRD716/ggml-vicuna-1.1-quantized/resolve/main/legacy-ggml-vicuna-7B-1.1-q4_0.bin"
    personality_path = "personalities_zoo/english/generic/gpt4all"

    model_name  = url.split("/")[-1]

    cfg = BindingConfig()
    cfg.binding = llm_binding.binding_folder_name
    cfg.model = model_name
    if not cfg.check_model_existance():
        cfg.download_model(url)

    model = build_model(cfg)
    personality = AIPersonality(personality_path, model)

    # If there is a disclaimer, show it
    if personality.disclaimer!="":
        print()
        print("Disclaimer")
        print(personality.disclaimer)
        print()
    
    if personality.welcome_message:
        print(personality.welcome_message)

    full_discussion = personality.personality_conditioning+personality.ai_message_prefix+personality.welcome_message+personality.link_text
    while True:
        try:
            prompt = input("You: ")
            if prompt == '':
                continue

            if personality.processor is not None:
                preprocessed_prompt = personality.processor.process_model_input(prompt)

                full_discussion+=personality.user_message_prefix+preprocessed_prompt+personality.link_text+personality.ai_message_prefix
            else:
                full_discussion+=personality.user_message_prefix+prompt+personality.link_text+personality.ai_message_prefix

            print(f"{personality.name}:", end='')
            def callback(text):
                print(text,end="",flush=True)
                return True

            output = model.generate(full_discussion, callback=callback)
            print("\n")

            if personality.processor is not None:
                if personality.processor.process_model_output is not None:
                    output = personality.processor.process_model_output(output)

        except KeyboardInterrupt:
            print("Keyboard interrupt detected.\nBye")
            break
    print("Done")
    print(f"{personality}")
