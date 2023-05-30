import subprocess
from pathlib import Path
import requests
from tqdm import tqdm
import yaml

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

            # Create configuration file
            self.create_config_file()

            # Create .installed file
            with open(install_file,"w") as f:
                f.write("ok")
            print("Installed successfully")

    def create_config_file(self):
        """
        Create a config_local.yaml file with predefined data.

        The function creates a config_local.yaml file with the specified data. The file is saved in the parent directory
        of the current file.

        Args:
            None

        Returns:
            None
        """
        data = {
            "pdf_file_path":  "" # Path to the PDF that will be discussed
        }
        path = Path(__file__).parent.parent / 'config_local.yaml'
        with open(path, 'w') as file:
            yaml.dump(data, file)