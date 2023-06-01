import streamlit as st
from pyaipersonality import AIPersonality
from pyaipersonality.binding import BindingConfig
from pathlib import Path
import argparse
import importlib

full_discussion_blocks=[]
elements={}
answer=[""]


def build_model(bindings_path:Path, cfg: BindingConfig):
    binding_path = Path(bindings_path)/cfg["binding"]
    # first find out if there is a requirements.txt file
    install_file_name="install.py"
    install_script_path = binding_path / install_file_name        
    if install_script_path.exists():
        module_name = install_file_name[:-3]  # Remove the ".py" extension
        module_spec = importlib.util.spec_from_file_location(module_name, str(install_script_path))
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        if hasattr(module, "Install"):
            module.Install(None)
    # define the full absolute path to the module
    absolute_path = binding_path.resolve()            
    # infer the module name from the file path
    module_name = binding_path.stem    
    # use importlib to load the module from the file path
    loader = importlib.machinery.SourceFileLoader(module_name, str(absolute_path/"__init__.py"))
    binding_module = loader.load_module()
    binding_class = getattr(binding_module, binding_module.binding_name)

    model = binding_class(cfg)
    return model

# Define a function to generate a chatbot response
def generate_response(model, personality, prompt):
    answer[0]=''
    def callback(text):
        answer[0]  = answer[0] + text
        elements["output"].write(answer)
        # print(text,end="",flush=True)
        return True
    
    if personality.processor is not None:
        preprocessed_prompt = personality.processor.process_model_input(prompt)
    else:
        preprocessed_prompt = prompt
        
    full_discussion_blocks.append(personality.user_message_prefix)
    full_discussion_blocks.append(preprocessed_prompt)
    full_discussion_blocks.append(personality.link_text)
    full_discussion_blocks.append(personality.ai_message_prefix)
        
    full_discussion = ''.join(full_discussion_blocks)
    
    generated_text = model.generate(full_discussion, new_text_callback=callback)
    full_discussion_blocks.append(generated_text)
    
    return generated_text

# Create the Streamlit UI
def main():
    parser = argparse.ArgumentParser()
    # Place your model in models/<the binding name> 
    # streamlit run examples/streamlit_example/streamlit_example.py -- -m Manticore-13B.ggmlv3.q4_0.bin
    
    parser.add_argument('--config', '-cfg', default="configs/config.yaml", help='Path to the configuration file')
    parser.add_argument('--bindings_path', '-bp', default="bindings_zoo", help='Binding path')
    parser.add_argument('--binding', '-b', default=None, help='Binding value')
    parser.add_argument('--personality', '-p', default=None, help='Path to the personality folder')
    parser.add_argument('--model_name', '-m', default=None, help='Model name')
    
    args = parser.parse_args()
    cfg = BindingConfig(args.config)
    if args.binding:
        cfg.binding = args.binding
    if args.model_name:
        cfg.model = args.model_name
        
    model = build_model(args.bindings_path, cfg)
    personality = AIPersonality(args.personality)    
    full_discussion_blocks.append(personality.personality_conditioning)
    full_discussion_blocks.append(personality.ai_message_prefix)
    full_discussion_blocks.append(personality.welcome_message)
    full_discussion_blocks.append(personality.link_text) 
    
    st.title("LordOfLLMs (LLLMs)")
    st.markdown("Welcome to the Lord of LLMS. One tool to rule them ALL")

    # Get user input
    elements["output"] = st.empty()
    user_input = st.text_input("User:", "")

    if user_input:
        # Generate a response using the chatbot
        bot_response = generate_response(model, personality, user_input)
        
        # Display the response
        st.text_area(personality.name+":", bot_response, height=300)

# Run the app
if __name__ == "__main__":
    main()




