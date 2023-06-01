# Tuto
## Install for your project
```bash
pip install --upgrade pyaipersonality
```
Now create your project with the following structure
root
|- bindings/
| |- Grub a binding from the bindings zoo
|- models/
| |- The binding name (will be created when you install the binding)
|- personalities/
| |- Here you can install any personality you want from the zoo
|- install_binding.py
|- streamlit_example.py

Copy those files in your root path:
|- install_binding.py
|- streamlit_example.py

First we need to install the binding :
```bash
python install_binding.py -bp bindings -b binding_name
```
Now, download a model from the zoo (in your binding folder, look at models.yaml and download one of the models) look at the parameter server and filename and combine them to get the full link. for example in llama_cpp_official, you can download this model:
```
https://huggingface.co/TheBloke/Manticore-13B-GGML/resolve/main/Manticore-13B.ggmlv3.q4_0.bin
```

Once done, you are ready to go. Launch your streamlit server :
```bash
streamlit run examples/streamlit_example/streamlit_example.py -- -bp bindings -m Manticore-13B.ggmlv3.q4_0.bin
```
## Install from here
```bash
python install_binding.py -b binding_name
```
Now, download a model from the zoo (in your binding folder, look at models.yaml and download one of the models) look at the parameter server and filename and combine them to get the full link. for example in llama_cpp_official, you can download this model:
```
https://huggingface.co/TheBloke/Manticore-13B-GGML/resolve/main/Manticore-13B.ggmlv3.q4_0.bin
```
Once done, you are ready to go. Launch your streamlit server :
```bash
streamlit run examples/streamlit_example/streamlit_example.py -- -m Manticore-13B.ggmlv3.q4_0.bin
```

# Note
you can also select your personality by using -p and giving the full path to the personality
