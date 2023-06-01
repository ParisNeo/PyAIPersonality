# AIPersonality Server and PyQt Client

This is a Python project that consists of a server and a PyQt client for interacting with the AIPersonality text generation model. The server is built using Flask and Flask-SocketIO, while the client is implemented using PyQt5.

## Server

The server code is located in the file `lllm_server.py`. It sets up a Flask application with Flask-SocketIO to establish a WebSocket connection with clients. The server receives text generation requests from clients, generates text based on the given prompt, and sends the generated text back to the clients.

To run the server, execute the following command:

```bash
python server.py --host localhost --port 9600 --config configs/config.yaml --bindings_path bindings_zoo
```
You can customize the host, port, configuration file, and bindings path by providing appropriate command-line arguments.

## Client
The client code is implemented using PyQt5 and can be found in the file client.py. It provides a graphical user interface (GUI) for interacting with the server. The client connects to the server using WebSocket and allows users to enter a prompt and generate text based on that prompt.

To run the client, execute the following command:

```bash
pyaipersonality-server  --host 0.0.0.0 --port 9600
```
The client GUI will appear, and you can enter a prompt in the text area. Click the "Generate Text" button to send the prompt to the server for text generation. The generated text will be displayed in the text area.

Make sure you have the necessary dependencies installed, such as Flask, Flask-SocketIO, Flask-CORS, pyaipersonality, and PyQt5, before running the server and client.

## Dependencies
The project depends on the following Python packages:

- Flask
- Flask-SocketIO
- Flask-CORS
- pyaipersonality
- PyQt5

You can install the dependencies using pip:
```bash
pip install flask flask-socketio flask-cors pyaipersonality pyqt5
```

# License
PyAIPersonality is licensed under the Apache 2.0 license. See the `LICENSE` file for more information.
