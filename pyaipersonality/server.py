from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from pyaipersonality import AIPersonality
from pyaipersonality.binding import BindingConfig
import importlib
from pathlib import Path
import argparse
import logging

# Store connected clients
clients = {}

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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)
# Set log level to warning
app.logger.setLevel(logging.WARNING)
# Configure a custom logger for Flask-SocketIO
socketio_log = logging.getLogger('socketio')
socketio_log.setLevel(logging.WARNING)
socketio_log.addHandler(logging.StreamHandler())


@socketio.on('connect')
def handle_connect():
    client_id = request.sid
    clients[client_id] = request.namespace
    print(f'Client connected with session ID: {client_id}')

@socketio.on('disconnect')
def handle_disconnect():
    client_id = request.sid
    if client_id in clients:
        del clients[client_id]
    print(f'Client disconnected with session ID: {client_id}')


@socketio.on('generate_text')
def handle_generate_text(data):
    # Placeholder code for text generation
    # Replace this with your actual text generation logic
    client_id = data['client_id']
    prompt = data['prompt']
    generated_text = f"Generated text for '{prompt}'"
    print(f"Text generation requested by client :{client_id}")

    def callback(text):
        print(text,end="",flush=True)
        # Emit the generated text to the client
        emit('text_chunk', {'chunk': text}, room=clients[client_id])
        return True

    generated_text = model.generate(prompt, new_text_callback=callback)
    
    # Emit the generated text to the client
    emit('text_generated', {'text': generated_text}, room=clients[client_id])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', '-hst', default="localhost", help='Host name')
    parser.add_argument('--port', '-prt', default="9600", help='Port number')
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
    personality = AIPersonality()
    socketio.run(app, host=args.host, port=args.port)
