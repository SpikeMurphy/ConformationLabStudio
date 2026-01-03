import os
import threading
import subprocess
import sys
import tarfile
import itertools
from tkinter import *
from tkinter import filedialog, messagebox # Messagebox
from tkinter import ttk # mol*viewer button progress bar + scrollbar
from PIL import Image, ImageTk # Logo

# Path
if getattr(sys, 'frozen', False):
    APPDIR = sys._MEIPASS
else:
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
root.title("ShipFold Studio")
root.grid_rowconfigure(0, weight=0)
root.grid_rowconfigure(1, weight=0)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=0)
root.grid_columnconfigure(0, weight=1)

# center window 90%
def get_centered_geometry(scale=0.9):
    # Temporär Tk-Fenster für Bildschirmmaße
    tmp_root = Tk()
    tmp_root.withdraw()
    tmp_root.update_idletasks()
    try:
        # macOS: verfügbare Fläche ohne Menü/Dock
        from AppKit import NSScreen
        frame = NSScreen.mainScreen().visibleFrame()
        screen_width = int(frame.size.width)
        screen_height = int(frame.size.height)
    except ImportError:
        # Fallback: normale Bildschirmmaße
        screen_width = tmp_root.winfo_screenwidth()
        screen_height = tmp_root.winfo_screenheight()
    tmp_root.destroy()
    window_width = int(screen_width * scale)
    window_height = int(screen_height * scale)
    window_x = (screen_width - window_width) // 2
    window_y = (screen_height - window_height) // 2
    return window_width, window_height, window_x, window_y
window_width, window_height, window_x, window_y = get_centered_geometry(0.9)
root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

# header frame
header_frame = Frame(root)
header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=0, padx=10)
# separator
separator = Frame(root, height=2, bg="white", relief="sunken")
separator.grid(row=1, column=0, columnspan=3, sticky="ew", pady=10, padx=10)

# logo
logo_path = os.path.join(APPDIR, "ShipFoldLogo.png")
if os.path.exists(logo_path):
    logo_img = Image.open(logo_path).resize((100, 100), Image.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    logo_label = Label(header_frame, image=logo_photo)
    logo_label.image = logo_photo
    logo_label.grid(row=0, column=0, rowspan=2, padx=10, pady=5)
title_frame = Frame(header_frame)
title_frame.grid(row=0, column=1, sticky="w", padx=10)
title_label = Label(title_frame, text="ShipFold Studio", 
                    font=("Arial", 22, "bold"), fg="white")
title_label.grid(row=0, column=0, sticky="w")
subtitle_label = Label(title_frame, text="Local Protein Structure Prediction for Apple Devices", 
                       font=("Arial", 12), fg="white")
subtitle_label.grid(row=1, column=0, sticky="w")

# scrollbar
# define scrollbar when neccessary

# Scrollable main frame
main_container = Frame(root)
main_container.grid(row=2, column=0, columnspan=3, sticky="nsew")
main_canvas = Canvas(main_container, highlightthickness=0)
main_canvas.pack(side=LEFT, fill=BOTH, expand=True)
scrollable_frame = Frame(main_canvas)
window_id = main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

def show_scrollbar(event=None):
    v_scrollbar.grid(row=0, column=1, sticky="ns")

def hide_scrollbar(event=None):
    v_scrollbar.grid_remove()

main_canvas.bind("<Enter>", show_scrollbar)
main_canvas.bind("<Leave>", hide_scrollbar)

# Scrolling main frame and messagebox
def on_frame_configure(event):
    bbox = main_canvas.bbox(window_id)
    if bbox:
        main_canvas.configure(scrollregion=bbox)
    print("Canvas-BBox:", bbox)
    print("Canvas-Items:", main_canvas.find_all())
scrollable_frame.bind("<Configure>", on_frame_configure)
def on_canvas_configure(event):
    main_canvas.itemconfig(window_id, width=event.width)
main_canvas.bind("<Configure>", on_canvas_configure)
# Unified Scroll Handling
def _on_global_mousewheel(event):
    widget = root.winfo_containing(event.x_root, event.y_root)
    if widget is not None and (widget == output_text or str(widget).startswith(str(output_text))):
        if sys.platform == "darwin":
            output_text.yview_scroll(-1 * event.delta, "units")
        else:
            output_text.yview_scroll(-1 * (event.delta // 120), "units")
        return "break"
    if sys.platform == "darwin":
        main_canvas.yview_scroll(-1 * event.delta, "units")
    else:
        main_canvas.yview_scroll(-1 * (event.delta // 120), "units")
    return "break"
root.bind_all("<MouseWheel>", _on_global_mousewheel)

# widgets middle
scrollable_frame.grid_columnconfigure(0, weight=1)  # linke Spalte
scrollable_frame.grid_columnconfigure(1, weight=1)  # mittlere Spalte
scrollable_frame.grid_columnconfigure(2, weight=1)  # rechte Spalte

# Background image (with 80% opacity)
"""
bg_image_path = os.path.join(APPDIR, "background.png")
if os.path.exists(bg_image_path):
    bg_image = Image.open(bg_image_path)
    bg_image.resize((window_width, window_height), Image.LANCZOS)
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_item = main_canvas.create_image(0, 0, image=bg_photo, anchor="nw")
    main_canvas.bg_photo = bg_photo
    main_canvas.tag_lower(bg_item)
"""
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

input_label = Label(scrollable_frame, padx=10, text="Input file:")
input_label.grid(row=0 , column=0, sticky="w")
input_entry = Entry(scrollable_frame, textvariable=inputpath_selected, bg="#2b2b2b")
input_entry.grid(row=0 , column=1, padx=10, pady=2)
input_button = Button(scrollable_frame, text = "Browse", fg="#000000", command = select_input_path)
input_button.grid(row=0 , column=2)

output_label = Label(scrollable_frame, padx=10, text="Output folder:")
output_label.grid(row=3 , column= 0, sticky="w")
output_entry = Entry(scrollable_frame, textvariable = outputpath_selected, bg="#2b2b2b")
output_entry.grid(row=3 , column=1, padx=10, pady=2)
output_button = Button(scrollable_frame, text = "Browse", fg="#000000", command = select_output_path)
output_button.grid(row=3 , column=2)

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

# only numbers
def only_numbers(new_value):
    if new_value.isdigit() or new_value == "":
        return True
    root.bell()
    return False
vcmd = (root.register(only_numbers), "%P")

# Placeholders
_tmp = Entry(scrollable_frame)
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
num_relax_label = Label(scrollable_frame, padx=10, text="Number of Relaxes:")
num_relax_label.grid(row=4 , column=0, sticky="w")
num_relax_entry = Entry(scrollable_frame,  bg="#2b2b2b", validate="key", validatecommand=vcmd)
num_relax_entry.grid(row=4 , column=1, padx=10, pady=2)
num_relax_entry.insert(0, "0")
# add_placeholder(num_relax_entry, "Enter Number")

num_recycle_label = Label(scrollable_frame, padx=10, text="Number of Recycles:")
num_recycle_label.grid(row=5 , column=0, sticky="w")
num_recycle_entry = Entry(scrollable_frame,  bg="#2b2b2b", validate="key", validatecommand=vcmd)
num_recycle_entry.grid(row=5 , column=1, padx=10, pady=2)
num_recycle_entry.insert(0, "3")
# add_placeholder(num_recycle_entry, "Enter Number") # either placeholder or default
# info button
num_recycle_info = Label(scrollable_frame, text="ⓘ", fg="#007acc", cursor="hand2")
num_recycle_info.grid(row=5, column=2)
num_recycle_tooltip = ToolTip(
    num_recycle_info,
    "Number of times each of the five models is refined. Default=3 -> 3 times 5 models = 15 cycles total."
    )

num_seeds_label = Label(scrollable_frame, padx=10, text="Number of Seeds:")
num_seeds_label.grid(row=6 , column=0, sticky="w")
num_seeds_entry = Entry(scrollable_frame, bg="#2b2b2b", validate="key", validatecommand=vcmd)
num_seeds_entry.grid(row=6 , column=1, padx=10, pady=2)
num_seeds_entry.insert(0, "3")
# add_placeholder(num_seeds_entry, "Enter Number")
# info button
num_seeds_info = Label(scrollable_frame, text="ⓘ", fg="#007acc", cursor="hand2")
num_seeds_info.grid(row=6, column=2)
num_seeds_tooltip = ToolTip(
    num_seeds_info,
    "Number of independent predictions. Amount of times the five models are computed. Default=3 -> 3 times 5 models and 3 recycles = 45 cycles total."
    )

random_seeds_label = Label(scrollable_frame, padx=10, text="Randome Seeds:")
random_seeds_label.grid(row=7, column=0, sticky="w")
random_seeds_entry = Entry(scrollable_frame, bg="#2b2b2b", validate="key", validatecommand=vcmd)
random_seeds_entry.grid(row=7, column=1, padx=10, pady=2)
random_seeds_entry.insert(0, "")
# add_placeholder(random_seeds_entry, "Enter Number")
# info button
random_seeds_info = Label(scrollable_frame, text="ⓘ", fg="#007acc", cursor="hand2")
random_seeds_info.grid(row=7, column=2)
random_seeds_tooltip = ToolTip(
    random_seeds_info,
    "Set a specific random seed for reproducibility. For random-seed=45 and num-seed=3, seeds 45, 46 and 47 will be used. Leave empty for randome seed choice."
    )

max_msa_label = Label(scrollable_frame, padx=10, text="Number of Sequences for Multi Sequence Alignment:")
max_msa_label.grid(row=8, column=0, sticky="w")
max_msa_frame = Frame(scrollable_frame)
max_msa_frame.grid(row=8, column=1, padx=10, pady=2)
max_msa_entry1 = Entry(max_msa_frame, bg="#2b2b2b", validate="key", validatecommand=vcmd)
max_msa_entry1.pack(side=LEFT)
max_msa_entry1.insert(0, "256")
# add_placeholder(max_msa_entry1, "unpaired sequences")
max_msa_label_div = Label(max_msa_frame, text = ":")
max_msa_label_div.pack(side=LEFT)
max_msa_entry2 = Entry(max_msa_frame, bg="#2b2b2b", validate="key", validatecommand=vcmd)
max_msa_entry2.pack(side=LEFT)
max_msa_entry2.insert(0, "256")
# add_placeholder(max_msa_entry2, "paired sequences")
# info button
max_msa_info = Label(scrollable_frame, text="ⓘ", fg="#007acc", cursor="hand2")
max_msa_info.grid(row=8, column=2)
max_msa_tooltip = ToolTip(
    max_msa_info,
    "Number of multi seqence alignments. <unpaired>:<paired>. Number of alignments of single chains and chain pairs."
    )

# Dropdowns for parameters
model_type_label = Label(scrollable_frame, padx=10, text = "Model:")
model_type_label.grid(row=9, column=0, sticky="w")
model_type_options = ["auto", "alphafold2_ptm", "alphafold2_multimer_v1", "alphafold2_multimer_v2", "alphafold2_multimer_v3"]
model_type_default = StringVar(value = "alphafold2_ptm")
model_type_dropdown = OptionMenu(scrollable_frame, model_type_default, *model_type_options)
model_type_dropdown.grid(row=9 , column=1, padx=10, pady=2)
# info button
model_type_info = Label(scrollable_frame, text="ⓘ", fg="#007acc", cursor="hand2")
model_type_info.grid(row=9, column=2)
model_type_tooltip = ToolTip(
    model_type_info,
    "The default is auto. Usually recommended: 'alphafold2_ptm' for single chains and 'alphafold2_multimer_v3' for multiple chains."
    )

pair_mode_label = Label(scrollable_frame, padx=10, text = "Pair Mode:")
pair_mode_label.grid(row=10, column=0, sticky="w")
pair_mode_options = ["unpaired_paired", "unpaired", "paired"]
pair_mode_default = StringVar(value = "unpaired_paired")
pair_mode_dropdown = OptionMenu(scrollable_frame, pair_mode_default, *pair_mode_options)
pair_mode_dropdown.grid(row=10, column=1, padx=10, pady=2)
# info button
pair_mode_info = Label(scrollable_frame, text="ⓘ", fg="#007acc", cursor="hand2")
pair_mode_info.grid(row=10, column=2)
pair_mode_tooltip = ToolTip(
    pair_mode_info,
    "Default 'unpaired_paired' wich does both. 'unpaired' uses independent alignments only for each chain and 'paired' only uses paired sequences and can be used when complexes are well preserved."
    )

msa_mode_label = Label(scrollable_frame, padx=10, text = "MSA Mode:")
msa_mode_label.grid(row=11, column=0, sticky="w")
msa_mode_options = ["mmseqs2_uniref", "mmseqs2_env", "jackhmmer_uniref"]
msa_mode_default = StringVar(value = "mmseqs2_uniref")
msa_mode_dropdown = OptionMenu(scrollable_frame, msa_mode_default, *msa_mode_options)
msa_mode_dropdown.grid(row=11, column=1, padx=10, pady=2)
# info button
msa_mode_info = Label(scrollable_frame, text="ⓘ", fg="#007acc", cursor="hand2")
msa_mode_info.grid(row=11, column=2)
msa_mode_tooltip = ToolTip(
    msa_mode_info,
    "Default 'mmseqs2_uniref' searches for MSA against UniRef databasses. 'mmseqs2_env' additionally searches environmental sequences and can be used for rare proteins with runtime drawbacks. 'jackhmmer_uniref' can find very distant homologs and is very slow."
    )

rank_label = Label(scrollable_frame, padx=10, text = "Rank:")
rank_label.grid(row=12, column=0, sticky="w")
rank_options = ["plddt", "multimer"]
rank_default = StringVar(value = "plddt")
rank_dropdown = OptionMenu(scrollable_frame, rank_default, *rank_options)
rank_dropdown.grid(row=12 , column=1, padx=10, pady=2)
# info button
rank_info = Label(scrollable_frame, text="ⓘ", fg="#007acc", cursor="hand2")
rank_info.grid(row=12, column=2)
rank_tooltip = ToolTip(
    rank_info,
    "Use 'plddt' for single sequences and 'multimer' for complexes."
    )

# Dropdown menu templates
templates_label = Label(scrollable_frame, padx=10, text = "Templates:")
templates_label.grid(row=13, column=0, sticky="w")
templates_options = ["Yes", "No"]
templates_default = StringVar(value = "No")
templates_dropdown = OptionMenu(scrollable_frame, templates_default, *templates_options)
templates_dropdown.grid(row=13 , column=1, padx=10, pady=2)
# info button
templates_info = Label(scrollable_frame, text="ⓘ", fg="#007acc", cursor="hand2")
templates_info.grid(row=13, column=2)
templates_tooltip = ToolTip(
    templates_info,
    "Used to allow the model to bias against reference sequences from databases."
    )

# Dropdown menu amber
amber_label = Label(scrollable_frame, padx=10, text = "Relaxation:")
amber_label.grid(row=14, column=0, sticky="w")
amber_options = ["Yes", "No"]
amber_default = StringVar(value = "No")
amber_dropdown = OptionMenu(scrollable_frame, amber_default, *amber_options)
amber_dropdown.grid(row=14 , column=1, padx=10, pady=2)
# info button
amber_info = Label(scrollable_frame, text="ⓘ", fg="#007acc", cursor="hand2")
amber_info.grid(row=14, column=2)
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
clear_button = Button(scrollable_frame, text = "clear all", command = clear_button_command)
clear_button.grid(row=15, column=1, padx=10, pady=10)

# process termiante
def cancel_process():
    global process
    if process and process.poll() is None:  # läuft noch
        process.terminate()
        write_output("[INFO] Process terminated by user.", error=True)
        stop_loading_animation(success=False)
        run_button.config(state="normal")
        cancel_button.config(state="disabled")

# button cancel (terminate)
cancel_button = Button(scrollable_frame, text="cancel", command=cancel_process, state="disabled")
cancel_button.grid(row=17, column=1, padx=5, pady=10)

process = None

# Message widget
output_text = Text(scrollable_frame, wrap="word", height=15, state="disabled")
output_text.grid(row=16, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

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

# Message box scrollbar
# define message scrollbar when neccessary

# running a task animation
loading_label = Label(scrollable_frame)
loading_label.grid(row=17, column=0, pady=5)
loading_animation_running = False
def start_loading_animation():
    global loading_animation_running
    loading_animation_running = True
    spinner = itertools.cycle(["🏃🏻‍♂️                                 🚴🏻",
                               "🏃🏻‍♂️                               🚴🏻",
                               "🏃🏻‍♂️                             🚴🏻",
                               "🏃🏻‍♂️                           🚴🏻",
                               "🏃🏻‍♂️                         🚴🏻",
                               "🏃🏻‍♂️                       🚴🏻",
                               "🏃🏻‍♂️                     🚴🏻",
                               "🏃🏻‍♂️                   🚴🏻",
                               "🏃🏻‍♂️                 🚴🏻",
                               "🏃🏻‍♂️               🚴🏻",
                               "🏃🏻‍♂️             🚴🏻",
                               "🏃🏻‍♂️           🚴🏻",
                               "🏃🏻‍♂️         🚴🏻",
                               "🏃🏻‍♂️       🚴🏻",
                               "🏃🏻‍♂️💥🚴🏻",
                               "🏃🏻‍♂️💥🚴🏻",
                               "🧎🏻‍♂️‍➡️🚲🧎🏻",
                               "🧎🏻‍♂️‍➡️🚲🧎🏻",
                               "🧎🏻‍♂️‍➡️🚲🧎🏻",
                               "🧎🏻‍♂️‍➡️📞🧎🏻",
                               "🧎🏻‍♂️‍➡️📞🧎🏻",
                               "🧎🏻‍♂️‍➡️📞🧎🏻",
                               "🧎🏻‍♂️‍➡️🧎🏻                                      🚑",
                               "🧎🏻‍♂️‍➡️🧎🏻                                     🚑",
                               "🧎🏻‍♂️‍➡️🧎🏻                                    🚑",
                               "🧎🏻‍♂️‍➡️🧎🏻                 🐦‍⬛            🚑",
                               "🧎🏻‍♂️‍➡️🧎🏻                🐦‍⬛           🚑",
                               "🧎🏻‍♂️‍➡️🧎🏻               🐦‍⬛          🚑",
                               "🧎🏻‍♂️‍➡️🧎🏻              🐦‍⬛         🚑",
                               "🧎🏻‍♂️‍➡️🧎🏻             🐦‍⬛        🚑",
                               "🧎🏻‍♂️‍➡️🧎🏻            🐦‍⬛       🚑",
                               "🧎🏻‍♂️‍➡️🧎🏻           🐦‍⬛      🚑",
                               "🧎🏻‍♂️‍➡️🧎🏻          🐦‍⬛     🚑",
                               "🧎🏻‍♂️‍➡️🧎🏻         🐦‍⬛    🚑",
                               "🧎🏻‍♂️‍➡️🧎🏻       🐦‍⬛💥🚑",
                               "🧎🏻‍♂️‍➡️🧎🏻       🐦‍⬛💥🚑",
                               "👀",
                               "👀",
                               "👀",
                               "👀",
                               "👀",
                               "👀",
                               "🐦‍⬛ He is fine",
                               "🐦‍⬛ He is fine",
                               "🐦‍⬛ He is fine",
                               "🐦‍⬛ He is fine",
                               "🐦‍⬛ He is fine",
                               "🐦‍⬛ He is fine"])
    def animate():
        if loading_animation_running:
            loading_label.config(text= next(spinner))
            root.after(500, animate) 
    animate()
def stop_loading_animation(success=True):
    global loading_animation_running
    loading_animation_running = False
    if success:
        loading_label.config(text="✅ Finished", fg="green")
    else:
        loading_label.config(text="❌ Error", fg="red")

# button Mol*Viewer
def open_molstar():
    if getattr(sys, "frozen", False):
        molstar_path = os.path.join(os.path.dirname(sys.executable), "run_molstar")
        molstar_process = subprocess.Popen([molstar_path])
    else:
        molstar_path = os.path.join(os.path.abspath("."), "run_molstar.py")
        molstar_process = subprocess.Popen([sys.executable, molstar_path])
    # disable button for 15s
    molstar_button.config(state=DISABLED)
    molstar_button.grid_remove()
    molstar_progress.grid(row=17, column=2, padx=5, pady=10)
    molstar_progress.start(10)
    def check_process():
        if molstar_process.poll() is None:
            root.after(500, check_process)
        else:
            reset_button()
    def reset_button():
        molstar_progress.stop()
        molstar_progress.grid_remove()
        molstar_button.grid(row=17, column=2, padx=5, pady=10)
        molstar_button.config(state=NORMAL)
    check_process()
molstar_button = Button(scrollable_frame, text="Open Mol*Viewer", command=open_molstar)
molstar_button.grid(row=17, column=2, padx=5, pady=10)
molstar_progress = ttk.Progressbar(scrollable_frame, orient=HORIZONTAL, length=100, mode='indeterminate')
molstar_progress.grid_remove()

# button run prediction
def run_button_command():
    global process
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
        global process
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
        finally:
            success = (process and process.returncode == 0)
            stop_loading_animation(success=success) # stop running a task animation
            run_button.config(state="normal") # enable run button
            molstar_button.config(state="normal") # enable run button
            cancel_button.config(state="disabled") # disable terminate button
            process = None
    threading.Thread(target=run_process, daemon=True).start()
run_button = Button(scrollable_frame, text = "run", command = run_button_command)
run_button.grid(row=15, column=2, padx=10, pady=10)

# Buttons hover effect
def make_hover(widget, hover_fg):
    orig_fg = widget.cget("fg")
    def on_enter(e): widget.config(fg=hover_fg)
    def on_leave(e): widget.config(fg=orig_fg)
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)
make_hover(input_button, "#868686")
make_hover(output_button, "#868686")
make_hover(molstar_button, "#4E9BFF")
make_hover(run_button, "#42D23A")
make_hover(cancel_button, "#FF0000")
make_hover(clear_button, "#FFA200")

# Footer
footer = Frame(root)  
footer.grid(row=3, column=2, columnspan=3, sticky="ew")

#Rights
rights_label = Label(
    footer,
    text="© 2025 Spike Murphy Müller from the Institute of Biochemistry and Signal Transduction, University-Medical Center Hamburg Eppendorf",
    font=("Arial", 8),
    fg="white",
    anchor="e",
    justify="right"
)
rights_label.grid(row=0, column=2, sticky="e", padx=10, pady=5)

# Menu
menubar = Menu(root)
root.config(menu=menubar)

# Help Menu
help_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Help", menu=help_menu)
# Version Notes
def show_version_notes():
    notes = """
ShipFold Studio v1.6.0 – 28.09.2025
-----------------------------------
- scrolling changes (no main frame scrolling when in message box)
- scrollbars removed
- new skript for mol*viewer window (run_mostar.py)
- button mol*viewer added
- hover effect for button mol*viewer
- button mol*viewer disabled and replaced with loading bar for 10s when clicked
- main window size changes (90% of screen)
- mol*viewer window size changes (80% of screen)
- main window grid change (centered)

ShipFold Studio v1.5.0 – 28.09.2025
-----------------------------------
- alpha test (unreleased)
- help menu added
- Version notes added
- about added

ShipFold Studio v1.4.0 – 27.09.2025
-----------------------------------
- alpha test (unreleased)
- scrollable main frame added
- rights moved to footer

ShipFold Studio v1.3.0 – 28.09.2025
-----------------------------------
- alpha test (unreleased)
- only numbers function added
- button colors added
- process termination button added
- button hover effect added
- rights added to main window

ShipFold Studio v1.2.0 – 27.09.2025
-----------------------------------
- alpha test (unreleased)
- header added
- logo added
- background added
- tooltips added
- default values added
- running task animation added
- run command added

ShipFold Studio v1.1.0 – 28.09.2025
-----------------------------------
- alpha test (unreleased)

ShipFold Studio v1.0.0 – 27.09.2025
-----------------------------------
- alpha test (unreleased)
"""
    top = Toplevel(root)
    top.title("Version Notes")
    frame = Frame(top)
    frame.pack(fill="both", expand=True, padx=10, pady=10)
    text = Text(frame, wrap="word", height=15)
    scrollbar = Scrollbar(frame, command=text.yview)
    text.config(yscrollcommand=scrollbar.set)
    text.insert("1.0", notes)
    text.config(state="disabled")
    text.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
help_menu.add_command(label="Version Notes", command=show_version_notes)

root.mainloop()

'''
python /Users/spikemurphymuller/ShipFoldGeneration/ShipFoldStudio_v1.6.py
'''