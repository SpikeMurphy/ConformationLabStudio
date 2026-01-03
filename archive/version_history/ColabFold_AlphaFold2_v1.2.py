import os
import threading
import subprocess
import sys
import tarfile
import itertools
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

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
root.geometry("920x800")

# header frame
header_frame = Frame(root)
header_frame.grid(row=0, column=0, columnspan=4, sticky="w", pady=10, padx=10)
# logo
logo_path = os.path.join(APPDIR, "logo.png")
if os.path.exists(logo_path):
    logo_img = Image.open(logo_path).resize((100, 100), Image.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    logo_label = Label(header_frame, image=logo_photo)
    logo_label.image = logo_photo
    logo_label.pack(side=LEFT, padx=(10), pady=5)
title_frame = Frame(header_frame)
title_frame.pack(side=LEFT, padx=10)
title_label = Label(title_frame, text="LocalColabFold Studio", 
                    font=("Arial", 22, "bold"), fg="white")
title_label.pack(anchor="w")
subtitle_label = Label(title_frame, text="Local Protein Structure Prediction for Apple Devices", 
                       font=("Arial", 12), fg="white")
subtitle_label.pack(anchor="w")

# Background image 80% opacity
bg_image_path = os.path.join(APPDIR, "background.png")
if os.path.exists(bg_image_path):
    bg_image = Image.open(bg_image_path)
    bg_image = bg_image.resize((920, 800), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)

    bg_label = Label(root, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

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

input_label = Label(root, padx=10, text="Input file:")
input_label.grid(row=1 , column=0, sticky="w")
input_entry = Entry(root, textvariable=inputpath_selected, bg="#2b2b2b", width=50)
input_entry.grid(row=1 , column=1, padx=10, pady=2)
input_button = Button(root, text = "Browse", command = select_input_path)
input_button.grid(row=1 , column=2)

output_label = Label(root, padx=10, text="Output folder:")
output_label.grid(row=2 , column= 0, sticky="w")
output_entry = Entry(root, textvariable = outputpath_selected, bg="#2b2b2b", width=50)
output_entry.grid(row=2 , column=1, padx=10, pady=2)
output_button = Button(root, text = "Browse", command = select_output_path)
output_button.grid(row=2 , column=2)

# ToolTip i
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)
    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip_window = tw = Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = Label(
            tw,
            text=self.text,
            background="darkgrey",
            fg="#007acc",
            relief="solid",
            borderwidth=1,
            justify="left",
            wraplength=300
        )
        label.pack(ipadx=1, ipady=1)
    def hide_tip(self, event=None):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

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
num_relax_label = Label(root, padx=10, text="Number of Relaxes:")
num_relax_label.grid(row=3 , column=0, sticky="w")
num_relax_entry = Entry(root,  bg="#2b2b2b")
num_relax_entry.grid(row=3 , column=1, padx=10, pady=2)
num_relax_entry.insert(0, "0")
# add_placeholder(num_relax_entry, "Enter Number")

num_recycle_label = Label(root, padx=10, text="Number of Recycles:")
num_recycle_label.grid(row=4 , column=0, sticky="w")
num_recycle_entry = Entry(root,  bg="#2b2b2b")
num_recycle_entry.grid(row=4 , column=1, padx=10, pady=2)
num_recycle_entry.insert(0, "3")
# add_placeholder(num_recycle_entry, "Enter Number") # either placeholder or default
# info button
num_recycle_info = Label(root, text="ⓘ", fg="#007acc", cursor="hand2")
num_recycle_info.grid(row=4, column=2)
num_recycle_tooltip = ToolTip(
    num_recycle_info,
    "Number of times each of the five models is refined. Default=3 -> 3 times 5 models = 15 cycles total."
    )

num_seeds_label = Label(root, padx=10, text="Number of Seeds:")
num_seeds_label.grid(row=5 , column=0, sticky="w")
num_seeds_entry = Entry(root, bg="#2b2b2b")
num_seeds_entry.grid(row=5 , column=1, padx=10, pady=2)
num_seeds_entry.insert(0, "3")
# add_placeholder(num_seeds_entry, "Enter Number")
# info button
num_seeds_info = Label(root, text="ⓘ", fg="#007acc", cursor="hand2")
num_seeds_info.grid(row=5, column=2)
num_seeds_tooltip = ToolTip(
    num_seeds_info,
    "Number of independent predictions. Amount of times the five models are computed. Default=3 -> 3 times 5 models and 3 recycles = 45 cycles total."
    )

random_seeds_label = Label(root, padx=10, text="Randome Seeds:")
random_seeds_label.grid(row=6 , column=0, sticky="w")
random_seeds_entry = Entry(root, bg="#2b2b2b")
random_seeds_entry.grid(row=6 , column=1, padx=10, pady=2)
random_seeds_entry.insert(0, "")
# add_placeholder(random_seeds_entry, "Enter Number")
# info button
random_seeds_info = Label(root, text="ⓘ", fg="#007acc", cursor="hand2")
random_seeds_info.grid(row=6, column=2)
random_seeds_tooltip = ToolTip(
    random_seeds_info,
    "Set a specific random seed for reproducibility. For random-seed=45 and num-seed=3, seeds 45, 46 and 47 will be used. Leave empty for randome seed choice."
    )

max_msa_label = Label(root, padx=10, text="Number of Sequences for Multi Sequence Alignment:")
max_msa_label.grid(row=7 , column=0, sticky="w")
max_msa_frame = Frame(root)
max_msa_frame.grid(row=7, column=1, padx=10, pady=2)
max_msa_entry1 = Entry(max_msa_frame, width=15, bg="#2b2b2b")
max_msa_entry1.pack(side=LEFT)
max_msa_entry1.insert(0, "256")
# add_placeholder(max_msa_entry1, "unpaired sequences")
max_msa_label_div = Label(max_msa_frame, text = ":")
max_msa_label_div.pack(side=LEFT)
max_msa_entry2 = Entry(max_msa_frame, width=15, bg="#2b2b2b")
max_msa_entry2.pack(side=LEFT)
max_msa_entry2.insert(0, "256")
# add_placeholder(max_msa_entry2, "paired sequences")
# info button
max_msa_info = Label(root, text="ⓘ", fg="#007acc", cursor="hand2")
max_msa_info.grid(row=7, column=2)
max_msa_tooltip = ToolTip(
    max_msa_info,
    "Number of multi seqence alignments. <unpaired>:<paired>. Number of alignments of single chains and chain pairs."
    )

# Dropdowns for parameters
model_type_label = Label(root, padx=10, text = "Model:")
model_type_label.grid(row=8, column=0, sticky="w")
model_type_options = ["auto", "alphafold2_ptm", "alphafold2_multimer_v1", "alphafold2_multimer_v2", "alphafold2_multimer_v3"]
model_type_default = StringVar(value = "alphafold2_ptm")
model_type_dropdown = OptionMenu(root, model_type_default, *model_type_options)
model_type_dropdown.grid(row=8 , column=1, padx=10, pady=2)
# info button
model_type_info = Label(root, text="ⓘ", fg="#007acc", cursor="hand2")
model_type_info.grid(row=8, column=2)
model_type_tooltip = ToolTip(
    model_type_info,
    "The default is auto. Usually recommended: 'alphafold2_ptm' for single chains and 'alphafold2_multimer_v3' for multiple chains."
    )

pair_mode_label = Label(root, padx=10, text = "Pair Mode:")
pair_mode_label.grid(row=9, column=0, sticky="w")
pair_mode_options = ["unpaired_paired", "unpaired", "paired"]
pair_mode_default = StringVar(value = "unpaired_paired")
pair_mode_dropdown = OptionMenu(root, pair_mode_default, *pair_mode_options)
pair_mode_dropdown.grid(row=9 , column=1, padx=10, pady=2)
# info button
pair_mode_info = Label(root, text="ⓘ", fg="#007acc", cursor="hand2")
pair_mode_info.grid(row=9, column=2)
pair_mode_tooltip = ToolTip(
    pair_mode_info,
    "Default 'unpaired_paired' wich does both. 'unpaired' uses independent alignments only for each chain and 'paired' only uses paired sequences and can be used when complexes are well preserved."
    )

msa_mode_label = Label(root, padx=10, text = "MSA Mode:")
msa_mode_label.grid(row=10, column=0, sticky="w")
msa_mode_options = ["mmseqs2_uniref", "mmseqs2_env", "jackhmmer_uniref"]
msa_mode_default = StringVar(value = "mmseqs2_uniref")
msa_mode_dropdown = OptionMenu(root, msa_mode_default, *msa_mode_options)
msa_mode_dropdown.grid(row=10 , column=1, padx=10, pady=2)
# info button
msa_mode_info = Label(root, text="ⓘ", fg="#007acc", cursor="hand2")
msa_mode_info.grid(row=10, column=2)
msa_mode_tooltip = ToolTip(
    msa_mode_info,
    "Default 'mmseqs2_uniref' searches for MSA against UniRef databasses. 'mmseqs2_env' additionally searches environmental sequences and can be used for rare proteins with runtime drawbacks. 'jackhmmer_uniref' can find very distant homologs and is very slow."
    )

rank_label = Label(root, padx=10, text = "Rank:")
rank_label.grid(row=11, column=0, sticky="w")
rank_options = ["plddt", "multimer"]
rank_default = StringVar(value = "plddt")
rank_dropdown = OptionMenu(root, rank_default, *rank_options)
rank_dropdown.grid(row=11 , column=1, padx=10, pady=2)
# info button
rank_info = Label(root, text="ⓘ", fg="#007acc", cursor="hand2")
rank_info.grid(row=11, column=2)
rank_tooltip = ToolTip(
    rank_info,
    "Use 'plddt' for single sequences and 'multimer' for complexes."
    )

# Dropdown menu templates
templates_label = Label(root, padx=10, text = "Templates:")
templates_label.grid(row=12, column=0, sticky="w")
templates_options = ["Yes", "No"]
templates_default = StringVar(value = "No")
templates_dropdown = OptionMenu(root, templates_default, *templates_options)
templates_dropdown.grid(row=12 , column=1, padx=10, pady=2)
# info button
templates_info = Label(root, text="ⓘ", fg="#007acc", cursor="hand2")
templates_info.grid(row=12, column=2)
templates_tooltip = ToolTip(
    templates_info,
    "Used to allow the model to bias against reference sequences from databases."
    )

# Dropdown menu amber
amber_label = Label(root, padx=10, text = "Relaxation:")
amber_label.grid(row=13, column=0, sticky="w")
amber_options = ["Yes", "No"]
amber_default = StringVar(value = "No")
amber_dropdown = OptionMenu(root, amber_default, *amber_options)
amber_dropdown.grid(row=13 , column=1, padx=10, pady=2)
# info button
amber_info = Label(root, text="ⓘ", fg="#007acc", cursor="hand2")
amber_info.grid(row=13, column=2)
amber_tooltip = ToolTip(
    amber_info,
    "Used to relax the prediction by running energy minimisation thereby fixing unrealistic bond lengths and angles caused by steric clashes or strained bond geometrics."
    )

# button clear all inputs
def clear_button_command():
    inputpath_selected.set("")
    outputpath_selected.set("")

    num_relax_entry.delete(0, END); num_relax_entry.insert(0, "0")
    num_recycle_entry.delete(0, END); num_recycle_entry.insert(0, "3")
    num_seeds_entry.delete(0, END); num_seeds_entry.insert(0, "3")
    random_seeds_entry.delete(0, END)
    max_msa_entry1.delete(0, END); max_msa_entry1.insert(0, "256")
    max_msa_entry2.delete(0, END); max_msa_entry2.insert(0, "256")

    model_type_default.set("alphafold2_ptm")
    pair_mode_default.set("unpaired_paired")
    msa_mode_default.set("mmseqs2_uniref")
    rank_default.set("plddt")
    templates_default.set("No")
    amber_default.set("No")
clear_button = Button(root, text = "clear all", fg="red", command = clear_button_command)
clear_button.grid(row=14, column=1, padx=10, pady=10)

# Message widget
output_text = Text(root, wrap="word", height=15, width=100, state="disabled")
output_text.grid(row=15, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

# Scrollbar for message
scrollbar = Scrollbar(root, command=output_text.yview)
output_text.config(yscrollcommand=scrollbar.set)
scrollbar.grid(row=15, column=3, sticky="ns")

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

# running a task animation
loading_label = Label(root, text="", fg="blue", font=("Arial", 12, "bold"))
loading_label.grid(row=16, column=1, pady=5)
loading_animation_running = False
def start_loading_animation():
    global loading_animation_running
    loading_animation_running = True
    spinner = itertools.cycle(["🏃🏻‍♂️                   🚴🏻",
                               "🏃🏻‍♂️                 🚴🏻",
                               "🏃🏻‍♂️               🚴🏻",
                               "🏃🏻‍♂️             🚴🏻",
                               "🏃🏻‍♂️           🚴🏻",
                               "🏃🏻‍♂️         🚴🏻",
                               "🏃🏻‍♂️       🚴🏻",
                               "🏃🏻‍♂️💥🚲",
                               "🧎🏻‍♂️‍➡️🧎🏻",
                               "🧎🏻‍♂️‍➡️🧎🏻          🐦‍⬛       🚑",
                               "🧎🏻‍♂️‍➡️🧎🏻         🐦‍⬛       🚑",
                               "🧎🏻‍♂️‍➡️🧎🏻        🐦‍⬛      🚑",
                               "🧎🏻‍♂️‍➡️🧎🏻       🐦‍⬛     🚑",
                               "🧎🏻‍♂️‍➡️🧎🏻      🐦‍⬛    🚑",
                               "🧎🏻‍♂️‍➡️🧎🏻     🐦‍⬛   🚑",
                               "🧎🏻‍♂️‍➡️🧎🏻    🐦‍⬛  🚑",
                               "🧎🏻‍♂️‍➡️🧎🏻   🐦‍⬛💥🚑",
                               "👀",
                               "👀"])
    def animate():
        if loading_animation_running:
            loading_label.config(text= next(spinner), fg="blue")
            root.after(1000, animate) 
    animate()
def stop_loading_animation(success=True):
    global loading_animation_running
    loading_animation_running = False
    if success:
        loading_label.config(text="✅ Finished", fg="green")
    else:
        loading_label.config(text="❌ Error", fg="red")

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
    num_relax = num_relax_entry.get().strip() or "0"
    num_recycle = num_recycle_entry.get().strip() or "3"
    num_seeds = num_seeds_entry.get().strip() or "3"
    random_seeds = random_seeds_entry.get()
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
    if random_seeds_entry.get().strip() != "":
        prediction_command.extend(["--random-seed", random_seeds_entry.get().strip()])
    if templates_default.get() == "Yes":
        prediction_command.append("--templates")
    if amber_default.get() == "Yes":
        prediction_command.append("--amber")
    write_output("Running command: " + " ".join(prediction_command))
    # start running a task animation
    start_loading_animation() # start running a task animation
    run_button.config(state="disabled") # disable run button
    cancel_button.config(state="normal") # enable terminate button
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
        # stop running a task animation
        finally: # stop running a task animation
            stop_loading_animation(success=(process.returncode == 0 if 'process' in locals() else False)) # stop running a task animation
            run_button.config(state="normal") # enable run button
    threading.Thread(target=run_process, daemon=True).start()
run_button = Button(root, text = "run", fg="green", command = run_button_command)
run_button.grid(row=14, column=2, padx=10, pady=10)

root.mainloop()