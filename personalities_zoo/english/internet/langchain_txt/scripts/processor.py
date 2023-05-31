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

class Processor(PAPScript):
    """
    A class that processes model inputs and outputs.

    Inherits from PAPScript.
    """

    def __init__(self, personality: AIPersonality, model = None) -> None:
        super().__init__()
        self.personality = personality
        self.model = model
    @staticmethod
    def read_text_file(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    
    def build_db(self):
        self.txt =  Processor.read_text_file(self.config["text_file_path"])

        self.text_splitter = CharacterTextSplitter(
            chunk_size=250,
            chunk_overlap=0,
            length_function=len
        )
        self.chunks = self.text_splitter.split_text(text)
        print("Vectorizing document")
        self.emb = LlamaCppEmbeddings(model_path="models/llama_cpp_official/Wizard-Vicuna-7B-Uncensored.ggmlv2.q4_0.bin", n_ctx=2048)
        
        self.vector_store = FAISS.from_texts(self.chunks, embedding=self.emb)
        print("Vectorization done successfully")



    

    def run_workflow(self, generate_fn, prompt, previous_discussion_text="", callback=None):
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



