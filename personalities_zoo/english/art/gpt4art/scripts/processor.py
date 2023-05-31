import subprocess
from pathlib import Path
import os
import sys
sd_folder = Path(".") / "shared/sd"
sys.path.append(str(sd_folder))
from scripts.txt2img import *
from pyaipersonality import PAPScript, AIPersonality
import time

import sys
import yaml
import re
import argparse

class SD:
    def __init__(self, gpt4art_config):
        # Get the current directory
        root_dir = Path(".")
        current_dir = Path(__file__).resolve().parent

        # Store the path to the script
        shared_folder = root_dir/"shared"
        self.sd_folder = shared_folder / "sd"

        self.script_path = self.sd_folder / "scripts" / "txt2img.py"
        # Add the sd folder to the import path
        
        parser = argparse.ArgumentParser()

        parser.add_argument(
            "--prompt",
            type=str,
            nargs="?",
            default="a painting of a virus monster playing guitar",
            help="the prompt to render"
        )
        parser.add_argument(
            "--outdir",
            type=str,
            nargs="?",
            help="dir to write results to",
            default="outputs/txt2img-samples"
        )
        parser.add_argument(
            "--skip_grid",
            action='store_true',
            help="do not save a grid, only individual samples. Helpful when evaluating lots of samples",
        )
        parser.add_argument(
            "--skip_save",
            action='store_true',
            help="do not save individual samples. For speed measurements.",
        )
        parser.add_argument(
            "--ddim_steps",
            type=int,
            default=50,
            help="number of ddim sampling steps",
        )
        parser.add_argument(
            "--plms",
            action='store_true',
            help="use plms sampling",
        )
        parser.add_argument(
            "--dpm_solver",
            action='store_true',
            help="use dpm_solver sampling",
        )
        parser.add_argument(
            "--laion400m",
            action='store_true',
            help="uses the LAION400M model",
        )
        parser.add_argument(
            "--fixed_code",
            action='store_true',
            help="if enabled, uses the same starting code across samples ",
        )
        parser.add_argument(
            "--ddim_eta",
            type=float,
            default=0.0,
            help="ddim eta (eta=0.0 corresponds to deterministic sampling",
        )
        parser.add_argument(
            "--n_iter",
            type=int,
            default=1,
            help="sample this often",
        )
        parser.add_argument(
            "--H",
            type=int,
            default=512,
            help="image height, in pixel space",
        )
        parser.add_argument(
            "--W",
            type=int,
            default=512,
            help="image width, in pixel space",
        )
        parser.add_argument(
            "--C",
            type=int,
            default=4,
            help="latent channels",
        )
        parser.add_argument(
            "--f",
            type=int,
            default=8,
            help="downsampling factor",
        )
        parser.add_argument(
            "--n_samples",
            type=int,
            default=1,
            help="how many samples to produce for each given prompt. A.k.a. batch size",
        )
        parser.add_argument(
            "--n_rows",
            type=int,
            default=0,
            help="rows in the grid (default: n_samples)",
        )
        parser.add_argument(
            "--scale",
            type=float,
            default=7.5,
            help="unconditional guidance scale: eps = eps(x, empty) + scale * (eps(x, cond) - eps(x, empty))",
        )
        parser.add_argument(
            "--from-file",
            type=str,
            help="if specified, load prompts from this file",
        )
        parser.add_argument(
            "--config",
            type=str,
            default="configs/stable-diffusion/v1-inference.yaml",
            help="path to config which constructs model",
        )
        parser.add_argument(
            "--ckpt",
            type=str,
            default="models/ldm/stable-diffusion-v1/model.ckpt",
            help="path to checkpoint of model",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=-1,
            help="the seed (for reproducible sampling)",
        )
        parser.add_argument(
            "--precision",
            type=str,
            help="evaluate at this precision",
            choices=["full", "autocast"],
            default="autocast"
        )
        opt = parser.parse_args()

        if opt.laion400m:
            print("Falling back to LAION 400M model...")
            opt.config = "configs/latent-diffusion/txt2img-1p4B-eval.yaml"
            opt.ckpt = "models/ldm/text2img-large/model.ckpt"
            opt.outdir = "outputs/txt2img-samples-laion400m"
        else:
            opt.ckpt = root_dir/ "shared" / "sd_models"/ gpt4art_config["model_name"]

        opt.ddim_steps = gpt4art_config.get("ddim_steps",50)
        opt.scale = gpt4art_config.get("scale",7.5)
        opt.W = gpt4art_config.get("W",512)
        opt.H = gpt4art_config.get("H",512)
        opt.skip_grid = gpt4art_config.get("skip_grid",True)
        opt.batch_size = gpt4art_config.get("batch_size",1)
        opt.num_images = gpt4art_config.get("num_images",1)
        
        

        
        config = OmegaConf.load(f"{self.sd_folder / opt.config}")
        self.model = load_model_from_config(config, f"{opt.ckpt}")

        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        self.model = self.model.to(device)

        if gpt4art_config["sampler_name"].lower()=="dpms":
            self.sampler = DPMSolverSampler(self.model)
        elif gpt4art_config["sampler_name"].lower()=="plms":
            self.sampler = PLMSSampler(self.model)
        else:
            self.sampler = DDIMSampler(self.model)
        

        os.makedirs(opt.outdir, exist_ok=True)

        print("Creating invisible watermark encoder (see https://github.com/ShieldMnt/invisible-watermark)...")
        wm = "Gpt4Art"
        self.wm_encoder = WatermarkEncoder()
        self.wm_encoder.set_watermark('bytes', wm.encode('utf-8'))


        self.opt = opt

    def generate(self, prompt, num_images=1, seed = -1):
        self.opt.seed=seed
        self.opt.num_images=num_images
        outpath = self.opt.outdir
        batch_size = 1
        n_rows = self.opt.n_rows if self.opt.n_rows > 0 else batch_size
        seed_everything(self.opt.seed)

        if not self.opt.from_file:
            assert prompt is not None
            data = [batch_size * [prompt]]

        else:
            print(f"reading prompts from {self.opt.from_file}")
            with open(self.opt.from_file, "r") as f:
                data = f.read().splitlines()
                data = list(chunk(data, batch_size))

        sample_path = os.path.join(outpath, "samples")
        os.makedirs(sample_path, exist_ok=True)
        base_count = len(os.listdir(sample_path))
        grid_count = len(os.listdir(outpath)) - 1

        start_code = None
        if self.opt.fixed_code:
            start_code = torch.randn([self.opt.n_samples, self.opt.C, self.opt.H // self.opt.f, self.opt.W // self.opt.f], device=device)

        precision_scope = autocast if self.opt.precision=="autocast" else nullcontext
        with torch.no_grad():
            with precision_scope("cuda"):
                with self.model.ema_scope():
                    tic = time.time()
                    all_samples = list()
                    for n in trange(self.opt.num_images, desc="Sampling"):
                        for prompts in tqdm(data, desc="data"):
                            uc = None
                            if self.opt.scale != 1.0:
                                uc = self.model.get_learned_conditioning(batch_size * [""])
                            if isinstance(prompts, tuple):
                                prompts = list(prompts)
                            c = self.model.get_learned_conditioning(prompts)
                            shape = [self.opt.C, self.opt.H // self.opt.f, self.opt.W // self.opt.f]
                            samples_ddim, _ = self.sampler.sample(S=self.opt.ddim_steps,
                                                            conditioning=c,
                                                            batch_size=self.opt.batch_size,
                                                            shape=shape,
                                                            verbose=False,
                                                            unconditional_guidance_scale=self.opt.scale,
                                                            unconditional_conditioning=uc,
                                                            eta=self.opt.ddim_eta,
                                                            x_T=start_code)

                            x_samples_ddim = self.model.decode_first_stage(samples_ddim)
                            x_samples_ddim = torch.clamp((x_samples_ddim + 1.0) / 2.0, min=0.0, max=1.0)
                            x_samples_ddim = x_samples_ddim.cpu().permute(0, 2, 3, 1).numpy()

                            x_checked_image, has_nsfw_concept = check_safety(x_samples_ddim)

                            x_checked_image_torch = torch.from_numpy(x_checked_image).permute(0, 3, 1, 2)

                            if not self.opt.skip_save:
                                for x_sample in x_checked_image_torch:
                                    x_sample = 255. * rearrange(x_sample.cpu().numpy(), 'c h w -> h w c')
                                    img = Image.fromarray(x_sample.astype(np.uint8))
                                    img = put_watermark(img, self.wm_encoder)
                                    img.save(os.path.join(sample_path, f"{base_count:05}.png"))
                                    base_count += 1

                            if not self.opt.skip_grid:
                                all_samples.append(x_checked_image_torch)

                    if not self.opt.skip_grid:
                        # additionally, save as grid
                        grid = torch.stack(all_samples, 0)
                        grid = rearrange(grid, 'n b c h w -> (n b) c h w')
                        grid = make_grid(grid, nrow=n_rows)

                        # to image
                        grid = 255. * rearrange(grid, 'c h w -> h w c').cpu().numpy()
                        img = Image.fromarray(grid.astype(np.uint8))
                        img = put_watermark(img, self.wm_encoder)
                        img.save(os.path.join(outpath, f'grid-{grid_count:04}.png'))
                        grid_count += 1

                    toc = time.time()

        print(f"Your samples are ready and waiting for you here: \n{outpath} \n"+f" \nEnjoy.")
        
        out_put_path = Path("outputs/txt2img-samples/samples")
        files =[f for f in out_put_path.iterdir()]
        return files[-num_images:]
        

   
class Processor(PAPScript):
    """
    A class that processes model inputs and outputs.

    Inherits from PAPScript.
    """

    def __init__(self, personality: AIPersonality) -> None:
        super().__init__()
        self.personality = personality
        self.word_callback = None
        self.generate_fn = None
        self.config = self.load_config_file()
        self.sd = SD(self.config)

    def load_config_file(self):
        """
        Load the content of config_local.yaml file.

        The function reads the content of the config_local.yaml file and returns it as a Python dictionary.

        Args:
            None

        Returns:
            dict: A dictionary containing the loaded data from the config_local.yaml file.
        """        
        path = Path(__file__).parent.parent / 'config_local.yaml'
        with open(path, 'r') as file:
            data = yaml.safe_load(file)
        return data


    def remove_image_links(self, markdown_text):
        # Regular expression pattern to match image links in Markdown
        image_link_pattern = r"!\[.*?\]\((.*?)\)"

        # Remove image links from the Markdown text
        text_without_image_links = re.sub(image_link_pattern, "", markdown_text)

        return text_without_image_links

    def remove_text_from_string(self, string, text_to_find):
        """
        Removes everything from the first occurrence of the specified text in the string (case-insensitive).

        Parameters:
        string (str): The original string.
        text_to_find (str): The text to find in the string.

        Returns:
        str: The updated string.
        """
        index = string.lower().find(text_to_find.lower())

        if index != -1:
            string = string[:index]

        return string
    
    def process(self, text):
        bot_says = self.bot_says + text
        antiprompt = self.personality.detect_antiprompt(bot_says)
        if antiprompt:
            self.bot_says = self.remove_text_from_string(bot_says,antiprompt)
            print("Detected hallucination")
            return False
        else:
            self.bot_says = bot_says
            return True

    def generate(self, prompt, max_size):
        self.bot_says = ""
        return self.personality.model.generate(
                                prompt, 
                                max_size, 
                                self.process,
                                temperature=self.personality.model_temperature,
                                top_k=self.personality.model_top_k,
                                top_p=self.personality.model_top_p,
                                repeat_penalty=self.personality.model_repeat_penalty,
                                ).strip()    
        

    def run_workflow(self, prompt, previous_discussion_text="", callback=None):
        """
        Runs the workflow for processing the model input and output.

        This method should be called to execute the processing workflow.

        Args:
            generate_fn (function): A function that generates model output based on the input prompt.
                The function should take a single argument (prompt) and return the generated text.
            prompt (str): The input prompt for the model.
            previous_discussion_text (str, optional): The text of the previous discussion. Default is an empty string.
            callback a callback function that gets called each time a new token is received
        Returns:
            None
        """
        self.word_callback = callback

        # 1 first ask the model to formulate a query
        prompt = f"{self.remove_image_links(previous_discussion_text+self.personality.user_message_prefix+prompt+self.personality.link_text+self.personality.ai_message_prefix)}\n"
        print(prompt)
        sd_prompt = self.generate(prompt, self.config["max_generation_prompt_size"])
        if callback is not None:
            callback(sd_prompt.strip()+"\n", 0)

        files = self.sd.generate(sd_prompt.strip(), self.config["num_images"], self.config["seed"])
        output = sd_prompt.strip()+"\n"
        for i in range(len(files)):
            files[i] = str(files[i]).replace("\\","/")
            output += f"![]({files[i]})\n"

        return output


