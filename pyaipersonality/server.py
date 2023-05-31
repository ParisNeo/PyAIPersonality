from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from pyaipersonality import AIPersonality
from pyaipersonality.binding import BindingConfig
import importlib
from pathlib import Path
import argparse


def build_model(bindings_path:Path, cfg: BindingConfig):
    binding_path = Path("bindings")/cfg["binding"]
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
    # use importlib to load the module from the file path
    loader = importlib.machinery.SourceFileLoader(module_name, str(absolute_path/"__init__.py"))
    binding_module = loader.load_module()
    binding_class = getattr(binding_module, binding_module.binding_name)

    model = binding_class(cfg)
    return model

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('generate_text')
def handle_generate_text(data):
    # Placeholder code for text generation
    # Replace this with your actual text generation logic
    prompt = data['prompt']
    generated_text = f"Generated text for '{prompt}'"

    # Emit the generated text to the client
    emit('text_generated', {'text': generated_text})

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-cfg', default=None, help='Path to the configuration file')
    parser.add_argument('--bindings_path', '-p', default="bindings_zoo", help='Binding path')
    parser.add_argument('--binding', '-b', default=None, help='Binding value')
    parser.add_argument('--model_name', '-m', default=None, help='Model name')
    args = parser.parse_args()
    cfg = BindingConfig(Path(args.indings_path) ,args.config)
    if args.binding:
        cfg.binding = args.binding
    if args.model:
        cfg.model = args.model_name
    build_model()
    socketio.run(app)
