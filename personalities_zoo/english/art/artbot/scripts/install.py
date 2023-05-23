import subprocess
from pathlib import Path
import requests
from tqdm import tqdm

class Install:
    def __init__(self, personality):
        # Get the current directory
        current_dir = Path(__file__).resolve().parent.parent
        sd_folder = current_dir / "sd"

        if not sd_folder.exists():
            print("This is the first time you are using this personality.")
            print("Installing ...")
            
            # Step 2: Install dependencies using pip from requirements.txt
            requirements_file = current_dir / "requirements.txt"
            subprocess.run(["pip", "install", "-r", str(requirements_file), "-f", "https://download.pytorch.org/whl/cu117/torch_stable.html"])

            # Step 1: Clone repository
            subprocess.run(["git", "clone", "https://github.com/CompVis/stable-diffusion.git", str(sd_folder)])

            # Step 5: Install the Python package inside sd folder
            subprocess.run(["pip", "install", str(sd_folder)])

            # Step 3: Create models/Stable-diffusion folder if it doesn't exist
            models_folder = current_dir / "models"
            models_folder.mkdir(parents=True, exist_ok=True)

            # Step 4: Download model file
            model_url = "https://huggingface.co/Lykon/DreamShaper/resolve/main/DreamShaper_5_beta2_noVae_half_pruned.ckpt"
            model_file = models_folder / "DreamShaper_5_beta2_noVae_half_pruned.ckpt"
            
            # Download with progress using tqdm
            response = requests.get(model_url, stream=True)
            total_size = int(response.headers.get("content-length", 0))
            block_size = 1024  # 1KB
            progress_bar = tqdm(total=total_size, unit="B", unit_scale=True)
            
            with open(model_file, "wb") as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
            
            progress_bar.close()