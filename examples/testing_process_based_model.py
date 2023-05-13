import multiprocessing as mp
import time
from pyGpt4All.config import load_config, save_config
import importlib
from pathlib import Path
import sys 
from pyaipersonality import AIPersonality

class ModelProcess:
    def __init__(self, config=None):
        self.config = config
        self.generate_queue = mp.Queue()
        self.generation_queue = mp.Queue()
        self.cancel_queue = mp.Queue(maxsize=1)
        self.clear_queue_queue = mp.Queue(maxsize=1)
        self.set_config_queue = mp.Queue(maxsize=1)
        self.started_queue = mp.Queue()
        self.process = None
        self.is_generating  = mp.Value('i', 0)
            
    def load_backend(self, backend_path):

        # define the full absolute path to the module
        absolute_path = backend_path.resolve()

        # infer the module name from the file path
        module_name = backend_path.stem

        # use importlib to load the module from the file path
        loader = importlib.machinery.SourceFileLoader(module_name, str(absolute_path/"__init__.py"))
        backend_module = loader.load_module()
        backend_class = getattr(backend_module, backend_module.backend_name)
        return backend_class

    def start(self):
        if self.process is None:
            self.process = mp.Process(target=self._run)
            self.process.start()

    def stop(self):
        if self.process is not None:
            self.generate_queue.put(None)
            self.process.join()
            self.process = None

    def set_backend(self, backend_path):
        self.backend = backend_path

    def set_model(self, model_path):
        self.model = model_path
        
    def set_config(self, config):
        self.set_config_queue.put(config)
        

    def generate(self, prompt, id):
        self.generate_queue.put((prompt, id))

    def cancel_generation(self):
        self.cancel_queue.put(('cancel',))

    def clear_queue(self):
        self.clear_queue_queue.put(('clear_queue',))

    def rebuild_model(self):
        try:
            self.backend = self.load_backend(Path("backends")/self.config["backend"])
            print("Backend loaded successfully")
            self.model = self.backend(self.config)
            print("Model created successfully")
        except Exception as ex:
            print("Couldn't build backend")
            print(ex)
            
    def rebuild_personality(self):
        try:
            personality_path = f"personalities/{self.config['personality_language']}/{self.config['personality_category']}/{self.config['personality']}"
            self.personality = AIPersonality(personality_path)
        except Exception as ex:
            print("Personality file not found. Please verify that the personality you have selected exists or select another personality. Some updates may lead to change in personality name or category, so check the personality selection in settings to be sure.")
            if self.config["debug"]:
                print(ex)
            self.personality = AIPersonality()
            
    def _run(self):
        
        self.rebuild_model()
        self.rebuild_personality()
        while True:
            self._check_cancel_queue()
            self._check_clear_queue()

            command = self.generate_queue.get()
            if command is None:
                break

            if self.cancel_queue.empty() and self.clear_queue_queue.empty():
                self.is_generating.value = 1
                self.started_queue.put(1)
                self._generate(*command)
                self.is_generating.value = 0
 
    def _generate(self, prompt, id):
        self.id = id
        total_n_predict = self.config['n_predict']
        print(f"Generating {total_n_predict} outputs... ")
        print(f"Input text :\n{prompt}",end="")        
        if self.config["override_personality_model_parameters"]:
            self.model.generate(
                prompt,
                new_text_callback=self._callback,
                n_predict=total_n_predict,
                temp=self.config['temperature'],
                top_k=self.config['top_k'],
                top_p=self.config['top_p'],
                repeat_penalty=self.config['repeat_penalty'],
                repeat_last_n = self.config['repeat_last_n'],
                seed=self.config['seed'],
                n_threads=self.config['n_threads']
            )
        else:
            self.model.generate(
                prompt,
                new_text_callback=self._callback,
                n_predict=total_n_predict,
                temp=self.personality.model_temperature,
                top_k=self.personality.model_top_k,
                top_p=self.personality.model_top_p,
                repeat_penalty=self.personality.model_repeat_penalty,
                repeat_last_n = self.personality.model_repeat_last_n,
                #seed=self.config['seed'],
                n_threads=self.config['n_threads']
            )


    def _check_cancel_queue(self):
        while not self.cancel_queue.empty():
            command = self.cancel_queue.get()
            if command is not None:
                self._cancel_generation()

    def _check_clear_queue(self):
        while not self.clear_queue_queue.empty():
            command = self.clear_queue_queue.get()
            if command is not None:
                self._clear_queue()

    def _check_set_config_queue(self):
        while not self.set_config_queue.empty():
            config = self.set_config_queue.get()
            if config is not None:
                self._set_config(config)

    def _cancel_generation(self):
        # Perform any necessary cancellation logic
        while not self.cancel_queue.empty():
            self.cancel_queue.get()
            self.is_generating.value = 0
            
    def _clear_queue(self):
        while not self.generate_queue.empty():
            self.generate_queue.get()

    def _set_config(self, config):
        bk_cfg = self.config
        self.config = config
        # verify that the backend is the same
        if self.config["backend"]!=bk_cfg["backend"] or self.config["model"]!=bk_cfg["model"]:
            self.rebuild_model()
            
        # verify that the personality is the same
        if self.config["personality"]!=bk_cfg["personality"] or self.config["personality_category"]!=bk_cfg["personality_category"] or self.config["personality_language"]!=bk_cfg["personality_language"]:
            self.rebuild_personality()
        
        
    def _callback(self, text):
        # Stream the generated text to the main process
        self.generation_queue.put((text,self.id))
        # if stop generation is detected then stop
        if self.is_generating.value==1:
            return True
        else:
            return False
        
if __name__ == '__main__':
    config_file_path = f"configs/local_default.yaml"
    config = load_config(config_file_path)
    
    # Example usage
    process = ModelProcess(config)
    process.start()

    process.generate("""
###gpt4all:
## Information:
Assistant's name is gpt4all
Today's date is Saturday, May 13, 2023
## Instructions:
Your mission is to assist user to perform various tasks and answer his questions
###gpt4all:
Welcome! My name is gpt4all.
How can I help you today?

###user:
Help me write a poem
###gpt4all:                 
"""
        , 0)
    process.started_queue.get()
    while(process.is_generating.value):  # Simulating other commands being issued
        while not process.generation_queue.empty():
            chunk = process.generation_queue.get()
            print(chunk[0],end="")
            sys.stdout.flush()

    print("New stuff)")
    process.generate('Another prompt', 2)
    time.sleep(5)  # Simulating more commands being issued
    process.cancel_generation()


    process.clear_queue()
    process.stop()
