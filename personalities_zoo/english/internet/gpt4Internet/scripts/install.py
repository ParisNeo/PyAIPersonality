import subprocess
from pathlib import Path
import requests
from tqdm import tqdm

class Install:
    def __init__(self, personality):
        # Get the current directory
        current_dir = Path(__file__).resolve().parent.parent
        install_file = current_dir / ".installed"

        if not install_file.exists():
            print(f"This is the first time you are using this personality : {personality.name}.")
            print("Installing ...")
            
            # Step 2: Install dependencies using pip from requirements.txt
            requirements_file = current_dir / "requirements.txt"
            subprocess.run(["pip", "install", "--no-cache-dir", "-r", str(requirements_file)])
            with open(install_file,"w") as f:
                f.write("ok")
            print("Installed successfully")
            
