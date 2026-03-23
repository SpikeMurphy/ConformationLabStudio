import os
import threading
import subprocess
import sys
import tarfile
import shutil
from tkinter import *
from tkinter import filedialog, messagebox

# Path
if getattr(sys, 'frozen', False):
    # PyInstaller bundle
    APPDIR = sys._MEIPASS
else:
    # Normal Python script run
    APPDIR = os.path.dirname(os.path.abspath(__file__))
ENV_TAR = os.path.join(APPDIR, "colabfold_env.tar.gz")
ENV_DIR = os.path.expanduser("~/Library/Application Support/ColabFoldEnv")
# Unpack if not already unpacked
if not os.path.exists(os.path.join(ENV_DIR, "bin")):
    os.makedirs(ENV_DIR, exist_ok=True)
    if os.path.exists(ENV_TAR):
        with tarfile.open(ENV_TAR, "r:gz") as tar:
            tar.extractall(ENV_DIR)
colabfold_bin = os.path.join(ENV_DIR, "bin", "colabfold_batch")

# Root (Window)
root = Tk()
root.title("ColabFold[AlphaFold2]")
root.geometry("900x600")

# Selecting paths 
def select_input_path():
    path = filedialog.askopenfilename(title="Select input file")
    if path:
        inputpath_selected.set(path)

def select_output_path():
    path = filedialog.askdirectory(title="Select output folder")
    if path:
        outputpath_selected.set(path)
        
inputpath_selected = StringVar()
outputpath_selected = StringVar()

input_label = Label(root, text="Input file:")
input_label.grid(row=0 , column=0, sticky="w")
input_entry = Entry(root, textvariable=inputpath_selected, width=50)
input_entry.grid(row=0 , column=1, padx=5, pady=2)
input_button = Button(root, text = "Browse", command = select_input_path)
input_button.grid(row=0 , column=2)

output_label = Label(root, text="Output folder:")
output_label.grid(row=2 , column= 0, sticky="w")
output_entry = Entry(root, textvariable = outputpath_selected, width=50)
output_entry.grid(row=2 , column=1, padx=5, pady=2)
output_button = Button(root, text = "Browse", command = select_output_path)
output_button.grid(row=2 , column=2)

# Placeholders
_tmp = Entry(root)
DEFAULT_ENTRY_FG = _tmp.cget("fg") or "black"
_tmp.destroy()
def add_placeholder(entry, placeholder, default_fg = DEFAULT_ENTRY_FG):
    entry.insert(0, placeholder)
    entry.config(fg="grey")

    def on_focus_in(event):
        if entry.get() == placeholder:
            entry.delete(0, "end")
            entry.config(fg=default_fg)

    def on_focus_out(event):
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.config(fg="grey")

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

# Entrys for parameters
num_relax_label = Label(root, text="Number of Relaxes:")
num_relax_label.grid(row=3 , column=0, sticky="w")
num_relax_entry = Entry(root, )
num_relax_entry.grid(row=3 , column=1, padx=5, pady=2)
add_placeholder(num_relax_entry, "Enter Number")

num_recycle_label = Label(root, text="Number of Recycles:")
num_recycle_label.grid(row=4 , column=0, sticky="w")
num_recycle_entry = Entry(root, )
num_recycle_entry.grid(row=4 , column=1, padx=5, pady=2)
add_placeholder(num_recycle_entry, "Enter Number")

num_seeds_label = Label(root, text="Number of Seeds:")
num_seeds_label.grid(row=5 , column=0, sticky="w")
num_seeds_entry = Entry(root, )
num_seeds_entry.grid(row=5 , column=1, padx=5, pady=2)
add_placeholder(num_seeds_entry, "Enter Number")

max_msa_label = Label(root, text="Number of Sequences for Multi Sequence Alignment:")
max_msa_label.grid(row=6 , column=0, sticky="w")
max_msa_frame = Frame(root)
max_msa_frame.grid(row=6, column=1, padx=5, pady=2)
max_msa_entry1 = Entry(max_msa_frame, width=15)
max_msa_entry1.pack(side=LEFT)
add_placeholder(max_msa_entry1, "unpaired sequences")
max_msa_label_div = Label(max_msa_frame, text = ":")
max_msa_label_div.pack(side=LEFT)
max_msa_entry2 = Entry(max_msa_frame, width=15)
max_msa_entry2.pack(side=LEFT)
add_placeholder(max_msa_entry2, "paired sequences")

# Dropdowns for parameters
model_type_label = Label(root, text = "Model:")
model_type_label.grid(row=7, column=0, sticky="w")
model_type_options = ["alphafold2_ptm", "alphafold2_multimer_v3"]
model_type_default = StringVar(value = "alphafold2_ptm")
model_type_dropdown = OptionMenu(root, model_type_default, *model_type_options)
model_type_dropdown.grid(row=7 , column=1)

pair_mode_label = Label(root, text = "Pair Mode:")
pair_mode_label.grid(row=8, column=0, sticky="w")
pair_mode_options = ["unpaired_paired", "unpaired", "paired"]
pair_mode_default = StringVar(value = "unpaired_paired")
pair_mode_dropdown = OptionMenu(root, pair_mode_default, *pair_mode_options)
pair_mode_dropdown.grid(row=8 , column=1)

msa_mode_label = Label(root, text = "MSA Mode:")
msa_mode_label.grid(row=9, column=0, sticky="w")
msa_mode_options = ["mmseqs2_uniref"]
msa_mode_default = StringVar(value = "mmseqs2_uniref")
msa_mode_dropdown = OptionMenu(root, msa_mode_default, *msa_mode_options)
msa_mode_dropdown.grid(row=9 , column=1)

rank_label = Label(root, text = "Rank:")
rank_label.grid(row=10, column=0, sticky="w")
rank_options = ["plddt", "multimer"]
rank_default = StringVar(value = "plddt")
rank_dropdown = OptionMenu(root, rank_default, *rank_options)
rank_dropdown.grid(row=10 , column=1)

# Dropdown menu templates
templates_label = Label(root, text = "Templates:")
templates_label.grid(row=11, column=0, sticky="w")
templates_options = ["Yes", "No"]
templates_default = StringVar(value = "No")
templates_dropdown = OptionMenu(root, templates_default, *templates_options)
templates_dropdown.grid(row=11 , column=1)

# Dropdown menu amber
amber_label = Label(root, text = "Relaxation:")
amber_label.grid(row=12, column=0, sticky="w")
amber_options = ["Yes", "No"]
amber_default = StringVar(value = "No")
amber_dropdown = OptionMenu(root, amber_default, *amber_options)
amber_dropdown.grid(row=12 , column=1)

# button clear all inputs
def clear_button_command():
    inputpath_selected.set("")
    outputpath_selected.set("")

    num_relax_entry.delete(0, END)
    num_recycle_entry.delete(0, END)
    num_seeds_entry.delete(0, END)
    max_msa_entry1.delete(0, END)
    max_msa_entry2.delete(0, END)

    model_type_default.set("alphafold2_ptm")
    pair_mode_default.set("unpaired_paired")
    msa_mode_default.set("mmseqs2_uniref")
    rank_default.set("plddt")
    templates_default.set("No")
    amber_default.set("No")
clear_button = Button(root, text = "clear all", command = clear_button_command)
clear_button.grid(row=13, column=1, pady=5)

# Message widget
output_text = Text(root, wrap="word", height=15, width=100, state="disabled")
output_text.grid(row=14, column=0, columnspan=3, padx=5, pady=10, sticky="nsew")

# Scrollbar for message
scrollbar = Scrollbar(root, command=output_text.yview)
output_text.config(yscrollcommand=scrollbar.set)
scrollbar.grid(row=14, column=3, sticky="ns")

# Message
def write_output(message, error=False):
    output_text.config(state="normal")
    if error:
        output_text.insert("end", "[ERR] " + message + "\n", "error")
        output_text.tag_config("error", foreground="red")
    else:
        output_text.insert("end", message + "\n")
    output_text.see("end")
    output_text.config(state="disabled")


# button run prediction
def run_button_command():
    # Collect parameters
    inputpath = inputpath_selected.get()
    outputpath = outputpath_selected.get()
    if not inputpath or not outputpath:
        messagebox.showerror("Error", "Please select input and output paths")
        return
    if not os.path.exists(colabfold_bin):
        write_output(f"[FATAL ERROR] colabfold_batch not found at {colabfold_bin}", error=True)
        return
    num_relax = num_relax_entry.get()
    num_recycle = num_recycle_entry.get()
    num_seeds = num_seeds_entry.get()
    max_msa = max_msa_entry1.get() + ":" + max_msa_entry2.get()
    model_type = model_type_default.get()
    pair_mode = pair_mode_default.get()
    msa_mode = msa_mode_default.get()
    rank = rank_default.get()
    templates = templates_default.get()
    amber = amber_default.get()
    # Create protein prediction command
    prediction_command = [
        colabfold_bin, inputpath, outputpath,
        "--num-relax", str(num_relax),
        "--num-recycle", str(num_recycle),
        "--num-seeds", str(num_seeds),
        "--max-msa", str(max_msa),
        "--model-type", model_type,
        "--pair-mode", pair_mode,
        "--msa-mode", msa_mode,
        "--rank", rank
    ]
    if templates_default.get() == "Yes":
        prediction_command.append("--templates")
    if amber_default.get() == "Yes":
        prediction_command.append("--amber")
    
    write_output("Running command: " + " ".join(prediction_command))

    def run_process():
        try:
            env = os.environ.copy()
            env["PATH"] = os.path.join(ENV_DIR, "bin") + os.pathsep + env["PATH"]
            env["LD_LIBRARY_PATH"] = os.path.join(ENV_DIR, "lib") + os.pathsep + env.get("LD_LIBRARY_PATH", "")

            process = subprocess.Popen(
                prediction_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env
            )
            for line in process.stdout:
                if line.strip():
                    write_output(line.strip())
            process.wait()
            write_output(f"Finished with code {process.returncode}")
        except Exception as e:
            write_output(f"[FATAL ERROR] {e}", error=True)

    threading.Thread(target=run_process, daemon=True).start()

run_button = Button(root, text = "run", command = run_button_command)
run_button.grid(row=13, column=2, pady=5)

root.mainloop()