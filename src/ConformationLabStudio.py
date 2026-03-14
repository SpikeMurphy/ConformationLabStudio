# TODO: clear all should also clear status to idle and loading animation
# TODO: add more print statements to see in terminal what happens inside the app
# TODO: load best fitting file into mol* viewer when finished using URL
    # example to load local pdb: http://localhost:8000/?structure-url=myprotein.pdb&structure-url-format=pdb
# TODO: handle failing amber relaxation (see if processes afterwards are stopped, like ranking or generating names according to ranking): 
'''
Traceback (most recent call last):
File "/Users/spikemurphymuller/Library/Application Support/ConfLabEnv/bin/conflab_batch", line 7, in <module>
sys.exit(main())
File "/Users/spikemurphymuller/Library/Application Support/ConfLabEnv/lib/python3.10/site-packages/colabfold/batch.py", line 2031, in main
run(
File "/Users/spikemurphymuller/Library/Application Support/ConfLabEnv/lib/python3.10/site-packages/colabfold/batch.py", line 1569, in run
results = predict_structure(
File "/Users/spikemurphymuller/Library/Application Support/ConfLabEnv/lib/python3.10/site-packages/colabfold/batch.py", line 517, in predict_structure
pdb_lines = relax_me(
File "/Users/spikemurphymuller/Library/Application Support/ConfLabEnv/lib/python3.10/site-packages/colabfold/relax.py", line 30, in relax_me
relaxed_pdb_lines, _, _ = amber_relaxer.process(prot=pdb_obj)
File "/Users/spikemurphymuller/Library/Application Support/ConfLabEnv/lib/python3.10/site-packages/alphafold/relax/relax.py", line 62, in process
out = amber_minimize.run_pipeline(
File "/Users/spikemurphymuller/Library/Application Support/ConfLabEnv/lib/python3.10/site-packages/alphafold/relax/amber_minimize.py", line 476, in run_pipeline
ret = _run_one_iteration(
File "/Users/spikemurphymuller/Library/Application Support/ConfLabEnv/lib/python3.10/site-packages/alphafold/relax/amber_minimize.py", line 420, in _run_one_iteration
raise ValueError(f"Minimization failed after {max_attempts} attempts.")
ValueError: Minimization failed after 100 attempts.
Finished with code 1
Run failed after 1h 13m 49s
'''
# TODO: Update log file, e.g. include batch command, and ranking, remove unnecessary output.
# TODO: Update error handling, reset status update colors (currently remain red)

APP_NAME = "ConformationLab Studio"
APP_VERSION = "1.0.1"
APP_AUTHOR = "Spike Murphy Müller"

### imports ###
# from AppKit import NSScreen
import itertools
from logging import root
import os
from PIL import Image as PILImage, ImageTk as PILImageTk
import platform
import psutil
import subprocess
import sys
import tarfile
from threading import Thread
import time
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar, Notebook
import webbrowser


# =================================================== #
# ===== CLASSES ===================================== #
# =================================================== #

class ToolTip:
    # TODO: redo
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        tw = Toplevel(self.widget)
        tw.withdraw()
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
        label.pack()
        tw.update_idletasks()
        width_info = tw.winfo_reqwidth()
        tw.destroy()
        x = self.widget.winfo_rootx() - width_info
        y = self.widget.winfo_rooty() + self.widget.winfo_height() // 2
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

# =================================================== #
# ===== MAIN ======================================== #
# =================================================== #

def main():
    #===== Process initialization =====# 

    # Set variable process to global
    global process 
    # Initialize global variable process to none for subprocess handling
    process = None

    #===== Initial window setup =====# 

    # Initialize Tkinter application root, make root central GUI object
    root = Tk()
    # Bring window to front and focus
    root.focus_force()
    # Set title (displayed in title bar)
    root.title("ConformationLab Studio")
    configure_grid(root)

    '''
    |                    ROW 0                  | <- header
    |                    ROW 1                  | <- header
    |                    ROW 2                  | <- body
    |                    ROW 3                  | <- footer
    '''

    #===== Central state dictionary =====# 

    # Initialize dictionary to store shared variables objects
    state = {}
    # Get paths for app, environment and conflab binary
    app_dir, env_dir, conflab_bin = get_app_paths()
    # Store root and paths
    state.update({
        'root': root,
        'app_dir': app_dir,
        'env_dir': env_dir,
        'conflab_bin': conflab_bin
    })

    # Create validation commands for input fields
    validation_cmd = create_validation_commands(root)
    # Store validation commands in validation dictionary in state dictionary
    state['validation_cmd'] = validation_cmd

    ''' 
    Dict Structure:

    state
     ├─ root
     ├─ app_dir
     ├─ env_dir
     ├─ conflab_bin
     └─ vcmd_dict
         ├─ vcmd_numbers
         ├─ vcmd_numbers_or_auto
         └─ vcmd_numbers_commas
    '''

    #===== Build User Interface =====# 

    # Create header frame
    header_frame = Frame(root)
    header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=0, padx=10)
    configure_header_frame(header_frame, app_dir)

    '''
    | COLUMN 0 | COLUMN 1 | COLUMN 2 | COLUMN 3 | <- HEADER
    | COLUMN 0 | COLUMN 1 | COLUMN 2 | COLUMN 3 | <- HEADER
    |                   row 2                   | <- body
    |                   row 3                   | <- footer

    ->

    |   LOGO   |  TITLE   | COLUMN 2 | COLUMN 3 | <- LOGO, TITLE
    |   LOGO   | SUBTITLE | COLUMN 2 | COLUMN 3 | <- LOGO, SUBTITLE
    |                   row 2                   | <- body
    |                   row 3                   | <- footer
    '''

    # Create main container (body)
    main_frame = Frame(root)
    main_frame.grid(row=2, column=0, columnspan=3, sticky="nsew")

    '''
    |   logo   |  title   | column 2 | column 3 | <- header
    |   logo   | subtitle | column 2 | column 3 | <- header
    |   COLUMN 0   |   COLUMN 1   |   COLUMN 2  | <- BODY (MAIN_FRAME)
    |                    row 3                  | <- footer
    '''

    #===== Create Scrollable Interface =====# 

    # Create main canvas with scrollbar for body
    main_canvas = Canvas(main_frame, highlightthickness=0)
    main_canvas.pack(side=LEFT, fill=BOTH, expand=True)

    '''
    | xxxxxxxxxxxxxxxxxx row 1 xxxxxxxxxxxxxxxx | <- header
    | xxxxxxxxxxxxxxxxxx row 2 xxxxxxxxxxxxxxxx | <- header
    |                 MAIN CANVAS               | <- MAIN CANVAS
    | xxxxxxxxxxxxxxxxxx row 3 xxxxxxxxxxxxxxxx | <- footer
    '''

    # Create scrollable frame inside canvas
    scrollable_frame = Frame(main_canvas)
    configure_scrollable_frame(scrollable_frame)

    '''
    | xxxxxxxxxxxxxxxxxx row 1 xxxxxxxxxxxxxxxx | <- header
    | xxxxxxxxxxxxxxxxxx row 2 xxxxxxxxxxxxxxxx | <- header
    |               SCROLLABLE FRAME            | <- SCROLLABLE FRAME 
    | xxxxxxxxxxxxxxxxxx row 3 xxxxxxxxxxxxxxxx | <- footer
    
    

    root
    │
    ├── Header Frame
    │
    ├── Main Frame
    │     └── Main Canvas
    │           └── Scrollable Frame
    │                 ├── BASIC widgets
    │                 ├── ADVANCED widgets
    │                 ├── OUTPUT widget
    │                 ├── STATUS widget
    │                 └── LOADING widget
    │
    └── Footer Frame
    '''

    # embed scrollable frame inside the canvas
    window_id = main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    # configure scroll region on frame resizing
    scrollable_frame.bind("<Configure>", lambda e: on_frame_configure(e, main_canvas, window_id))
    # configure scroll region on canvas resizing
    main_canvas.bind("<Configure>", lambda e: on_canvas_configure(e, main_canvas, window_id))
    # configure scrolling with mouse wheel
    root.bind_all("<MouseWheel>", lambda e: on_global_mousewheel(e, root, main_canvas))

    #===== Path selectors & Environment unpacking =====# 

    # Create path selectors for input, output and template paths
    path_selectors = create_path_selectors()

    # Ensure conflab environment is extracted and available
    ensure_conflab_env(app_dir, env_dir)

    #===== Build MODES =====# 

    # build BASCI mode labels, entries, dropdowns and buttons
    basic_widgets = build_basic_mode(scrollable_frame, path_selectors, validation_cmd)
    # append BASCI widget and variables to central storage "state"
    state.update(basic_widgets)
    # build ADVANCED mode labels, entries, dropdowns and buttons
    adv_widgets = build_advanced_mode(scrollable_frame, path_selectors, validation_cmd)
    # append ADVANCED widget and variables to central storage "state"
    state.update(adv_widgets)

    # ADVANCED mode visibility default not visible
    advanced_visible = BooleanVar(value=False)
    # update central storage "state"
    state['advanced_visible'] = advanced_visible
    # create toggle for ADVANCED Mode and keep canvas
    toggle_canvas = advanced_toggle(root, header_frame, state['advanced_frame'], advanced_visible)
    # update central storage "state"
    state['toggle_canvas'] = toggle_canvas
    # initially hide ADVANCED frame if required
    if not advanced_visible.get():
        # update central storage "state"
        state['advanced_frame'].grid_remove()

    #===== Buttons =====# 

    # clear button
    state['clear_button'] = build_clear_button(scrollable_frame, state)

    # cancel button
    state['cancel_button'] = build_cancel_button(scrollable_frame, state)

    # Mol*Viewer button
    state['molstar_button'], state['molstar_progress'] = build_molstar_button(scrollable_frame, state)

    # run button
    state['run_button'] = build_run_button(scrollable_frame, state)

    # Button hover effects
    apply_hover_effect(state)

    # Output text widget
    state['output_text'] = build_output_wiget(scrollable_frame)

    # Status label
    state['status_label'] = build_status_frame(scrollable_frame)

    # Loading animation frame
    state['loading_label'] = build_loading_frame(scrollable_frame)

    # Create footer frame
    footer = Frame(root)
    footer.grid(row=4, column=0, columnspan=3, sticky="ew")
    configure_footer(footer)

    '''
    |   logo   |  title   | column 2 | column 3 | <- header
    |   logo   | subtitle | column 2 | column 3 | <- header
    |   column 0   |   column 1   |   column 2  | <- body
    |   COLUMN 0   |   COLUMN 1   |   COLUMN 2  | <- FOOTER
    '''

    # Shortcuts
    bind_shortcuts(root, state)
    bind_shortcut_overlay(root)

    # Menu bar
    state['menubar'] = build_menubar(root)
    configure_about(state['menubar'], root, app_dir)
    configure_system(state['menubar'], root)
    configure_help(state['menubar'])

    # create main loop
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))
    # update_theme(root) # currently unnecessary, no individual object changes necessary
    root.mainloop()


# =================================================== #
# ===== HELPER FUNCTIONS ============================ #
# =================================================== #

# TODO: create comments according to best practice for all helper functions

def configure_grid(root):
    '''
    Configure root grid with 4 rows and 3 columns

    :param root:    Tkinter root window
    :type root:     Tkinter.Tk

    :raises:        ValueError: If root is not a Tkinter.Tk instance

    :return:        None
    '''
    # Check for valid input
    if not isinstance(root, Tk):
        raise ValueError("root must be a Tkinter.Tk instance")

    # first row: header, fixed height (logo with rowspan 2, title)
    root.grid_rowconfigure(0, weight=0)
    # second row: header, fixed height (logo with rowspan 2, subtitle)
    root.grid_rowconfigure(1, weight=0)
    # third row: body, flexible height
    root.grid_rowconfigure(2, weight=1)
    # fourth row: footer bar, fixed height
    root.grid_rowconfigure(3, weight=0)
    root.grid_columnconfigure(0, weight=1)

    # center window 90%
    scale = get_centered_geometry(0.9)
    root.geometry(scale)


def get_centered_geometry(scale=0.9):
    '''
    Calculate centered window geometry based on screen size and scale.
    
    :param scale:   percent of the screen to use for the window (0-1, default 0.9)
    :type scale:    float

    :raises:        ValueError: If scale is not between 0 and 1
    :raises:        TypeError: If scale is not between an int or a float

    :return:        geometry string in the format "w x h + x + y" for Tkinter
    :rtype:         str
    '''
    # check for valid input
    if not 0 < scale <= 1:
        raise ValueError("scale must be between 0 (not visible) and 1 (full screen)")
    
    try:
        from AppKit import NSScreen
        # Use AppKit to get the visible screen area.
        frame = NSScreen.mainScreen().visibleFrame()
        # Calculate window size
        screen_width = int(frame.size.width)
        screen_height = int(frame.size.height)
    except Exception:
         # Fallback
        tmp_root = Tk()
        tmp_root.withdraw()
        tmp_root.update_idletasks()
        screen_width = tmp_root.winfo_screenwidth()
        screen_height = tmp_root.winfo_screenheight()
        tmp_root.destroy()
    # Adjust window size based on scale
    window_width = int(screen_width * scale)
    window_height = int(screen_height * scale)
    # Calculate x and y position to center window on screen
    window_x = (screen_width - window_width) // 2
    window_y = (screen_height - window_height) // 2
    
    # Return geometry string for Tkinter
    return f"{window_width}x{window_height}+{window_x}+{window_y}"


def get_app_paths():
    '''
    Get application directory paths and environment setup.

    :raises:    FileNotFoundError: If environment archive or conflab binary is not found after extraction
    
    :return:    app path, environment path, and conflab binary path
    :rtype:     tuple of (str, str, str)
    '''
    #===== Get app directory =====# 
    
    # Check if the program is running as a bundled executable (PyInstaller)
    # True → running as packaged app
    if getattr(sys, 'frozen', False):
        # set app directory to temporary folder created by PyInstaller where the bundled files are extracted
        app_dir = sys._MEIPASS
    # False → running as normal python script
    else:
        # set app directory to directory containing the current Python script
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    #===== Get environment directories (archive and extraction) =====# 

    # Get path to the compressed environment archive inside the app directory
    env_archive = os.path.join(app_dir, "conflab_env.tar.gz")
    # Get folder in user's application support directory for environment export
    env_dir = os.path.expanduser("~/Library/Application Support/ConfLabEnv")
    
    #===== Extract environment =====# 

    # Check whether the environment has already been extracted
    if not os.path.exists(os.path.join(env_dir, "bin")):
        # Creates the directory if needed
        os.makedirs(env_dir, exist_ok=True)
        # Check if the compressed environment file exists
        if not os.path.exists(env_archive):
            raise FileNotFoundError("Environment archive not found")
        else:
            # Opens the tar.gz file
            with tarfile.open(env_archive, "r:gz") as tar:
                # Extract the contents of the tar.gz file into the environment application support directory
                tar.extractall(env_dir)
    
    #===== Get binary directory =====# 

    # Get path to the conflab binary within the environment
    conflab_bin = os.path.join(env_dir, "bin", "conflab_batch")
    # Check if environment was successfully unpacked and binary exists
    if not os.path.exists(conflab_bin):
        raise FileNotFoundError("conflab binary not found")
    
    #===== Return paths =====# 
    return app_dir, env_dir, conflab_bin


def create_validation_commands(root):
    '''
    Create validation commands.

    :param root:    Tkinter root window for registering validation commands
    :type root:     Tkinter.Tk
    
    :raises:        ValueError: If root is not a Tkinter.Tk instance

    :return:        validation command tuples for different input types
    :rtype:         dict[str, tuple[Tkinter/Tcl registered function, substitution code]] {
                        'vcmd_numbers': tuple,
                        'vcmd_numbers_or_auto': tuple,
                        'vcmd_numbers_commas': tuple
                    }
    '''
    # Check for valid input
    if not isinstance(root, Tk):
        raise ValueError("root must be a Tkinter.Tk instance")

    #===== Define validation functions =====# 

    def only_numbers(new_value):
        '''
        Validation function to allow only digits in an entry field.
        
        :param new_value:   value of the entry field after the proposed change
        :type new_value:    str

        :raises:            ValueError: If new value is not "" or digits only

        :return:            True if valid, False if invalid
        :rtype:             bool
        '''
        # Check if value is digits only or empty (allow deletion)
        if new_value.isdigit() or new_value == "":
            return True
        else:
            # Upon invalid input, ring bell and reject change
            root.bell()
            return False
    
    def numbers_or_auto(new_value):
        '''
        Validation function to allow only int/float or the string "auto" or an entry field.

        :param new_value:   the new value of the entry field after the proposed change
        :type new_value:    str

        :raises:            ValueError: If new value is not "" or subset of beginning of "auto" and cannot be converted to float
        
        :return:            True if valid, False if invalid
        :rtype:             bool
        '''
        # Check if value is empty (allow deletion) or is subset of beginning of "auto" (case-insensitive)
        if new_value == "" or "auto".startswith(new_value.lower()):
            return True
        else:
            try:
                # Check if input can be converted to a floating point number (is digit or float)
                float(new_value)
                return True
            except ValueError:
                # Upon invalid input, ring bell and reject change
                root.bell()
                return False
    
    def numbers_and_commas(new_value):
        '''
        Validation function to allow only digits and commas in an entry field.

        :param new_value:   the new value of the entry field after the proposed change
        :type new_value:    str

        :raises:            ValueError: If new value is not "" or digits and commas only

        :return:            True if valid, False if invalid
        :rtype:             bool
        '''
        if all(c.isdigit() or c == "," for c in new_value) or new_value == "":
            return True
        else:
            # Upon invalid input, ring bell and reject change
            root.bell()
            return False
    
    #===== Create validation commands =====# 

    # Registers the Python functions with the Tkinter/Tcl interpreter
    vcmd_numbers = (root.register(only_numbers), "%P")
    vcmd_numbers_or_auto = (root.register(numbers_or_auto), "%P")
    vcmd_numbers_commas = (root.register(numbers_and_commas), "%P")
    
    #===== Return validation commands =====# 

    return {
        'vcmd_numbers': vcmd_numbers,
        'vcmd_numbers_or_auto': vcmd_numbers_or_auto,
        'vcmd_numbers_commas': vcmd_numbers_commas
    }


def configure_header_frame(header_frame, app_dir):
    '''
    Configure header frame with logo, title and subtitle.

    :param header_frame:    the frame to configure as header
    :type header_frame:     Tkinter.Frame
    
    :param app_dir:         the application directory to load the logo from
    :type app_dir:          str
    
    :raises:                ValueError: If header_frame is not a Tkinter.Frame instance 
    :raises:                ValueError: If app_dir is not a string
    :raises:                TypeError: If argument missing
    
    :return:                None
    '''
    # Check for valid input
    if not isinstance(header_frame, Frame):
        raise ValueError("header_frame must be a Tkinter.Frame instance")
    if not isinstance(app_dir, str):
        raise ValueError("app_dir must be a string")
    
    # Get logo path
    logo_path = os.path.join(app_dir, "ConformationLabLogo.png")
    if os.path.exists(logo_path):
        # Open, resize and scale logo
        logo_img = PILImage.open(logo_path).resize((100, 100), PILImage.LANCZOS)
        # convert logo to PhotoImage for Tkinter (cannot use pillow image)
        logo_tkinter = PILImageTk.PhotoImage(logo_img)
        # Create label to display image in
        logo_label = Label(header_frame, image=logo_tkinter)
        logo_label.image = logo_tkinter
        # place logo in first two rows of the firs column
        logo_label.grid(row=0, column=0, rowspan=2, padx=10, pady=5)
    
    # Create title and subtitle
    title_frame = Frame(header_frame)
    title_frame.grid(row=0, column=1, sticky="w", padx=10, pady=20)
    title_label = Label(title_frame, text="ConformationLab Studio", font=("Arial", 22, "bold"))
    title_label.grid(row=0, column=0, sticky="w")
    subtitle_label = Label(title_frame, text="Local Protein Structure Prediction for Apple Devices", font=("Arial", 12))
    subtitle_label.grid(row=1, column=0, sticky="w")
    
    # Configure header frame

    # first column: logo, fixed width
    header_frame.columnconfigure(0, weight=0)
    # second column: title and subtitle, expandable
    header_frame.columnconfigure(1, weight=1)
    # third column: empty, fixed width
    header_frame.columnconfigure(2, weight=0)
    # fourth column: empty, fixed width (for toggle button)
    header_frame.columnconfigure(3, weight=0)


def configure_scrollable_frame(scrollable_frame):
    # Configure scrollable frame
    scrollable_frame.grid_columnconfigure(0, weight=1)
    scrollable_frame.grid_columnconfigure(1, weight=1)
    scrollable_frame.grid_columnconfigure(2, weight=1)


def on_frame_configure(event, main_canvas, window_id):
    # scrollregion equal to bounding box of the scrollable frame
    bbox = main_canvas.bbox(window_id)
    if bbox:
        main_canvas.configure(scrollregion=bbox)


def on_canvas_configure(event, main_canvas, window_id):
    # scrollable_frame width equal to canvas width
    main_canvas.itemconfig(window_id, width=event.width)

def on_global_mousewheel(event, root, main_canvas):
    '''
    Handle mouse wheel scrolling for both Text widgets and the main canvas.
    
    :param event:           mouse wheel event
    :type event:            Tkinter.Event
    
    :param root:            root window to check for widget under mouse
    :type root:             Tkinter.Tk
    
    :param main_canvas:     main canvas to scroll if not over a Text widget
    :type main_canvas:      Tkinter.Canvas
    
    :raises:                ValueError: If root is not a Tkinter.Tk instance
    :raises:                ValueError: If main_canvas is not a Tkinter.Canvas instance

    :return:                "break" to indicate event has been handled
    :rtype:                 str 
    '''
    # Check for valid input
    if not isinstance(root, Tk):
        raise ValueError("root must be a Tkinter.Tk instance")
    if not isinstance(main_canvas, Canvas):
        raise ValueError("main_canvas must be a Tkinter.Canvas instance")
    
    # Get current widget mouse is over
    widget = root.winfo_containing(event.x_root, event.y_root)
    # mouse over text widget, scroll individually
    if isinstance(widget, Text):
        # MacOS
        if sys.platform == "darwin":
            widget.yview_scroll(-1 * event.delta, "units")
        # Windows
        else:
            widget.yview_scroll(-1 * (event.delta // 120), "units")
        return "break"
    # mouse over canvas, scroll canvas
    # MacOS
    if sys.platform == "darwin":
        main_canvas.yview_scroll(-1 * event.delta, "units")
    # Windows
    else:
        main_canvas.yview_scroll(-1 * (event.delta // 120), "units")
    return "break"


def create_path_selectors():
    # TODO: understand and redo
    '''
    Create all path selectors for opening selection dialogs for input files, output folders, and template files.
    
    :param:     None

    :raises:    None

    :returns:   Dictionary of StringVar and callback function to open selection dialog
    :rtype:     dict[str, tuple[StringVar, Callable]] {
                    "input": (StringVar, select_input_function),
                    "output": (StringVar, select_input_function),
                    "template": (StringVar, select_input_function)
                } 
    '''
    def create_selector(dialog_type, title):
        '''
        Create single path selector for opening selection dialog for input files, output folders, or template files.
        
        :param dialog_type:     Type of dialog to open ("file" or "directory")
        :type dialog_type:      str

        :param title:           Title displayed in the file selection dialog
        :type title:            str

        :raises:                

        :returns:               Tuple of StringVar and callback function to open selection dialog
        :rtype:                 tuple[StringVar, Callable]

        '''
        # initialize path_var
        path_var = StringVar()
        
        def select_path():
            '''
            Open a file or directory selection dialog and store the selected path in the path variable.

            :param:     None

            :raises:    ValueError, if dialog_type is not a file or a directory

            :returns:   None
            '''
            # Check for valid input
            if dialog_type not in ("file", "directory"):
                raise ValueError(f"Invalid dialog type: {dialog_type}")

            # directory
            if dialog_type == "directory":
                # Select folder
                path = filedialog.askdirectory(title=title)
            # file
            else:
                # Select file
                path = filedialog.askopenfilename(title=title)
            # if a path was created, save in path_var
            if path:
                path_var.set(path)
        
        # Return tuple of StringVar and callback function to open selection dialog
        return path_var, select_path
    
    # Return dictionary of StringVar and callback function to open selection dialogs
    return {
        'input': create_selector("file", "Select input file"),
        'output': create_selector("directory", "Select output folder"),
        'template': create_selector("file", "Select input template file")
    }


def ensure_conflab_env(app_dir, env_dir):
    '''
    Ensure conflab environment is extracted.

    This is already done in the def get_app_paths() function.
    This is a failsafe that runs each time a run is started. 
    #TODO: possibly combine into one, by calling this function at the first execution
    
    :param app_dir:     application directory
    :type app_dir:      str

    :param env_dir:     environment directory
    :type env_dir:      str

    :raises:            FileNotFoundError, if environment in the archive of the application bundle does not exist

    :returns:           path of users application support directory where environment is stored
    :rtype:             str
    '''
    conflab_bin = os.path.join(env_dir, "bin", "conflab_batch")
    if not os.path.exists(conflab_bin):
        env_archive = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(sys.executable)), "conflab_env.tar.gz")
        print(f"INFO: Extracting environment to {env_dir} ...")
        os.makedirs(env_dir, exist_ok=True)
        # Check if the compressed environment file exists
        if not os.path.exists(env_archive):
            raise FileNotFoundError("Environment archive not found")
        else:
            # Opens the tar.gz file
            with tarfile.open(env_archive, "r:gz") as tar:
                # Extract the contents of the tar.gz file into the environment application support directory
                tar.extractall(path=env_dir)
        print("INFO: Environment successfully extracted.")
    return conflab_bin


def build_basic_mode(scrollable_frame, path_selectors, validation_cmd):
    '''
    Build BASIC mode UI

    :param scrollable_frame:    parent frame to place widgets in
    :type scrollable_frame:     Tkinter.Frame

    :param path_selectors:      path selectors for input and outout
    :type path_selectors:       dict[str, tuple[StringVar, Callable]] {
                                    "input": (StringVar, select_input_function),
                                    "output": (StringVar, select_input_function),
                                    "template": (StringVar, select_input_function)
                                }

    :param validation_cmd:      validation command tuples
    :type validation_cmd:       dict[str, tuple[Tkinter/Tcl registered function, substitution code]] {
                                    'vcmd_numbers': tuple,
                                    'vcmd_numbers_or_auto': tuple,
                                    'vcmd_numbers_commas': tuple
                                }     

    :raises:                    KeyError, if key in path_selectors is missing
                                KeyError, if key in validation_cmd is missing
                                AttributeError, if Tkinter object is invalid

    :returns:                   dictionary containing the widgets and control variables
    :rtype:                     dict[str, object]{
                                    'inputpath_selected': inputpath_selected,
                                    'outputpath_selected': outputpath_selected,
                                    'assembly_type_var': assembly_type_var,
                                    'num_seeds_entry': num_seeds_entry,
                                    'random_seeds_entry': random_seeds_entry,
                                    'model_type_var': model_type_var,
                                    'num_recycle_entry': num_recycle_entry,
                                    'recycle_early_stop_tolerance_entry': recycle_early_stop_tolerance_entry,
                                    'max_msa_entry1': max_msa_entry1,
                                    'max_msa_entry2': max_msa_entry2,
                                    'msa_mode_var': msa_mode_var,
                                    'pair_mode_var': pair_mode_var,
                                    'rank_var': rank_var,
                                    'templates_var': templates_var,
                                    'num_relax_entry': num_relax_entry,
                                    'amber_var': amber_var,
                                    'overwrite_existing_results_var': overwrite_existing_results_var,
                                    'zip_var': zip_var,
                                    'input_button': input_button,
                                    'output_button': output_button,
                                    'input_entry': input_entry,
                                    'output_entry': output_entry,
                                }

    '''
    # Create path selectors for inputfile and outputfolder
    inputpath_selected, select_input_path = path_selectors['input']
    outputpath_selected, select_output_path = path_selectors['output']

    # BASIC mode frame
    basic_frame = LabelFrame(scrollable_frame, text="BASIC mode")
    basic_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
    basic_frame.columnconfigure(0, weight=1)
    basic_frame.columnconfigure(1, weight=1)
    basic_frame.columnconfigure(2, weight=1)
    
    # Path selection frame
    path_frame = LabelFrame(basic_frame, text="Path", padx=10, pady=10)
    path_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
    path_frame.columnconfigure(0, weight=1, uniform="inputs")
    path_frame.columnconfigure(1, weight=2, uniform="inputs")
    
    input_label = Label(path_frame, padx=10, text="Input file:")
    input_label.grid(row=0, column=0, sticky="w")
    input_entry = Entry(path_frame, textvariable=inputpath_selected)
    input_entry.grid(row=0, column=1, padx=10, pady=2)
    input_button = Button(path_frame, text="Browse", fg="#000000", command=select_input_path)
    input_button.grid(row=0, column=2)
    
    output_label = Label(path_frame, padx=10, text="Output folder:")
    output_label.grid(row=1, column=0, sticky="w")
    output_entry = Entry(path_frame, textvariable=outputpath_selected)
    output_entry.grid(row=1, column=1, padx=10, pady=2)
    output_button = Button(path_frame, text="Browse", fg="#000000", command=select_output_path)
    output_button.grid(row=1, column=2)
    
    # Assembly frame
    assembly_frame = LabelFrame(basic_frame, text="Path and Assembly", padx=10, pady=10)
    assembly_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
    assembly_frame.columnconfigure(0, weight=1, uniform="inputs")
    assembly_frame.columnconfigure(1, weight=2, uniform="inputs")
    
    assembly_type_label = Label(assembly_frame, padx=10, text="Assembly Type:")
    assembly_type_label.grid(row=1, column=0, sticky="w")
    assembly_type_options = ["monomer", "multimer"]
    assembly_type_var = StringVar(value="monomer")
    assembly_type_dropdown = OptionMenu(assembly_frame, assembly_type_var, *assembly_type_options)
    assembly_type_dropdown.grid(row=1, column=1, padx=10, pady=2)
    assembly_type_info = Label(assembly_frame, text="ⓘ", fg="#007acc", cursor="hand2")
    assembly_type_info.grid(row=1, column=2)
    assembly_type_tooltip = ToolTip(assembly_type_info,
        "Monomer: one amino acid chain or Multimer: multiple amino acid chains")
    
    # Seeds frame
    seeds_frame = LabelFrame(basic_frame, text="Seeds", padx=10, pady=10)
    seeds_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
    seeds_frame.columnconfigure(0, weight=1, uniform="inputs")
    seeds_frame.columnconfigure(1, weight=2, uniform="inputs")
    
    num_seeds_label = Label(seeds_frame, padx=10, text="Number of Seeds:")
    num_seeds_label.grid(row=0, column=0, sticky="w")
    num_seeds_entry = Entry(seeds_frame, validate="key", validatecommand=validation_cmd['vcmd_numbers'])
    num_seeds_entry.grid(row=0, column=1, padx=10, pady=2)
    num_seeds_entry.insert(0, "3")
    num_seeds_info = Label(seeds_frame, text="ⓘ", fg="#007acc", cursor="hand2")
    num_seeds_info.grid(row=0, column=2)
    num_seeds_tooltip = ToolTip(num_seeds_info,
        "Possible entries: Integer ≥ 1. Number of independent predictions. Amount of times the five models are computed. Default=3 -> 3 times 5 models and 3 recycles = 45 cycles total.")
    
    random_seeds_label = Label(seeds_frame, padx=10, text="Random Seeds:")
    random_seeds_label.grid(row=1, column=0, sticky="w")
    random_seeds_entry = Entry(seeds_frame, validate="key", validatecommand=validation_cmd['vcmd_numbers'])
    random_seeds_entry.grid(row=1, column=1, padx=10, pady=2)
    random_seeds_entry.insert(0, "")
    random_seeds_info = Label(seeds_frame, text="ⓘ", fg="#007acc", cursor="hand2")
    random_seeds_info.grid(row=1, column=2)
    random_seeds_tooltip = ToolTip(random_seeds_info,
        "Set a specific random seed for reproducibility. For random-seed=45 and num-seed=3, seeds 45, 46 and 47 will be used. Leave empty for randome seed choice.")
    
    # Model frame
    model_frame = LabelFrame(basic_frame, text="Model", padx=10, pady=10)
    model_frame.grid(row=4, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
    model_frame.columnconfigure(0, weight=1, uniform="inputs")
    model_frame.columnconfigure(1, weight=2, uniform="inputs")
    
    model_type_label = Label(model_frame, padx=10, text="Model:")
    model_type_label.grid(row=0, column=0, sticky="w")
    model_type_options = ["auto", "alphafold2_ptm", "alphafold2_multimer_v1", "alphafold2_multimer_v2", "alphafold2_multimer_v3", "deepfold_v1"]
    model_type_var = StringVar(value="auto")
    model_type_dropdown = OptionMenu(model_frame, model_type_var, *model_type_options)
    model_type_dropdown.grid(row=0, column=1, padx=10, pady=2)
    model_type_info = Label(model_frame, text="ⓘ", fg="#007acc", cursor="hand2")
    model_type_info.grid(row=0, column=2)
    model_type_tooltip = ToolTip(model_type_info,
        "The default is auto. Usually recommended: 'alphafold2_ptm' for single chains and 'alphafold2_multimer_v3' for multiple chains.")
    
    # Recycles frame
    recycles_frame = LabelFrame(basic_frame, text="Recycles", padx=10, pady=10)
    recycles_frame.grid(row=5, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
    recycles_frame.columnconfigure(0, weight=1, uniform="inputs")
    recycles_frame.columnconfigure(1, weight=2, uniform="inputs")
    
    num_recycle_label = Label(recycles_frame, padx=10, text="Number of Recycles:")
    num_recycle_label.grid(row=0, column=0, sticky="w")
    num_recycle_entry = Entry(recycles_frame, validate="key", validatecommand=validation_cmd['vcmd_numbers'])
    num_recycle_entry.grid(row=0, column=1, padx=10, pady=2)
    num_recycle_entry.insert(0, "3")
    num_recycle_info = Label(recycles_frame, text="ⓘ", fg="#007acc", cursor="hand2")
    num_recycle_info.grid(row=0, column=2)
    num_recycle_tooltip = ToolTip(num_recycle_info,
        "Number of times each of the five models is refined. Default=3 -> 3 times 5 models = 15 cycles total.")
    
    recycle_early_stop_tolerance_label = Label(recycles_frame, padx=10, text="Recycles early Stop Tolerance:")
    recycle_early_stop_tolerance_label.grid(row=1, column=0, sticky="w")
    recycle_early_stop_tolerance_entry = Entry(recycles_frame, validate="key", validatecommand=validation_cmd['vcmd_numbers_or_auto'])
    recycle_early_stop_tolerance_entry.grid(row=1, column=1, padx=10, pady=2)
    recycle_early_stop_tolerance_entry.insert(0, "auto")
    recycle_early_stop_tolerance_info = Label(recycles_frame, text="ⓘ", fg="#007acc", cursor="hand2")
    recycle_early_stop_tolerance_info.grid(row=1, column=2)
    recycle_early_stop_tolerance_tooltip = ToolTip(recycle_early_stop_tolerance_info,
        "When the difference between plDDT in successive recycles is below this threshhold the recycle process is stopped. Auto: Default for monomers 0.0, Default for multimers 0.5.")
    
    # MSA frame
    msa_frame = LabelFrame(basic_frame, text="Multi Sequence Alignments", padx=10, pady=10)
    msa_frame.grid(row=6, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
    msa_frame.columnconfigure(0, weight=1, uniform="inputs")
    msa_frame.columnconfigure(1, weight=2, uniform="inputs")
    
    max_msa_label = Label(msa_frame, padx=10, text="Number of Sequences for Multi Sequence Alignment:")
    max_msa_label.grid(row=0, column=0, sticky="w")
    max_msa_frame = Frame(msa_frame)
    max_msa_frame.grid(row=0, column=1, padx=10, pady=2)
    max_msa_entry1 = Entry(max_msa_frame, validate="key", validatecommand=validation_cmd['vcmd_numbers'])
    max_msa_entry1.pack(side=LEFT)
    max_msa_entry1.insert(0, "256")
    max_msa_label_div = Label(max_msa_frame, text=":")
    max_msa_label_div.pack(side=LEFT)
    max_msa_entry2 = Entry(max_msa_frame, validate="key", validatecommand=validation_cmd['vcmd_numbers'])
    max_msa_entry2.pack(side=LEFT)
    max_msa_entry2.insert(0, "256")
    max_msa_info = Label(msa_frame, text="ⓘ", fg="#007acc", cursor="hand2")
    max_msa_info.grid(row=0, column=2)
    max_msa_tooltip = ToolTip(max_msa_info,
        "Number of multi sequence alignments. <unpaired>:<paired>. Number of alignments of single chains and chain pairs.")
    
    msa_mode_label = Label(msa_frame, padx=10, text="MSA Mode:")
    msa_mode_label.grid(row=1, column=0, sticky="w")
    msa_mode_options = ["mmseqs2_uniref_env", "mmseqs2_uniref", "single_sequence"]
    msa_mode_var = StringVar(value="mmseqs2_uniref_env")
    msa_mode_dropdown = OptionMenu(msa_frame, msa_mode_var, *msa_mode_options)
    msa_mode_dropdown.grid(row=1, column=1, padx=10, pady=2)
    msa_mode_info = Label(msa_frame, text="ⓘ", fg="#007acc", cursor="hand2")
    msa_mode_info.grid(row=1, column=2)
    msa_mode_tooltip = ToolTip(msa_mode_info,
        "Default 'mmseqs2_uniref_env' searches for MSA against UniRef databasses and environmental sequences. 'mmseqs2_uniref' searches uniref only for faster runtimes. 'single-sequence' uses no databases and therefor no MSA.")
    
    pair_mode_label = Label(msa_frame, padx=10, text="Pair Mode:")
    pair_mode_label.grid(row=2, column=0, sticky="w")
    pair_mode_options = ["unpaired_paired", "unpaired", "paired"]
    pair_mode_var = StringVar(value="unpaired_paired")
    pair_mode_dropdown = OptionMenu(msa_frame, pair_mode_var, *pair_mode_options)
    pair_mode_dropdown.grid(row=2, column=1, padx=10, pady=2)
    pair_mode_info = Label(msa_frame, text="ⓘ", fg="#007acc", cursor="hand2")
    pair_mode_info.grid(row=2, column=2)
    pair_mode_tooltip = ToolTip(pair_mode_info,
        "Default 'unpaired_paired' which does both. 'unpaired' uses independent alignments only for each chain and 'paired' only uses paired sequences and can be used when complexes are well preserved.")
    
    # Ranking frame
    ranking_frame = LabelFrame(basic_frame, text="Ranking", padx=10, pady=10)
    ranking_frame.grid(row=7, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
    ranking_frame.columnconfigure(0, weight=1, uniform="inputs")
    ranking_frame.columnconfigure(1, weight=2, uniform="inputs")
    
    rank_label = Label(ranking_frame, padx=10, text="Rank:")
    rank_label.grid(row=0, column=0, sticky="w")
    rank_options = ["auto", "plddt", "ptm", "iptm", "multimer"]
    rank_var = StringVar(value="auto")
    rank_dropdown = OptionMenu(ranking_frame, rank_var, *rank_options)
    rank_dropdown.grid(row=0, column=1, padx=10, pady=2)
    rank_info = Label(ranking_frame, text="ⓘ", fg="#007acc", cursor="hand2")
    rank_info.grid(row=0, column=2)
    rank_tooltip = ToolTip(rank_info, "Use 'plddt' for single sequences and 'multimer' for complexes.")
    
    # Templates frame
    templates_frame = LabelFrame(basic_frame, text="Templates", padx=10, pady=10)
    templates_frame.grid(row=8, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
    templates_frame.columnconfigure(0, weight=1, uniform="inputs")
    templates_frame.columnconfigure(1, weight=2, uniform="inputs")
    
    templates_label = Label(templates_frame, padx=10, text="Templates:")
    templates_label.grid(row=0, column=0, sticky="w")
    templates_options = ["Yes", "No"]
    templates_var = StringVar(value="Yes")
    templates_dropdown = OptionMenu(templates_frame, templates_var, *templates_options)
    templates_dropdown.grid(row=0, column=1, padx=10, pady=2)
    templates_info = Label(templates_frame, text="ⓘ", fg="#007acc", cursor="hand2")
    templates_info.grid(row=0, column=2)
    templates_tooltip = ToolTip(templates_info,
        "Used to allow the model to bias against reference sequences from databases.")
    
    # Relaxation frame
    relaxation_frame = LabelFrame(basic_frame, text="Relaxation", padx=10, pady=10)
    relaxation_frame.grid(row=9, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
    relaxation_frame.columnconfigure(0, weight=1, uniform="inputs")
    relaxation_frame.columnconfigure(1, weight=2, uniform="inputs")
    
    amber_label = Label(relaxation_frame, padx=10, text="Relaxation with Amber:")
    amber_label.grid(row=0, column=0, sticky="w")
    amber_options = ["Yes", "No"]
    amber_var = StringVar(value="No")
    amber_dropdown = OptionMenu(relaxation_frame, amber_var, *amber_options)
    amber_dropdown.grid(row=0, column=1, padx=10, pady=2)
    amber_info = Label(relaxation_frame, text="ⓘ", fg="#007acc", cursor="hand2")
    amber_info.grid(row=0, column=2)
    amber_tooltip = ToolTip(amber_info,
        "Used to relax the prediction by running energy minimisation thereby fixing unrealistic bond lengths and angles caused by steric clashes or strained bond geometrics.")
    
    num_relax_label = Label(relaxation_frame, padx=10, text="Number of Relaxes:")
    num_relax_label.grid(row=1, column=0, sticky="w")
    num_relax_entry = Entry(relaxation_frame, validate="key", validatecommand=validation_cmd['vcmd_numbers'])
    num_relax_entry.grid(row=1, column=1, padx=10, pady=2)
    num_relax_entry.insert(0, "0")
    num_relax_info = Label(relaxation_frame, text="ⓘ", fg="#007acc", cursor="hand2")
    num_relax_info.grid(row=1, column=2)
    num_relax_tooltip = ToolTip(num_relax_info, "Number of relaxations with amber.")
    
    # show number of realxes only when amber is selected
    def toggle_num_relax(*args):
        if amber_var.get() == "Yes":
            num_relax_entry.config(state="normal")
        else:
            num_relax_entry.delete(0, END)
            num_relax_entry.insert(0, "0")
            num_relax_entry.config(state="disabled")
    amber_var.trace_add("write", toggle_num_relax)
    toggle_num_relax()

    # Output frame (BASIC)
    output_frame = LabelFrame(basic_frame, text="Output", padx=10, pady=10)
    output_frame.grid(row=10, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
    output_frame.columnconfigure(0, weight=1, uniform="inputs")
    output_frame.columnconfigure(1, weight=2, uniform="inputs")
    
    overwrite_existing_results_label = Label(output_frame, padx=10, text="Overwrite Existing Results:")
    overwrite_existing_results_label.grid(row=6, column=0, sticky="w")
    overwrite_existing_results_options = ["Yes", "No"]
    overwrite_existing_results_var = StringVar(value="No")
    overwrite_existing_results_dropdown = OptionMenu(output_frame, overwrite_existing_results_var, *overwrite_existing_results_options)
    overwrite_existing_results_dropdown.grid(row=6, column=1, padx=10, pady=2)
    overwrite_existing_results_info = Label(output_frame, text="ⓘ", fg="#007acc", cursor="hand2")
    overwrite_existing_results_info.grid(row=6, column=2)
    overwrite_existing_results_tooltip = ToolTip(overwrite_existing_results_info,
        "Choose whether you want a second run to overwrite the old files. Default No.")
    
    zip_label = Label(output_frame, padx=10, text="Pack into ZIP-file:")
    zip_label.grid(row=7, column=0, sticky="w")
    zip_options = ["Yes", "No"]
    zip_var = StringVar(value="Yes")
    zip_dropdown = OptionMenu(output_frame, zip_var, *zip_options)
    zip_dropdown.grid(row=7, column=1, padx=10, pady=2)
    zip_info = Label(output_frame, text="ⓘ", fg="#007acc", cursor="hand2")
    zip_info.grid(row=7, column=2)
    zip_tooltip = ToolTip(zip_info,
        "Choose whether you want the output to be files, then you should choose a prior generated folder, or a ZIP-file. Default Yes")

    # return a dictionary of objects needed elsewhere
    return {
        'inputpath_selected': inputpath_selected,
        'outputpath_selected': outputpath_selected,
        'assembly_type_var': assembly_type_var,
        'num_seeds_entry': num_seeds_entry,
        'random_seeds_entry': random_seeds_entry,
        'model_type_var': model_type_var,
        'num_recycle_entry': num_recycle_entry,
        'recycle_early_stop_tolerance_entry': recycle_early_stop_tolerance_entry,
        'max_msa_entry1': max_msa_entry1,
        'max_msa_entry2': max_msa_entry2,
        'msa_mode_var': msa_mode_var,
        'pair_mode_var': pair_mode_var,
        'rank_var': rank_var,
        'templates_var': templates_var,
        'num_relax_entry': num_relax_entry,
        'amber_var': amber_var,
        'overwrite_existing_results_var': overwrite_existing_results_var,
        'zip_var': zip_var,
        'input_button': input_button,
        'output_button': output_button,
        'input_entry': input_entry,
        'output_entry': output_entry,
    }
    

def build_advanced_mode(scrollable_frame, path_selectors, validation_cmd):
    '''
    Build ADVANCED mode UI

    :param scrollable_frame:    parent frame to place widgets in
    :type scrollable_frame:     Tkinter.Frame

    :param path_selectors:      path selectors for input and outout
    :type path_selectors:       dict[str, tuple[StringVar, Callable]] {
                                    "input": (StringVar, select_input_function),
                                    "output": (StringVar, select_input_function),
                                    "template": (StringVar, select_input_function)
                                }

    :param validation_cmd:      validation command tuples
    :type validation_cmd:       dict[str, tuple[Tkinter/Tcl registered function, substitution code]] {
                                    'vcmd_numbers': tuple,
                                    'vcmd_numbers_or_auto': tuple,
                                    'vcmd_numbers_commas': tuple
                                }     

    :raises:                    KeyError, if key in path_selectors is missing
                                KeyError, if key in validation_cmd is missing
                                AttributeError, if Tkinter object is invalid

    :returns:                   dictionary containing the widgets and control variables
    :rtype:                     dict[str, object]{
                                    'advanced_frame': advanced_frame,
                                    'templatepath_selected': templatepath_selected,
                                    'num_model_entry': num_model_entry,
                                    'model_order_entry': model_order_entry,
                                    'num_ensemble_entry': num_ensemble_entry,
                                    'disable_cluster_profile_var': disable_cluster_profile_var,
                                    'use_dropout_var': use_dropout_var,
                                    'stop_at_score_entry': stop_at_score_entry,
                                    'save_all_var': save_all_var,
                                    'save_recycles_var': save_recycles_var,
                                }
    '''
        
    # path selector for template path
    templatepath_selected, select_template_path = path_selectors['template']

    # ADVANCED mode frame
    advanced_frame = LabelFrame(scrollable_frame, text="ADVANCED mode")
    advanced_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
    advanced_frame.columnconfigure(0, weight=1)
    advanced_frame.columnconfigure(1, weight=1)
    advanced_frame.columnconfigure(2, weight=1)
    advanced_frame.grid_remove()
    
    # Model (Advanced)
    model_advanced_frame = LabelFrame(advanced_frame, text="Model", padx=10, pady=10)
    model_advanced_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
    model_advanced_frame.columnconfigure(0, weight=1, uniform="inputs")
    model_advanced_frame.columnconfigure(1, weight=2, uniform="inputs")
    
    num_model_label = Label(model_advanced_frame, padx=10, text="Number of models:")
    num_model_label.grid(row=0, column=0, sticky="w")
    num_model_entry = Entry(model_advanced_frame, validate="key", validatecommand=validation_cmd['vcmd_numbers'])
    num_model_entry.grid(row=0, column=1, padx=10, pady=2)
    num_model_entry.insert(0, "5")
    num_model_info = Label(model_advanced_frame, text="ⓘ", fg="#007acc", cursor="hand2")
    num_model_info.grid(row=0, column=2)
    num_model_tooltip = ToolTip(num_model_info,
        "Controls how many of the five internal model weights are used. Enter 1 through 5. Default 5, all models.")
    
    model_order_label = Label(model_advanced_frame, padx=10, text="Model order:")
    model_order_label.grid(row=1, column=0, sticky="w")
    model_order_entry = Entry(model_advanced_frame, validate="key", validatecommand=validation_cmd['vcmd_numbers_commas'])
    model_order_entry.grid(row=1, column=1, padx=10, pady=2)
    model_order_entry.insert(0, "1,2,3,4,5")
    model_order_info = Label(model_advanced_frame, text="ⓘ", fg="#007acc", cursor="hand2")
    model_order_info.grid(row=1, column=2)
    model_order_tooltip = ToolTip(model_order_info,
        "Order in which the specified number of models are applied. Enter Permutations of 1 through 'num-models' devided by comma. Default for 5 models 1,2,3,4,5. Enter 0 for default.")
    
    # Ensemble (Advanced)
    ensemble_advanced_frame = LabelFrame(advanced_frame, text="Ensemble", padx=10, pady=10)
    ensemble_advanced_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
    ensemble_advanced_frame.columnconfigure(0, weight=1, uniform="inputs")
    ensemble_advanced_frame.columnconfigure(1, weight=2, uniform="inputs")
    
    num_ensemble_label = Label(ensemble_advanced_frame, padx=10, text="Number of ensembles:")
    num_ensemble_label.grid(row=0, column=0, sticky="w")
    num_ensemble_entry = Entry(ensemble_advanced_frame, validate="key", validatecommand=validation_cmd['vcmd_numbers'])
    num_ensemble_entry.grid(row=0, column=1, padx=10, pady=2)
    num_ensemble_entry.insert(0, "1")
    num_ensemble_info = Label(ensemble_advanced_frame, text="ⓘ", fg="#007acc", cursor="hand2")
    num_ensemble_info.grid(row=0, column=2)
    num_ensemble_tooltip = ToolTip(num_ensemble_info,
        "Number of ensemble predictions per model, default: 1 (no extra ensembles), use >1 only if instability is suspected.")
    
    # Cluster (Advanced)
    cluster_advanced_frame = LabelFrame(advanced_frame, text="Cluster", padx=10, pady=10)
    cluster_advanced_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
    cluster_advanced_frame.columnconfigure(0, weight=1, uniform="inputs")
    cluster_advanced_frame.columnconfigure(1, weight=2, uniform="inputs")
    
    disable_cluster_profile_label = Label(cluster_advanced_frame, padx=10, text="Disable cluster profile:")
    disable_cluster_profile_label.grid(row=0, column=0, sticky="w")
    disable_cluster_profile_options = ["Yes", "No"]
    disable_cluster_profile_var = StringVar(value="Yes")
    disable_cluster_profile_dropdown = OptionMenu(cluster_advanced_frame, disable_cluster_profile_var, *disable_cluster_profile_options)
    disable_cluster_profile_dropdown.grid(row=0, column=1, padx=10, pady=2)
    disable_cluster_profile_info = Label(cluster_advanced_frame, text="ⓘ", fg="#007acc", cursor="hand2")
    disable_cluster_profile_info.grid(row=0, column=2)
    disable_cluster_profile_tooltip = ToolTip(disable_cluster_profile_info,
        "Turns off cluster profile in MSA. Default off, turn on when working with very shallow alignments.")
    
    # Template (Advanced)
    template_advanced_frame = LabelFrame(advanced_frame, text="Template", padx=10, pady=10)
    template_advanced_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
    template_advanced_frame.columnconfigure(0, weight=1, uniform="inputs")
    template_advanced_frame.columnconfigure(1, weight=2, uniform="inputs")
    
    templatepath_label = Label(template_advanced_frame, padx=10, text="Input template file:")
    templatepath_label.grid(row=0, column=0, sticky="w")
    templatepath_entry = Entry(template_advanced_frame, textvariable=templatepath_selected)
    templatepath_entry.grid(row=0, column=1, padx=10, pady=2)
    templatepath_button = Button(template_advanced_frame, text="Browse", fg="#000000", command=select_template_path)
    templatepath_button.grid(row=0, column=2)
    
    # Output (Advanced)
    output_advanced_frame = LabelFrame(advanced_frame, text="Output", padx=10, pady=10)
    output_advanced_frame.grid(row=4, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
    output_advanced_frame.columnconfigure(0, weight=1, uniform="inputs")
    output_advanced_frame.columnconfigure(1, weight=2, uniform="inputs")
    
    use_dropout_label = Label(output_advanced_frame, padx=10, text="Use dropout:")
    use_dropout_label.grid(row=0, column=0, sticky="w")
    use_dropout_options = ["Yes", "No"]
    use_dropout_var = StringVar(value="No")
    use_dropout_dropdown = OptionMenu(output_advanced_frame, use_dropout_var, *use_dropout_options)
    use_dropout_dropdown.grid(row=0, column=1, padx=10, pady=2)
    use_dropout_info = Label(output_advanced_frame, text="ⓘ", fg="#007acc", cursor="hand2")
    use_dropout_info.grid(row=0, column=2)
    use_dropout_tooltip = ToolTip(use_dropout_info,
        "Activates dropout during inference and thereby estimates uncertainty, Default No, turn on for uncertainty analysis.")
    
    stop_at_score_label = Label(output_advanced_frame, padx=10, text="Stop at score:")
    stop_at_score_label.grid(row=1, column=0, sticky="w")
    stop_at_score_entry = Entry(output_advanced_frame, validate="key", validatecommand=validation_cmd['vcmd_numbers'])
    stop_at_score_entry.grid(row=1, column=1, padx=10, pady=2)
    stop_at_score_entry.insert(0, "")
    stop_at_score_info = Label(output_advanced_frame, text="ⓘ", fg="#007acc", cursor="hand2")
    stop_at_score_info.grid(row=1, column=2)
    stop_at_score_tooltip = ToolTip(stop_at_score_info,
        "Stops once a model reaches the specified confidence threshold (pLDDT or PTM). Enter an integer 0–100. Default = none or 100. Lower values (e.g., 85–90) can reduce runtime.")
    
    save_all_label = Label(output_advanced_frame, padx=10, text="Save all:")
    save_all_label.grid(row=2, column=0, sticky="w")
    save_all_options = ["Yes", "No"]
    save_all_var = StringVar(value="No")
    save_all_dropdown = OptionMenu(output_advanced_frame, save_all_var, *save_all_options)
    save_all_dropdown.grid(row=2, column=1, padx=10, pady=2)
    save_all_info = Label(output_advanced_frame, text="ⓘ", fg="#007acc", cursor="hand2")
    save_all_info.grid(row=2, column=2)
    save_all_tooltip = ToolTip(save_all_info,
        "Saves extra intermediate outputs. Default No, can be used for deep analysis.")
    
    save_recycles_label = Label(output_advanced_frame, padx=10, text="Save recycles:")
    save_recycles_label.grid(row=3, column=0, sticky="w")
    save_recycles_options = ["Yes", "No"]
    save_recycles_var = StringVar(value="No")
    save_recycles_dropdown = OptionMenu(output_advanced_frame, save_recycles_var, *save_recycles_options)
    save_recycles_dropdown.grid(row=3, column=1, padx=10, pady=2)
    save_recycles_info = Label(output_advanced_frame, text="ⓘ", fg="#007acc", cursor="hand2")
    save_recycles_info.grid(row=3, column=2)
    save_recycles_tooltip = ToolTip(save_recycles_info,
        "Saves all recycle states instead of only the final. Default no, can be used for analysis of convergence.")

    # return dict for adv widgets
    return {
        'advanced_frame': advanced_frame,
        'templatepath_selected': templatepath_selected,
        'num_model_entry': num_model_entry,
        'model_order_entry': model_order_entry,
        'num_ensemble_entry': num_ensemble_entry,
        'disable_cluster_profile_var': disable_cluster_profile_var,
        'use_dropout_var': use_dropout_var,
        'stop_at_score_entry': stop_at_score_entry,
        'save_all_var': save_all_var,
        'save_recycles_var': save_recycles_var,
    }


def advanced_toggle(root, header_frame, advanced_frame, advanced_visible):
    '''
    Create ADVANCED mode toggle switch in the header

    :param root:                root
    :type root:                 Trinter.Tk

    :param header_frame:        parent frame to place widgets in
    :type header_frame:         Tkinter.Frame

    :param advanced_frame:      frame to be toggeled
    :type advanced_frame:       Tkinter.Frame

    :param advanced_visible:    variable to track visibility of ADVANCED frame
    :type advanced_visible:     bool

    :raises:                    None         

    :returns:                   toggle for advanced mode
    :rtype:                     Tkinter.Canvas
    '''
    # Create container frame
    advanced_toggle_frame = LabelFrame(header_frame, text="ADVANCED Mode", padx=10, pady=10)
    advanced_toggle_frame.grid(row=0, column=3, sticky="e", padx=10, pady=5)
    
    # Creates the toggles canvas
    toggle_canvas = Canvas(advanced_toggle_frame, width=60, height=30,
                           bg=root.cget("bg"), highlightthickness=0)
    toggle_canvas.grid(row=0, column=2, pady=10, sticky="e")

    def draw():
        '''Builds the ADVANCED mode toggle switch'''
        # Removes all shapes currently drawn
        toggle_canvas.delete("all")
        # Build Toggle visual for ADVANCED mode visible
        if advanced_visible.get():
            toggle_canvas.create_oval(5, 5, 25, 25, fill="#4CAF50", width=0)
            toggle_canvas.create_oval(35, 5, 55, 25, fill="#4CAF50", width=0)
            toggle_canvas.create_rectangle(15, 5, 45, 25, fill="#4CAF50", width=0)
            toggle_canvas.create_oval(35, 5, 55, 25, fill="white", width=0)
        # Build Toggle visual for ADVANCED mode invisible
        else:
            toggle_canvas.create_oval(5, 5, 25, 25, fill="#AAAAAA", width=0)
            toggle_canvas.create_oval(35, 5, 55, 25, fill="#AAAAAA", width=0)
            toggle_canvas.create_rectangle(15, 5, 45, 25, fill="#AAAAAA", width=0)
            toggle_canvas.create_oval(5, 5, 25, 25, fill="#FFFFFF", width=0)

    # define toggle action
    def toggle(event=None):
        '''Defines action of the ADVANCED mode toggle switch'''
        # Read current state and set opposite state
        advanced_visible.set(not advanced_visible.get())
        # toggle advanced frame
        draw()
        if advanced_visible.get():
            advanced_frame.grid()
        else:
            advanced_frame.grid_remove()
        # Print state to command line
        print("Advanced mode:", advanced_visible.get())

    # Detect on toggle_canvas: "left mouse click" -> toggle()
    toggle_canvas.bind("<Button-1>", toggle)
    # Detect on root: "control + a" -> toggle()
    root.bind("<Control-a>", toggle)
    draw()
    return toggle_canvas


def build_clear_button(scrollable_frame, state):
    '''Create and return the clear button'''
    clear_button = Button(scrollable_frame, text="clear all",
                          command=lambda: clear_button_command(state))
    clear_button.grid(row=11, column=1, padx=10, pady=10)
    return clear_button


def clear_button_command(state):
    '''Clears all input fields to default values'''
    state['inputpath_selected'].set("")
    state['outputpath_selected'].set("")
    state['assembly_type_var'].set("monomer")
    state['num_seeds_entry'].delete(0, END)
    state['num_seeds_entry'].insert(0, "3")
    state['random_seeds_entry'].delete(0, END)
    state['model_type_var'].set("auto")
    state['num_recycle_entry'].delete(0, END)
    state['num_recycle_entry'].insert(0, "3")
    state['recycle_early_stop_tolerance_entry'].delete(0, END)
    state['recycle_early_stop_tolerance_entry'].insert(0, "auto")
    state['max_msa_entry1'].delete(0, END)
    state['max_msa_entry1'].insert(0, "256")
    state['max_msa_entry2'].delete(0, END)
    state['max_msa_entry2'].insert(0, "256")
    state['msa_mode_var'].set("mmseqs2_uniref_env")
    state['pair_mode_var'].set("unpaired_paired")
    state['rank_var'].set("auto")
    state['templates_var'].set("Yes")
    state['num_relax_entry'].delete(0, END)
    state['num_relax_entry'].insert(0, "0")
    state['amber_var'].set("No")
    state['overwrite_existing_results_var'].set("No")
    state['zip_var'].set("Yes")
    state['num_model_entry'].delete(0, END)
    state['num_model_entry'].insert(0, "5")
    try:
        num_models = int(state['num_model_entry'].get())
        default_model_order = ",".join(str(i) for i in range(1, num_models + 1))
    except ValueError:
        default_model_order = "1,2,3,4,5"
    state['model_order_entry'].delete(0, END)
    state['model_order_entry'].insert(0, default_model_order)
    state['num_ensemble_entry'].delete(0, END)
    state['num_ensemble_entry'].insert(0, "1")
    state['disable_cluster_profile_var'].set("Yes")
    state['templatepath_selected'].set("")
    state['use_dropout_var'].set("No")
    state['stop_at_score_entry'].delete(0, END)
    state['stop_at_score_entry'].insert(0, "")
    state['save_all_var'].set("No")
    state['save_recycles_var'].set("No")
    state['output_text'].config(state="normal")
    state['output_text'].delete("1.0", END)
    state['output_text'].config(state="disabled")


def build_cancel_button(scrollable_frame, state):
    '''Build Cancel Button'''
    cancel_button = Button(scrollable_frame, text="cancel",
                           command=lambda: cancel_process(state), state="disabled")
    cancel_button.grid(row=13, column=1, padx=5, pady=10)
    return cancel_button   


def cancel_process(state):
    '''Cancels the subprocess (protein prediction)'''
    # define process as global variable
    global process
    # Check if a process exists and it is still running
    if process and process.poll() is None:
        # Stop subprocess
        process.terminate()
        # Message to GUI output panel, error=True -> fg=red
        write_output(state['output_text'], "INFO: Process terminated by user.", error=True)
        # Stop the loading animation
        stop_loading_animation(state['loading_label'], success=False)
        # Enable run button
        state['run_button'].config(state="normal")
        # Disable cancel button
        state['cancel_button'].config(state="disabled")


def build_molstar_button(scrollable_frame, state):
    '''Build Mol* Viewer Button and Progress Bar'''
    molstar_button = Button(scrollable_frame, text="Open Mol*Viewer", command=lambda: molstar_button_command(state))
    molstar_button.grid(row=13, column=2, padx=5, pady=10)

    molstar_progress = Progressbar(scrollable_frame, orient=HORIZONTAL, length=100, mode='indeterminate')
    molstar_progress.grid_remove()

    return molstar_button, molstar_progress


def molstar_button_command(state):
    '''
    Launch Mol* viewer and update the button as well as the progress bar.

    '''
    molstar_button = state['molstar_button']
    molstar_progress = state['molstar_progress']

    # Check if the program was packaged with PyInstaller (sys.frozen only in bundeled executable)
    if getattr(sys, "frozen", False):
        # Get path of assisting script in bundel
        molstar_path = os.path.join(os.path.dirname(sys.executable), "run_molstar_v1.0")
        try:
            # Try executing assisting script
            molstar_process = subprocess.Popen([molstar_path])
        except FileNotFoundError:
            write_output(state["output_text"], "Mol* viewer not found", error=True)
            messagebox.showerror("FileNotFoundError: ", f"Failed to launch Mol* viewer.")
            return
    else:
        # Get path when running as script
        molstar_path = os.path.join(os.path.abspath("."), "run_molstar_v1.0.py")
        try:
            # Try executing assisting script
            molstar_process = subprocess.Popen([sys.executable, molstar_path])
        except FileNotFoundError:
            write_output(state["output_text"], "Mol* viewer not found", error=True)
            messagebox.showerror("FileNotFoundError: ", f"Failed to launch Mol* viewer.")
            return

    # To account for opening time so user doesent repeatedly click button, disable and remove butten after click   
    molstar_button.config(state=DISABLED)
    molstar_button.grid_remove()
    # To show user the window is loading, include progress bar
    molstar_progress.grid(row=13, column=2, padx=5, pady=10)
    molstar_progress.start(10)
    
    def check_process():
        '''Check Mol* viewer subprocess.'''
        if molstar_process.poll() is None:
            # Check every 500 ms if subprocess is still running
            state['root'].after(500, check_process)
        else:
            # Reset button and progressbar
            reset_button()
    
    def reset_button():
        '''Reset Mol* viewer button and progress bar.'''
        molstar_progress.stop()
        molstar_progress.grid_remove()
        molstar_button.grid(row=13, column=2, padx=5, pady=10)
        molstar_button.config(state=NORMAL)
    
    check_process()


def build_run_button(scrollable_frame, state):
    '''Builds run button'''
    run_button = Button(scrollable_frame, text="run", command=lambda: run_button_command(state))
    run_button.grid(row=11, column=2, padx=10, pady=10)
    return run_button


def safe_status_update(status_label, text, color=None):
    '''Safely update status label from any thread.'''
    text = str(text)
    
    if color:
        # When colour is passed in update status to text with color
        status_label.config(text=text, foreground=color)
    else:
        # When colour is not passed in update status to text with color=None
        status_label.config(text=text)


def write_output(output_text, message, error=False):
    '''Write message to output text widget.'''
    # Initialize output field to normal
    output_text.config(state="normal")

    if error:
        # When error is passed in print Errormessage in output field
        output_text.insert("end", "ERROR: " + message + "\n", "error")
        output_text.tag_config("error", foreground="red")
    else:
        # When error is not passed in print end to indicate end of subprocess
        output_text.insert("end", message + "\n")

    output_text.see("end")
    output_text.config(state="disabled")


def run_button_command(state):
    '''
    Build protein structure prediction command and execute thread.
    
    :param state:   Central collection of variables, including from the input fields
    :type state:    dict

    :raises:        None

    :returns:       None
    '''
    # Define process variable as global
    global process

    # Ensure the conflab binary ecists and is unpacked
    conflab_bin_path = ensure_conflab_env(state['app_dir'], state['env_dir'])
    if not os.path.exists(conflab_bin_path):
        write_output(state['output_text'], f"FATAL ERROR: conflab_batch not found at {conflab_bin_path}", error=True)
        messagebox.showerror("FileNotFoundError: ", f"conflab_batch executable not found at {conflab_bin_path}."
        )
        return

    # Get Paths
    inputpath = state['inputpath_selected'].get()
    outputpath = state['outputpath_selected'].get()

    # Promt user for input and output field if not selected
    if not inputpath or not outputpath:
        messagebox.showerror("Error: ", "Please select input and output paths")
        return

    # Gather BASIC variables for batch command
    num_relax = state['num_relax_entry'].get().strip() or "0"
    num_recycle = state['num_recycle_entry'].get().strip() or "3"
    recycle_early_stop_tolerance = state['recycle_early_stop_tolerance_entry'].get().strip().lower()
    if recycle_early_stop_tolerance == "auto":
        if state['assembly_type_var'].get() == "multimer":
            recycle_early_stop_tolerance = 0.5
        else:
            recycle_early_stop_tolerance = 0.0
    else:
        recycle_early_stop_tolerance = float(recycle_early_stop_tolerance)
    num_seeds = state['num_seeds_entry'].get().strip() or "3"
    random_seeds = state['random_seeds_entry'].get()
    max_msa = state['max_msa_entry1'].get() + ":" + state['max_msa_entry2'].get()
    model_type = state['model_type_var'].get()
    pair_mode = state['pair_mode_var'].get()
    msa_mode = state['msa_mode_var'].get()
    rank = state['rank_var'].get()
    templates = state['templates_var'].get()
    amber = state['amber_var'].get()
    overwrite_existing_results = state['overwrite_existing_results_var'].get()
    zip_choice = state['zip_var'].get()

    # Gather ADVANCED variables for batch command
    num_model = state['num_model_entry'].get()
    model_order = state['model_order_entry'].get()
    num_ensemble = state['num_ensemble_entry'].get()
    disable_cluster_profile = state['disable_cluster_profile_var'].get()
    templatepath = state['templatepath_selected'].get()
    use_dropout = state['use_dropout_var'].get()
    stop_at_score = state['stop_at_score_entry'].get()
    save_all = state['save_all_var'].get()
    save_recycles = state['save_recycles_var'].get()

    # build batch command
    prediction_command = [
        conflab_bin_path, inputpath, outputpath,
        "--num-seeds", str(num_seeds),
        "--model-type", model_type,
        "--num-recycle", str(num_recycle),
        "--recycle-early-stop-tolerance", str(recycle_early_stop_tolerance),
        "--msa-mode", msa_mode,
        "--max-msa", str(max_msa),
        "--pair-mode", pair_mode,
        "--rank", rank,
        "--num-relax", str(num_relax),
        "--num-model", str(num_model),
        "--num-ensemble", str(num_ensemble),
    ]

    if state['random_seeds_entry'].get().strip() != "":
        prediction_command.extend(["--random-seed", state['random_seeds_entry'].get().strip()])
    if templates == "Yes":
        prediction_command.append("--templates")
    if amber == "Yes":
        prediction_command.append("--amber")
    if overwrite_existing_results == "Yes":
        prediction_command.append("--overwrite-existing-results")
    if zip_choice == "Yes":
        prediction_command.append("--zip")
    if stop_at_score.strip() != "":
        prediction_command.extend(["--stop-at-score", str(stop_at_score.strip())])
    if model_order.strip() != "0" and model_order.strip() != "":
        prediction_command.extend(["--model-order", str(model_order.strip())])
    if disable_cluster_profile == "Yes":
        prediction_command.append("--disable-cluster-profile")
    if use_dropout == "Yes":
        prediction_command.append("--use-dropout")
    if save_all == "Yes":
        prediction_command.append("--save-all")
    if save_recycles == "Yes":
        prediction_command.append("--save-recycles")
    if templates == "Yes" and templatepath:
        prediction_command.extend(["--custom-template-path", templatepath])

    # store prediction batch command for worker thread
    state['prediction_command'] = prediction_command

    # User feedback in output field
    write_output(state['output_text'], "Running command: " + " ".join(prediction_command))
    safe_status_update(state['status_label'], "Starting prediction...")
    
    # start loading animation
    start_loading_animation(state['loading_label'])

    # Disable run button
    state['run_button'].config(state="disabled")
    # Enable cancel button
    state['cancel_button'].config(state="normal")

    # Start thread
    Thread(target=run_process, args=(state,), daemon=True).start()

def run_process(state):
    '''
    Run protein structure prediction.
    
    :param state:   Central collection of variables, including from the input fields
    :type state:    dict

    :raises:        None

    :returns:       None
    '''

    # Define process variable as global
    global process

    try:
        # Record start time for runtime calculation
        start_time = time.time()
        # Copy current system environment
        env = os.environ.copy()
        # Ensure programs in this environment are found first
        env["PATH"] = os.path.join(state['env_dir'], "bin") + os.pathsep + env["PATH"]
        # Ensure shared libraries can be found
        env["LD_LIBRARY_PATH"] = os.path.join(state['env_dir'], "lib") + os.pathsep + env.get("LD_LIBRARY_PATH", "")
        # Disable buffering and ensure the subprocess prints output immediately
        env["PYTHONUNBUFFERED"] = "1"
        # start process
        process = subprocess.Popen(
            # -i  prevent idle sleep; -m  prevent disk sleep; -s  prevent system sleep; -u  simulate user activity
            # start prediction command
            ["caffeinate", "-i", "-m", "-s", "-u"] + state['prediction_command'],
            # Capture program output to appear in GUI output field
            stdout=subprocess.PIPE,
            # Redirect errors into stdout to appear in GUI output field
            stderr=subprocess.STDOUT,
            # Treat output as strings
            text=True,
            env=env
        )
        # print output to output field and transfer information to status update
        for line in process.stdout:
            if line.strip():
                write_output(state['output_text'], line.strip())
                low = line.lower()
                if "setting max_seq" in low:
                    safe_status_update(state['status_label'], "Running Multiple Sequence Alignment...", color="#00FFC3")
                elif "model_1" in low:
                    safe_status_update(state['status_label'], "Predicting with Model 1...", color="#D2ADFF")
                elif "model_2" in low:
                    safe_status_update(state['status_label'], "Predicting with Model 2...", color="#B67BFF")
                elif "model_3" in low:
                    safe_status_update(state['status_label'], "Predicting with Model 3...", color="#9C4AFF")
                elif "model_4" in low:
                    safe_status_update(state['status_label'], "Predicting with Model 4...", color="#8521FF")
                elif "model_5" in low:
                    safe_status_update(state['status_label'], "Predicting with Model 5...", color="#7300FF")
                elif "relax" in low:
                    safe_status_update(state['status_label'], "Relaxation step...")
                elif "finished" in low or "done" in low:
                    safe_status_update(state['status_label'], "✅ Finished", color="green")
        # Wait until subprocess is finished
        process.wait()
        # Print message in output field
        write_output(state['output_text'], f"Finished with code {process.returncode}")
    except Exception as e:
        write_output(state['output_text'], f"FATAL ERROR: {e}", error=True)
    finally:
        # Record end time for runtime calculation
        end_time = time.time()
        # Perform runtime calculation
        elapsed = int(end_time - start_time)
        hours = elapsed // 3600
        minutes = (elapsed % 3600) // 60
        seconds = elapsed % 60
        elapsed_str = f"{hours}h {minutes}m {seconds}s"
        success = (process and process.returncode == 0)
        # stop loading animation
        stop_loading_animation(state['loading_label'], success=success)
        # Enable run button
        state['run_button'].config(state="normal")
        # Mol* viewer button to normal (should not change)
        state['molstar_button'].config(state="normal")
        # Disable cencel button
        state['cancel_button'].config(state="disabled")
        # Print status update
        if process and process.returncode == 0:
            safe_status_update(state['status_label'], f"✅ Completed successfully in {elapsed_str}", color="green")
            write_output(state['output_text'], f"Run completed successfully in {elapsed_str}")
        else:
            safe_status_update(state['status_label'], f"❌ Failed after {elapsed_str}", color="red")
            write_output(state['output_text'], f"Run failed after {elapsed_str}")
        
        # reset process to None
        process = None


def start_loading_animation(loading_label):
    '''Defines and starts loading animation.'''
    # Create the animation
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
    loading_label.loading_animation_running = True

    # Define animate function
    def animate():
        # If animation running is True cycle trough lines every 500 ms
        if hasattr(loading_label, 'loading_animation_running') and loading_label.loading_animation_running:
            loading_label.config(text=next(spinner))
            loading_label.after(500, animate)

    # Start animate function
    animate()


def stop_loading_animation(loading_label, success=True):
    '''Stops loading animation.'''
    # Set animation running to False
    loading_label.loading_animation_running = False
    # Update the loading label
    if success:
        loading_label.config(text="✅ Finished", fg="green")
    else:
        loading_label.config(text="❌ Error", fg="red")


def apply_hover_effect(state):
    '''Applys hover effects to buttons with color'''
    hover_effect(state['input_button'], "#868686")
    hover_effect(state['output_button'], "#868686")
    hover_effect(state['molstar_button'], "#4E9BFF")
    hover_effect(state['run_button'], "#42D23A")
    hover_effect(state['cancel_button'], "#FF0000")
    hover_effect(state['clear_button'], "#FFA200")
    

def hover_effect(widget, hover_fg):
    '''Defines hover effects'''
    # Get original button foreground
    orig_fg = widget.cget("fg")
    # Update foreground on mouse enter
    def on_enter(e):
        widget.config(fg=hover_fg)
    # Update foreground to default on mouse leave
    def on_leave(e):
        widget.config(fg=orig_fg)
    # Bind the mouse enter or leave event to the function on_enter on_leave. 
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)


def build_output_wiget(scrollable_frame):
    '''Builds output field for feedback from batch command and error messages.'''
    output_text = Text(scrollable_frame, wrap="word", height=15, state="disabled")
    output_text.grid(row=12, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
    return output_text


def build_status_frame(scrollable_frame):
    '''Builds status frame and label for additional easyer to comprehend status update alongside output field.'''
    status_frame = LabelFrame(scrollable_frame, text="Status", padx=10, pady=10)
    status_frame.grid(row=11, column=0, padx=10, pady=10, sticky="w")
    status_label = Label(status_frame, text="Idle", width=30, anchor="w", padx=20)
    status_label.pack(fill="x")
    return status_label


def build_loading_frame(scrollable_frame):
    '''Builds frame and label for the loading animation'''
    loading_frame = LabelFrame(scrollable_frame, width=30, text="Status", padx=10, pady=10)
    loading_frame.grid(row=13, column=0, padx=10, pady=10, sticky="w")
    loading_label = Label(loading_frame, width=30, anchor="w", padx=20)
    loading_label.pack(fill="x")
    # Initialize loading animation off
    loading_label.loading_animation_running = False
    return loading_label


def configure_footer(footer):
    '''Configures footer'''
    footer.grid_columnconfigure(0, weight=1)
    footer.grid_columnconfigure(1, weight=1)
    footer.grid_columnconfigure(2, weight=1)
    
    rights_label = Label(
        footer,
        text="© 2025 Spike Murphy Müller, MIT License, Distributed by Murphy Biochemistry UG (haftungsbeschränkt), Hamburg, Germany",
        font=("Arial", 12),
        fg="#555555",
        anchor="w",
        justify="right"
    )
    rights_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)


# =================================================== #
# ===== SHORTCUTS =================================== #
# =================================================== #


def bind_shortcuts(root, state):
    '''Bind application keyboard shortcuts.'''

    # On keyboard event, execute function
    root.bind_all("<Control-i>", lambda e: shortcut_browse_input(state))
    root.bind_all("<Control-o>", lambda e: shortcut_browse_output(state))

    root.bind_all("<Control-a>", lambda e: shortcut_toggle_advanced(state))

    root.bind_all("<Control-r>", lambda e: shortcut_run(state))
    root.bind_all("<Control-c>", lambda e: shortcut_cancel(state))
    root.bind_all("<Control-n>", lambda e: shortcut_clear(state))

    root.bind_all("<Control-v>", lambda e: shortcut_molviewer(state))

def shortcut_browse_input(state):
    '''Trigger browse input button.'''
    state["input_button"].invoke()


def shortcut_browse_output(state):
    '''Trigger browse output button.'''
    state["output_button"].invoke()


def shortcut_toggle_advanced(state):
    '''Toggle advanced mode.'''
    # Toggle ADVANCED visibility variable to opposite
    state["advanced_visible"].set(not state["advanced_visible"].get())

    # If advanced_visible is True
    if state["advanced_visible"].get():
        # Place ADVANCED frame on grid
        state["advanced_frame"].grid()
    else:
        # Remove ADVANCED frame on grid
        state["advanced_frame"].grid_remove()


def shortcut_run(state):
    '''Trigger start run button.'''
    state["run_button"].invoke()


def shortcut_cancel(state):
    '''Trigger cancel run button'''
    state["cancel_button"].invoke()


def shortcut_clear(state):
    '''Trigger clear fields button.'''
    state["clear_button"].invoke()


def shortcut_molviewer(state):
    '''Trigger start Mol* viewer button.'''
    state["molstar_button"].invoke()

def create_shortcut_overlay(root):
    '''Create overlay window showing shortcuts.'''
    # Create overlay window
    overlay = Toplevel(root)
    # Initially hide overlay
    overlay.withdraw()
    # Remove window decorations
    overlay.overrideredirect(True)
    overlay.attributes("-alpha", 0.9)
    # Attatch to main window (always on top)
    overlay.transient(root)
    overlay.configure(bg="black")
    # place centered with screenfill 40%
    overlay.geometry(get_centered_geometry(0.4))

    # create frame
    container = Frame(overlay, bg="black")
    container.pack(expand=True, padx=25, pady=25)

    # Create title
    title = Label(
        container,
        text="Keyboard Shortcuts",
        fg="white",
        bg="black",
        font=("Helvetica", 16, "bold")
    )
    title.grid(row=0, column=0, columnspan=2, pady=(0, 15))
    
    # Create list of shortcuts
    shortcuts = [
        ("Ctrl + I", "Browse Input"),
        ("Ctrl + O", "Browse Output"),
        ("Ctrl + A", "Toggle Advanced"),
        ("Ctrl + N", "Start New with Cleared Fields"),
        ("Ctrl + R", "Start Run"),
        ("Ctrl + C", "Cancel Run"),
        ("Ctrl + V", "Start Mol* Viewer"),
        ("Ctrl + S", "Open/Close Shortcut Help"),
        ("Cmd + Q", "Quit Application")
    ]

    # Initialize counter
    row_counter = 0
    for key, description in shortcuts:

        # Increment row counter
        row_counter += 1

        # Create label for key
        key_label = Label(
            container,
            text=key,
            fg="#7dd3fc",
            bg="black",
            font=("Helvetica", 14, "bold"),
            anchor="w"
        )
        # Create label for description
        description_label = Label(
            container,
            text=description,
            fg="white",
            bg="black",
            font=("Helvetica", 14),
            anchor="w"
        )

        # Place key and discription
        key_label.grid(row=row_counter, column=0, sticky="w", padx=(0, 20), pady=3)
        description_label.grid(row=row_counter, column=1, sticky="w", pady=3)

    return overlay


def bind_shortcut_overlay(root):
    '''Bind Cmd+S to toggle shortcut overlay.'''

    # Create variables for the Window and the visibility
    overlay = create_shortcut_overlay(root)
    visible = {"state": False}

    def toggle_overlay(event=None):
        '''Toggles visibility of shortcut overlay.'''
        if visible["state"]:
            # when visible state = True, remove window
            overlay.withdraw()
        else:
            # when visible state = False, show window
            overlay.deiconify()

        # update visibility variable
        visible["state"] = not visible["state"]

    # Bind keybordshortcut to the toggle funcrtion
    root.bind_all("<Control-s>", toggle_overlay)


# =================================================== #
# ===== MENU ======================================== #
# =================================================== #

def build_menubar(root):
    '''Builds the menubar attatched to root'''
    menubar = Menu(root)
    root.config(menu=menubar)
    return menubar

def configure_about(menubar, root, app_dir):
    '''Creates "About" dropdown menu'''
    # Create About menu
    about_menu = Menu(menubar, tearoff=0)
    # Create submenu
    menubar.add_cascade(label="About", menu=about_menu)
    # Add About submenu to About
    about_menu.add_command(label="About", command=lambda: show_about_disclaimer(root, app_dir))
    # Add Licenses submenu to About
    about_menu.add_command(label="Licenses", command=lambda: show_license(root))
    # Add Version Notes submenu to About
    about_menu.add_command(label="Version Notes", command=lambda: show_version_notes(root))

def configure_system(menubar, root):
    '''Creates "System" dropdown menu'''
    # Create System menu
    system_menu = Menu(menubar, tearoff=0)
    # Create submenu
    menubar.add_cascade(label="System", menu=system_menu)
    # Add System Statistics submenu to System
    system_menu.add_command(label="System Statistics", command=lambda: show_system_stats(root))

def configure_help(menubar):
    '''Creates "Help" dropdown menu'''
    # Create Help menu
    help_menu = Menu(menubar, tearoff=0)
    # Create submenu
    menubar.add_cascade(label="Help", menu=help_menu)
    # Add Report Issue submenu to Help
    help_menu.add_command(label="Report Issue", command=report_issue)

def resource_path(filename):
    '''Get the path to a resource file.'''
    # Checks if the program is running from a PyInstaller bundle
    if hasattr(sys, "_MEIPASS"):
        # If packaged, return the files path inside the bundle.
        return os.path.join(sys._MEIPASS, filename)
    else:
         # If not packaged, return the files path inside the current working directory.
        return os.path.join(os.path.abspath("."), filename)

def show_about_disclaimer(root, app_dir):
    '''Show about/disclaimer window.'''
    # Create window
    about_window = Toplevel(root)
    about_window.title("About/Disclaimer")
    about_window.geometry(get_centered_geometry(0.6))
    # Create notebook with tabs
    notebook = Notebook(about_window)
    # Fill window with notebook
    notebook.pack(expand=True, fill=BOTH)
    
    # Define Name and file to use
    about_files = {
        "About": "ABOUT.md",
        "Disclaimer": "DISCLAIMER.md"
    }

    for title, filename in about_files.items():
        # For each file create a frame and add to the notebook
        frame = Frame(notebook)
        notebook.add(frame, text=title)
        text = Text(frame, wrap="word", font=("Courier", 10))
        text.pack(expand=True, fill=BOTH, side="left")
        scrollbar = Scrollbar(frame, command=text.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        text.config(yscrollcommand=scrollbar.set)
        # Try to insert files text, else display not found message.
        try:
            with open(resource_path(filename), "r", encoding="utf-8") as f:
                text.insert(END, f.read())
        except FileNotFoundError:
            text.insert(END, f"{filename} not found.")
        # Make text read-only
        text.config(state="disabled")


def show_license(root):
    '''Show license window.'''
    # Create window
    license_window = Toplevel(root)
    license_window.title("Licenses")
    license_window.geometry(get_centered_geometry(0.6))
    # Create notebook with tabs
    notebook = Notebook(license_window)
    # Fill window with notebook
    notebook.pack(expand=True, fill=BOTH)
    
    # Define Name and file to use
    license_files = {
        "ConformationLabStudio (MIT)": "LICENSE_ConformationLabStudio.md",
        "ColabFold (Third-Party, MIT)": "LICENSE_ColabFold.md",
        "AlphaFold2 (Third-Party, Apache 2.0)": "LICENSE_AlphaFold2.md",
        "Third Party Licenses": "THIRD_PARTY_LICENSES.md"
    }
    # For each file create a frame and add to the notebook
    for title, filename in license_files.items():
        frame = Frame(notebook)
        notebook.add(frame, text=title)
        text = Text(frame, wrap="word", font=("Courier", 10))
        text.pack(expand=True, fill=BOTH, side="left")
        scrollbar = Scrollbar(frame, command=text.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        text.config(yscrollcommand=scrollbar.set)
        # Try to insert files text, else display not found message.
        try:
            with open(resource_path(filename), "r", encoding="utf-8") as f:
                text.insert(END, f.read())
        except FileNotFoundError:
            text.insert(END, f"{filename} not found.")
        # Make text read-only
        text.config(state="disabled")


def show_version_notes(root):
    # Create window
    version_window = Toplevel(root)
    version_window.title("Version Notes")
    version_window.geometry(get_centered_geometry(0.6))
    # Create notebook with tabs
    notebook = Notebook(version_window)
    # Fill window with notebook
    notebook.pack(expand=True, fill=BOTH)

    # Define Name and file to use
    versions_files = {
        "Versions": "VERSIONS.md",
    }

    # For each file create a frame and add to the notebook
    for title, filename in versions_files.items():
        frame = Frame(notebook)
        notebook.add(frame, text=title)
        text = Text(frame, wrap="word", font=("Courier", 10))
        text.pack(expand=True, fill=BOTH, side="left")
        scrollbar = Scrollbar(frame, command=text.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        text.config(yscrollcommand=scrollbar.set)
        # Try to insert files text, else display not found message.
        try:
            with open(resource_path(filename), "r", encoding="utf-8") as f:
                text.insert(END, f.read())
        except FileNotFoundError:
            text.insert(END, f"{filename} not found.")
        # Make text read-only
        text.config(state="disabled")


def show_system_stats(root):
    '''Show system statistics window.'''
    # Create Window
    system_stats = Toplevel(root)
    system_stats.title("System Statistics")
    system_stats.geometry("300x150")
    # Show always on top
    system_stats.attributes('-topmost', True)
    system_stats.update_idletasks()
    screen_width = system_stats.winfo_screenwidth()
    width = system_stats.winfo_width()
    x = screen_width - width
    y = 0
    system_stats.geometry(f"+{x}+{y}")
    # Create CPU and RAM labels and bars
    cpu_label = Label(system_stats, text="CPU Usage:")
    cpu_label.pack(anchor='w', padx=10, pady=5)
    cpu_progress = Progressbar(system_stats, orient='horizontal', length=200, mode='determinate', maximum=100)
    cpu_progress.pack(padx=10)
    cpu_percent_label = Label(system_stats, text="0%")
    cpu_percent_label.pack(anchor='e', padx=10)
    ram_label = Label(system_stats, text="RAM Usage:")
    ram_label.pack(anchor='w', padx=10, pady=5)
    ram_progress = Progressbar(system_stats, orient='horizontal', length=200, mode='determinate', maximum=100)
    ram_progress.pack(padx=10)
    ram_percent_label = Label(system_stats, text="0%")
    ram_percent_label.pack(anchor='e', padx=10)

    def update_stats():
        '''Update CPU and RAM usage indicators'''
        # Gets CPU usage in percent.
        cpu_pct = psutil.cpu_percent()
        # Gets RAM usage in percent.
        mem = psutil.virtual_memory()
        ram_pct = mem.percent
        # Update bars
        cpu_progress['value'] = cpu_pct
        cpu_percent_label.config(text=f"{int(cpu_pct)}%")
        ram_progress['value'] = ram_pct
        ram_percent_label.config(text=f"{int(ram_pct)}%")
        # repeat every second
        system_stats.after(1000, update_stats)

    update_stats()


def report_issue():
    '''Handle report issue menu command.'''
    subject = "[ConformationLab Studio] Report Issue"
    body = f'''
We are sorry to hear that there is an issue with ConformationLab Studio.
Thank you for your help in enhancing the application by providing an error report.
Please specify the problem:



-----
System Information:
OS: {platform.system()} {platform.release()}
Version: {platform.version()}
Python: {platform.python_version()}
Machine: {platform.machine()}
Processor: {platform.processor()}'''
    mailto_link = f"mailto:conformationlabstudio@gmail.com?subject={subject}&body={body}"
    if platform.system() == "Darwin":
        os.system("open -a Mail")
    elif platform.system() == "Windows":
        os.system("start outlook")
    elif platform.system() == "Linux":
        os.system("xdg-open mailto:")
    time.sleep(2)
    webbrowser.open(mailto_link, new=1)

def is_dark_mode():
    '''Determine if system is in dark mode.
    
    Currently unneccessary as included in tkinter, so theme updates automatically.
    Currently no objects that need to be handeled individually.
    '''
    try:
        if platform.system() == "Darwin":
            # Run a terminal command to reade apple interface style and save output as string
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True, text=True
            )
            # Check if "Dark" appears in the output
            return "Dark" in result.stdout
        elif platform.system() == "Windows":
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
        else:
            return False
    except Exception:
        return False


def update_theme(root):
    '''Update Theme elery 3 seconds
    
    Currently unneccessary as included in tkinter, so theme updates automatically.
    Currently no objects that need to be handeled individually.
    '''
    root.after(3000, lambda: update_theme(root))


def on_closing(root):
    '''Terminates running process (if any) and destroys root window.'''
    global process
    if process and process.poll() is None:
        try:
            process.terminate()
        except Exception as e:
            print(f"Error terminating process: {e}")
    root.destroy()

if __name__ == "__main__":
    main()

'''
Overall Structure (first draft... update...)

ConformationLabStudio.py
│
├── Todos
│
├── APP_NAME, APP_VERSION, APP_AUTHOR
│
├── Imports
│
├── Classes
│   └── ToolTip
│
├── MAIN PROGRAM
│   ├── main()
│   ├── initialize process
│   ├── create Tkinter window
│   ├── build UI layout
│   ├── build BASIC mode widgets
│   │   └── build_basic_mode()
│   ├── build ADVANCED mode widgets
│   │   └── build_advanced_mode()
│   ├── create buttons
│   │   ├── build_run_button()
│   │   ├── build_clear_button()
│   │   ├── build_cancel_button()
│   │   └── build_molstar_button()
│   ├── store everything in a shared "state" dictionary
│   └── start GUI event loop
│
├── HELPER FUNCTIONS
│   ├── UI configuration
│   │   ├── configure_grid()
│   │   ├── get_centered_geometry()
│   │   ├── configure_header_frame()
│   │   ├── configure_footer()
│   │   ├── configure_scrollable_frame()
│   │   ├── on_frame_configure()
│   │   └── on_canvas_configure()
│   │
│   ├── scrolling
│   │   └── on_global_mousewheel()
│   │
│   ├── path selection dialogs
│   │   ├── get_app_paths()
│   │   ├── create_path_selectors()
│   │   └── resource_path()
│   │
│   ├── environment setup
│   │   └── ensure_conflab_env()
│   │
│   ├── validation
│   │   └── create_validation_commands()
│   │
│   ├── widget builders
│   │   ├── build_output_wiget()
│   │   ├── build_status_frame()
│   │   ├── build_loading_frame()
│   │   └── advanced_toggle()
│   │
│   ├── UI effects
│   │   ├── apply_hover_effect()
│   │   └── hover_effect()
│   │
│   ├── keyboard shortcuts
│   │   ├── bind_shortcuts()
│   │   ├── shortcut_browse_input()
│   │   ├── shortcut_browse_output()
│   │   ├── shortcut_toggle_advanced()
│   │   ├── shortcut_run()
│   │   ├── shortcut_cancel()
│   │   ├── shortcut_clear()
│   │   └── shortcut_molviewer()
│   │
│   ├── shortcut overlay
│   │   ├── create_shortcut_overlay()
│   │   └── bind_shortcut_overlay()
│   │
│   ├── menu bar
│   │   ├── build_menubar()
│   │   ├── configure_about()
│   │   ├── configure_system()
│   │   └── configure_help()
│   │
│   └── system / theme
│       ├── is_dark_mode()
│       └── update_theme()
│
└── PROCESS CONTROL
    │
    ├── run button workflow
    │   ├── run_button_command()
    │   └── run_process()
    │
    ├── cancel workflow
    │   ├── build_cancel_button()
    │   └── cancel_process()
    │
    ├── output utilities
    │   ├── write_output()
    │   └── safe_status_update()
    │
    ├── loading animation
    │   ├── start_loading_animation()
    │   └── stop_loading_animation()
    │
    ├── molviewer
    │   └── molstar_button_command()
    │
    └── shutdown
        └── on_closing()
'''