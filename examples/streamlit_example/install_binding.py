from pyaipersonality import AIPersonality
from pyaipersonality.binding import BindingConfig
from pathlib import Path
import argparse
import importlib


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

# Create the Streamlit UI
def main():
    parser = argparse.ArgumentParser()
    # Place your model in models/<the binding name> 
    # streamlit run examples/streamlit_example/streamlit_example.py -- -m Manticore-13B.ggmlv3.q4_0.bin
    
    parser.add_argument('--bindings_path', '-bp', default="bindings_zoo", help='Binding path')
    parser.add_argument('--binding', '-b', default=None, help='Binding value')
    args = parser.parse_args()
    cfg = BindingConfig(args.config)
    if args.binding:
        cfg.binding = args.binding
    if args.model_name:
        cfg.model = args.model_name
        
    model = build_model(args.bindings_path, cfg)    
    