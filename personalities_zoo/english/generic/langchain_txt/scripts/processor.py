from pyaipersonality import PAPScript, AIPersonality

from langchain.text_splitter import CharacterTextSplitter 
from langchain.embeddings.llamacpp import LlamaCppEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.base_language import BaseLanguageModel
from langchain.schema import BaseMessage, LLMResult, PromptValue, get_buffer_string
from typing import List, Optional, Sequence, Set
from langchain.llms import LlamaCpp
from langchain.callbacks.manager import Callbacks
from pathlib import Path
import yaml

class Processor(PAPScript):
    """
    A class that processes model inputs and outputs.

    Inherits from PAPScript.
    """

    def __init__(self, personality: AIPersonality, model = None) -> None:
        super().__init__()
        self.personality = personality
        self.model = model
        self.config = self.load_config_file()
        self.build_db()

    def load_config_file(self):
        """
        Load the content of config_local.yaml file.

        The function reads the content of the config_local.yaml file and returns it as a Python dictionary.

        Args:
            None

        Returns:
            dict: A dictionary containing the loaded data from the config_local.yaml file.
        """        
        path = Path(__file__).parent.parent / 'config_local.yaml'
        with open(path, 'r') as file:
            data = yaml.safe_load(file)
        return data

    @staticmethod
    def read_text_file(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    
    def build_db(self):
        self.txt =  Processor.read_text_file(self.config["txt_file_path"])

        self.text_splitter = CharacterTextSplitter(
            chunk_size=250,
            chunk_overlap=0,
            length_function=len
        )
        self.chunks = self.text_splitter.split_text(self.txt)
        print("Vectorizing document")
        
        self.vector_store = FAISS.from_texts(self.chunks, embedding=self.model)
        print("Vectorization done successfully")

   

    def run_workflow(self, generate_fn, prompt, previous_discussion_text="", step_callback=None):
        """
        Runs the workflow for processing the model input and output.

        This method should be called to execute the processing workflow.

        Args:
            generate_fn (function): A function that generates model output based on the input prompt.
                The function should take a single argument (prompt) and return the generated text.
            prompt (str): The input prompt for the model.
            previous_discussion_text (str, optional): The text of the previous discussion. Default is an empty string.

        Returns:
            None
        """
        output =""
        docs = self.vector_store.similarity_search(prompt, k=3)
        chain = load_qa_chain(llm=LlamaCpp(model_path="models/llama_cpp_official/Wizard-Vicuna-7B-Uncensored.ggmlv2.q4_0.bin"), chain_type="stuff")
        response = chain.run(input_documents=docs, question=prompt)
        print(f"response: {response}")


        return output



