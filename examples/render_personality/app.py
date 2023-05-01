import yaml
from flask import Flask, render_template, send_from_directory
from pyaipersonality import AIPersonality
from pathlib import Path
import sys

app = Flask(__name__)

personality_path = Path("../../personalities_zoo/english/scifi/HAL9000")

if (personality_path/"assets/gltf").exists(): # personality has a gltf ile
    personality = AIPersonality(personality_path)
    gltf_model = str(Path("/english/scifi/HAL9000/assets/gltf/model.gltf"))
else:
    print(f"{personality_path} not found")    
    exit(1)

@app.route('/personalities_zoo')
def serve_file(filename):
    directory = '../../personalities_zoo/'
    return send_from_directory(directory, filename)

@app.route("/")
def index():
    return render_template("index.html", model_path=gltf_model, model_name=personality.name)

if __name__ == "__main__":
    app.run(debug=True)
