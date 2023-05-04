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
    full_context = personality.personality_conditioning+personality.link_text+personality.ai_message_prefix+personality.welcome_message if personality.welcome_message!="" else personality.personality_conditioning
    model = Model(model_path=f'models/{url.split("/")[-1]}',
                  prompt_context=full_context,
                  prompt_prefix=personality.link_text + personality.user_message_prefix + personality.link_text,
                  prompt_suffix=personality.link_text + personality.ai_message_prefix + personality.link_text
                  )
    # If there is a disclaimer, show it
    if personality.disclaimer!="":
        print()
        print("Disclaimer")
        print(personality.disclaimer)
        print()

    # Show conditionning
    print(full_context)
    
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
