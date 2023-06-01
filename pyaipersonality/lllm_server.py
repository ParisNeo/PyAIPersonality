from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from pyaipersonality import AIPersonality, MSG_TYPE
from pyaipersonality.binding import BindingConfig
import importlib
from pathlib import Path
import argparse
import logging

# Reset
color_reset = '\u001b[0m'

# Regular colors
color_black = '\u001b[30m'
color_red = '\u001b[31m'
color_green = '\u001b[32m'
color_yellow = '\u001b[33m'
color_blue = '\u001b[34m'
color_magenta = '\u001b[35m'
color_cyan = '\u001b[36m'
color_white = '\u001b[37m'

# Bright colors
color_bright_black = '\u001b[30;1m'
color_bright_red = '\u001b[31;1m'
color_bright_green = '\u001b[32;1m'
color_bright_yellow = '\u001b[33;1m'
color_bright_blue = '\u001b[34;1m'
color_bright_magenta = '\u001b[35;1m'
color_bright_cyan = '\u001b[36;1m'
color_bright_white = '\u001b[37;1m'
# Store connected clients
clients = {}
models = []
personalities = {}
answer = ['']

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

app = Flask("AIPersonality_Server")
app.config['SECRET_KEY'] = 'your-secret-key'
CORS(app)  # Enable CORS for all routes
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
    clients[client_id] = {"namespace":request.namespace,"full_discussion_blocks":[]}
    print(f'Client connected with session ID: {client_id}')

@socketio.on('disconnect')
def handle_disconnect():
    client_id = request.sid
    if client_id in clients:
        del clients[client_id]
    print(f'Client disconnected with session ID: {client_id}')

@socketio.on('list_personalities')
def handle_list_personalities():
    personality_names = list(personalities.keys())
    emit('personalities_list', {'personalities': personality_names}, room=request.sid)

@socketio.on('add_personality')
def handle_add_personality(data):
    personality_path = data['path']
    try:
        personality = AIPersonality(personality_path)
        personalities[personality.name] = personality
        emit('personality_added', {'name': personality.name}, room=request.sid)
    except Exception as e:
        error_message = str(e)
        emit('personality_add_failed', {'error': error_message}, room=request.sid)


@socketio.on('generate_text')
def handle_generate_text(data):
    model = models[0]
    client_id = request.sid
    prompt = data['prompt']
    personality:AIPersonality = personalities[data['personality']]
    # Placeholder code for text generation
    # Replace this with your actual text generation logic
    print(f"Text generation requested by client :{client_id}")

    answer[0]=''
    full_discussion_blocks = clients[client_id]["full_discussion_blocks"]
    def callback(text, messsage_type:MSG_TYPE):
        if messsage_type==MSG_TYPE.MSG_TYPE_CHUNK:
            answer[0]  = answer[0] + text
            emit('text_chunk', {'chunk': text}, room=client_id)
        return True
    
    if personality.processor is not None and personality.processor_cfg["process_model_input"]:
        preprocessed_prompt = personality.processor.process_model_input(prompt)
    else:
        preprocessed_prompt = prompt
        
    full_discussion_blocks.append(personality.user_message_prefix)
    full_discussion_blocks.append(preprocessed_prompt)
    full_discussion_blocks.append(personality.link_text)
    full_discussion_blocks.append(personality.ai_message_prefix)
        
    full_discussion = personality.personality_conditioning + ''.join(full_discussion_blocks)
    
    print(f"---------------- Input prompt -------------------")
    print(f"{color_green}{full_discussion}")
    print(f"{color_reset}--------------------------------------------")
    if personality.processor is not None and personality.processor_cfg["custom_workflow"]:
        print("processing...",end="",flush=True)
        generated_text = personality.processor.run_workflow(prompt, full_discussion, callback=callback)
    else:
        print("generating...",end="",flush=True)
        generated_text = model.generate(full_discussion, n_predict=personality.model_n_predicts, callback=callback)
    full_discussion_blocks.append(generated_text)
    print(f"{color_green}ok{color_reset}",end="",flush=True)    

    
    # Emit the generated text to the client
    emit('text_generated', {'text': generated_text}, room=client_id)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', '-hst', default="localhost", help='Host name')
    parser.add_argument('--port', '-prt', default="9600", help='Port number')
    parser.add_argument('--config', '-cfg', default="configs/config.yaml", help='Path to the configuration file')
    parser.add_argument('--bindings_path', '-bp', default="bindings_zoo", help='Binding path')
    parser.add_argument('--binding', '-b', default=None, help='Binding value')
    parser.add_argument('--personalities', '-p', nargs='+', default=[], help='A list of path to the personalites folders')
    parser.add_argument('--model_name', '-m', default="Manticore-13B.ggmlv3.q4_0.bin", help='Model name')
    args = parser.parse_args()
    path = Path(args.config)

    print("█       █        █       █▄  ▄█▄  ▄█")
    print("█       █        █       █ ▀▀   ▀▀ █")
    print("█       █        █       █         █")
    print("█▄▄▄▄   █▄▄▄▄▄   █▄▄▄▄   █         █")
    if path.exists():
        cfg = BindingConfig(args.config)
    else:
        cfg = BindingConfig()

    if args.binding:
        cfg.binding = args.binding

    if args.model_name:
        cfg.model = args.model_name
    model = build_model(args.bindings_path, cfg)
    models.append(model)

    personalities["default_personality"]=AIPersonality()
    for p in args.personalities:
        personality = AIPersonality(p)
        personalities[personality.name] = personality

    socketio.run(app, host=args.host, port=args.port)

if __name__ == '__main__':
    main()