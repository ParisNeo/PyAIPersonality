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
            print("-------------- GPT4ALL backend -------------------------------")
            print("This is the first time you are using this backend.")
            print("Installing ...")
            try:
                print("Checking pytorch")
                import torch
                import torchvision
                if torch.cuda.is_available():
                    print("CUDA is supported.")
                else:
                    print("CUDA is not supported. Reinstalling PyTorch with CUDA support.")
                    self.reinstall_pytorch_with_cuda()
            except Exception as ex:
                self.reinstall_pytorch_with_cuda()

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
            
    def reinstall_pytorch_with_cuda(self):
        subprocess.run(["pip", "install", "torch", "torchvision", "torchaudio", "--no-cache-dir", "--index-url", "https://download.pytorch.org/whl/cu117"])
        