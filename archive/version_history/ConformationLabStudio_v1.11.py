# imports ==================================================
import os
import threading
import subprocess # color mode
import sys
import tarfile
import itertools
from tkinter import *
from tkinter import filedialog, messagebox # Messagebox
from tkinter import ttk # mol*viewer button progress bar + scrollbar
from PIL import Image, ImageTk # Logo
import hashlib # Login
import re # Login
import datetime # Login
import requests # Login
import tkinter as tk # Login/window dimentions
import psutil
import webbrowser # report issue
import time # report issue
import platform  # report issue/color mode
import shutil
# imports (end) ==================================================

'''
# login ==================================================
#####################
ENABLE_MAILPW = False
ENABLE_ORCID = False
ENABLE_AUTH0 = True
#####################
GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbx95pCmR-J6P_VlCqYrlG35gF1f1F7WqwGrmmNVucWgmCooWOIxrSp9XQippsvhYnvv/exec"
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()
def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None
def send_request(email, password, action="Login"):
    password_hash = hash_password(password)
    data = {
        "username": email,
        "password": password_hash,
        "action": action,
        "timestamp": str(datetime.datetime.now())
    }
    try:
        r = requests.post(GOOGLE_SHEET_URL, json=data, timeout=10)
        return r.text.strip()
    except Exception as e:
        print("Request failed:", e)
        return "FAIL"
def show_login_window():
    result = {"ok": False, "email": None, "password": None, "orcid": None}
    login_root = tk.Tk()
    login_root.title("ConformationLab Studio Login")
    status_label = tk.Label(login_root, text="")
    status_label.pack(pady=5)
    # center window 90%
    def get_centered_geometry(scale=0.9):
        tmp_login_root = tk.Tk()
        tmp_login_root.withdraw()
        tmp_login_root.update_idletasks()
        try:
            from AppKit import NSScreen
            frame = NSScreen.mainScreen().visibleFrame()
            screen_width = int(frame.size.width)
            screen_height = int(frame.size.height)
        except ImportError:
            screen_width = tmp_login_root.winfo_screenwidth()
            screen_height = tmp_login_root.winfo_screenheight()
        tmp_login_root.destroy()
        window_width = int(screen_width * scale)
        window_height = int(screen_height * scale)
        window_x = (screen_width - window_width) // 2
        window_y = (screen_height - window_height) // 2
        return window_width, window_height, window_x, window_y
    window_width, window_height, window_x, window_y = get_centered_geometry(0.3)
    login_root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")
    if ENABLE_MAILPW:
        # login via mail and pw
        tk.Label(login_root, text="Email:").pack(pady=5)
        user_entry = tk.Entry(login_root)
        user_entry.pack(pady=5)
        tk.Label(login_root, text="Password:").pack(pady=5)
        pass_entry = tk.Entry(login_root, show="*")
        pass_entry.pack(pady=5)
        login_spinner = ttk.Progressbar(login_root, mode="determinate", length=80, maximum=100)
        register_spinner = ttk.Progressbar(login_root, mode="determinate", length=80, maximum=100)
        def run_progress(bar, seconds=3, callback=None):
            bar["value"] = 0
            steps = 100
            delay = int((seconds * 1000) / steps)
            def step():
                if bar["value"] < 100:
                    bar["value"] += 1
                    login_root.after(delay, step)
                else:
                    bar.pack_forget()
                    if callback:
                        callback()
            step()
        def temporarily_disable_buttons(clicked="login", seconds=3):
            login_button.config(state="disabled")
            register_button.config(state="disabled")
            if 'orcid_button' in locals():
                orcid_button.config(state="disabled")
            if 'auth0_button' in locals():
                auth0_button.config(state="disabled")
            if clicked == "login":
                login_spinner.pack(pady=2)
                status_label.config(text="🔑 Logging in...")
                run_progress(login_spinner, seconds, reset_buttons)
            elif clicked == "register":
                register_spinner.pack(pady=2)
                status_label.config(text="🔑 Registering...")
                run_progress(register_spinner, seconds, reset_buttons)
        def reset_buttons():
            login_button.config(state="normal")
            register_button.config(state="normal")
            if 'orcid_button' in locals():
                orcid_button.config(state="normal")
            if 'auth0_button' in locals():
                auth0_button.config(state="normal")
            login_spinner["value"] = 0
            register_spinner["value"] = 0
        def on_login():
            temporarily_disable_buttons("login")
            email = user_entry.get().strip()
            password = pass_entry.get().strip()
            def worker():
                resp = send_request(email, password, "Login")
                def handle_response():
                    login_spinner.pack_forget()
                    login_button.config(state="normal")
                    register_button.config(state="normal")
                    if 'orcid_button' in locals():
                        orcid_button.config(state="normal")
                    if 'auth0_button' in locals(): 
                        auth0_button.config(state="normal")
                    if resp == "OK":
                        result["ok"] = True
                        result["email"] = email
                        result["password"] = password
                        login_root.destroy()
                    elif resp == "NOT_ACTIVE":
                        status_label.config(text="⏳ Please activate your account via email.", fg="orange")
                    else:
                        status_label.config(text="❌ Invalid login", fg="red")
                login_root.after(0, handle_response)
            threading.Thread(target=worker, daemon=True).start()
        def on_register():
            temporarily_disable_buttons("register")
            email = user_entry.get().strip()
            password = pass_entry.get().strip()
            if not is_valid_email(email):
                status_label.config(text="❌ Please enter a valid email", fg="red")
                return
            def worker():
                resp = send_request(email, password, "Register")
                def handle_response():
                    register_spinner.pack_forget()
                    login_button.config(state="normal")
                    register_button.config(state="normal")
                    if 'orcid_button' in locals(): 
                        orcid_button.config(state="normal")
                    if 'auth0_button' in locals(): 
                        auth0_button.config(state="normal")
                    if resp == "PENDING_EMAIL":
                        status_label.config(text="📧 Check your email for activation link.", fg="orange")
                    elif resp == "DUPLICATE":
                        status_label.config(text="❌ Email already registered", fg="red")
                    elif resp == "OK":
                        status_label.config(text="✅ Registration successful! Please check your email.", fg="green")
                    else:
                        status_label.config(text="❌ Registration failed", fg="red")
                login_root.after(0, handle_response)
            threading.Thread(target=worker, daemon=True).start()
        login_button = tk.Button(login_root, text="Login", command=on_login)
        login_button.pack(pady=5)
        register_button = tk.Button(login_root, text="Register", command=on_register)
        register_button.pack(pady=5)
    if ENABLE_ORCID:
        # ORCID login
        orcid_spinner = ttk.Progressbar(login_root, mode="determinate", length=80, maximum=100)
        def reset_orcid():
            orcid_button.config(state="normal")
            if 'login_button' in locals(): 
                login_button.config(state="normal")
            if 'register_button' in locals(): 
                register_button.config(state="normal")
            if 'auth0_button' in locals(): 
                auth0_button.config(state="normal")
            orcid_spinner["value"] = 0
            orcid_spinner.pack_forget()
            status_label.config(text="")
        def run_orcid_progress(bar, orcid_process):
            bar["value"] = 0
            steps = 100
            delay = 50  
            def step():
                if orcid_process.poll() is None: 
                    bar["value"] = (bar["value"] + 1) % 100
                    login_root.after(delay, step)
                else:
                    bar.pack_forget()
                    orcid_button.config(state="normal")
                    if 'login_button' in locals(): 
                        login_button.config(state="normal")
                    if 'register_button' in locals(): 
                        register_button.config(state="normal")
                    if 'auth0_button' in locals(): 
                        auth0_button.config(state="normal")
                    try:
                        with open("orcid_result.json", "r") as f:
                            data = json.load(f)
                        if "orcid" in data:
                            status_label.config(text=f"✅ ORCID login successful: {data['orcid']}")
                            result["ok"] = True
                            result["orcid"] = data["orcid"]
                            login_root.after(1000, login_root.destroy)
                        else:
                            status_label.config(text="❌ ORCID login failed")
                    except FileNotFoundError:
                        status_label.config(text="❌ ORCID login failed (no result)")
            step()
        def on_orcid_login():
            orcid_button.config(state="disabled")
            if 'login_button' in locals(): 
                login_button.config(state="disabled")
            if 'register_button' in locals(): 
                register_button.config(state="disabled")
            if 'auth0_button' in locals(): 
                auth0_button.config(state="disabled")
            orcid_spinner.pack(pady=2)
            status_label.config(text="🔑 Opening ORCID login...")
            if getattr(sys, "frozen", False):
                orcid_path = os.path.join(os.path.dirname(sys.executable), "run_orcid")
                orcid_process = subprocess.Popen([orcid_path])
            else:
                orcid_path = os.path.join(os.path.abspath("."), "run_orcid.py")
                orcid_process = subprocess.Popen([sys.executable, orcid_path])
            run_orcid_progress(orcid_spinner, orcid_process)
        orcid_button = tk.Button(login_root, text="Login with ORCID", command=on_orcid_login)
        orcid_button.pack(pady=10)
    if ENABLE_AUTH0:
        # Auth0 login
        def run_auth0_progress(bar, auth0_process):
            bar["value"] = 0
            steps = 100
            delay = 50
            def step():
                if auth0_process.poll() is None:
                    bar["value"] = (bar["value"] + 1) % 100
                    login_root.after(delay, step)
                else:
                    bar.pack_forget()
                    auth0_button.config(state="normal")
                    if 'login_button' in locals(): 
                        login_button.config(state="normal")
                    if 'register_button' in locals(): 
                        register_button.config(state="normal")
                    if 'orcid_button' in locals(): 
                        orcid_button.config(state="normal")
                    try:
                        with open("auth0_result.json", "r") as f:
                            data = json.load(f)
                        if "email" in data:
                            status_label.config(text=f"✅ Auth0 login successful: {data['email']}")
                            result["ok"] = True
                            result["email"] = data["email"]
                            login_root.after(1000, login_root.destroy)
                        else:
                            status_label.config(text="❌ Auth0 login failed")
                    except FileNotFoundError:
                        status_label.config(text="❌ Auth0 login failed (no result)")
            step()
        def on_auth0_login():
            auth0_button.config(state="disabled")
            if 'login_button' in locals():
                login_button.config(state="disabled")
            if 'register_button' in locals():
                register_button.config(state="disabled")
            if 'orcid_button' in locals():
                orcid_button.config(state="disabled")
            auth0_spinner.pack(pady=2)
            status_label.config(text="🔑 Opening Auth0 login...")
            if getattr(sys, "frozen", False):
                auth0_path = os.path.join(os.path.dirname(sys.executable), "run_login_auth0_v1.0")
                auth0_process = subprocess.Popen([auth0_path])
            else:
                auth0_path = os.path.join(os.path.abspath("."), "run_login_auth0_v1.0.py")
                auth0_process = subprocess.Popen([sys.executable, auth0_path])
            run_auth0_progress(auth0_spinner, auth0_process)
        auth0_spinner = ttk.Progressbar(login_root, mode="determinate", length=80, maximum=100)
        auth0_button = tk.Button(login_root, text="Login with Auth0", command=on_auth0_login)
        auth0_button.pack(pady=10)
    login_root.mainloop()
    return result
#login feedback
result = show_login_window()
if not result["ok"]:
    sys.exit(0)  # exit if login fails
if result.get("orcid"):
    print("Logged in with ORCID:", result["orcid"])
else:
    print("Logged in with email:", result.get("email"))
email = result["email"]  # falls du die Mail später im UI anzeigen willst
# login (end) ==================================================
'''

# Path ==================================================
if getattr(sys, 'frozen', False):
    APPDIR = sys._MEIPASS
else:
    APPDIR = os.path.dirname(os.path.abspath(__file__))
ENV_TAR = os.path.join(APPDIR, "conflab_env.tar.gz")
ENV_DIR = os.path.expanduser("~/Library/Application Support/ConfLabEnv")
# Unpack if not already unpacked
if not os.path.exists(os.path.join(ENV_DIR, "bin")):
    os.makedirs(ENV_DIR, exist_ok=True)
    if os.path.exists(ENV_TAR):
        with tarfile.open(ENV_TAR, "r:gz") as tar:
            tar.extractall(ENV_DIR)
conflab_bin = os.path.join(ENV_DIR, "bin", "conflab_batch")
# path (end) ==================================================

# environment ==================================================
def ensure_conflab_env():
    target_dir = os.path.expanduser("~/Library/Application Support/ConfLabEnv")
    conflab_bin = os.path.join(target_dir, "bin", "conflab_batch")
    if not os.path.exists(conflab_bin):
        archive = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(sys.executable)), "conflab_env.tar.gz")
        print(f"[INFO] Entpacke Umgebung nach {target_dir} ...")
        os.makedirs(target_dir, exist_ok=True)
        with tarfile.open(archive, "r:gz") as tar:
            tar.extractall(path=target_dir)
        print("[INFO] Umgebung erfolgreich entpackt")
    return conflab_bin
# environment (end) ==================================================

# root = main window ==================================================
root = Tk()
root.lift()
root.attributes("-topmost", True)
root.after(100, lambda: root.attributes("-topmost", False))
def on_closing():
    global process
    if process and process.poll() is None:
        try:
            process.terminate()
        except Exception as e:
            print(f"Error terminating process: {e}")
    root.destroy()
root.title("ConformationLab Studio")
root.grid_rowconfigure(0, weight=0)
root.grid_rowconfigure(1, weight=0)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=0)
root.grid_columnconfigure(0, weight=1)
# center window 90%
def get_centered_geometry(scale=0.9):
    # Temporär Tk-Fenster für Bildschirmmaße
    try:
        # macOS: verfügbare Fläche ohne Menü/Dock
        from AppKit import NSScreen
        frame = NSScreen.mainScreen().visibleFrame()
        screen_width = int(frame.size.width)
        screen_height = int(frame.size.height)
    except ImportError:
        # Fallback: normale Bildschirmmaße
        tmp_root = tk.Tk()
        tmp_root.withdraw()
        tmp_root.update_idletasks()
        screen_width = tmp_root.winfo_screenwidth()
        screen_height = tmp_root.winfo_screenheight()
        tmp_root.destroy()
    window_width = int(screen_width * scale)
    window_height = int(screen_height * scale)
    window_x = (screen_width - window_width) // 2
    window_y = (screen_height - window_height) // 2
    return f"{window_width}x{window_height}+{window_x}+{window_y}"
root.geometry(get_centered_geometry(0.9))
# root = main window (end) ==================================================

# safe status update ==================================================
def safe_status_update(text, color=None):
    if color:
        root.after(0, lambda: status_label.config(text=text, foreground=color))
    else:
        root.after(0, lambda: status_label.config(text=text))
# safe status update (end) ==================================================

# theme light/dark mode ==================================================
def is_dark_mode() -> bool:
    try:
        if platform.system() == "Darwin":
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True, text=True
            )
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
def update_theme():
    root.after(3000, update_theme)

# theme light/dark mode (end) ==================================================

# header ==================================================
# header frame
header_frame = Frame(root)
header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=0, padx=10)
'''
# separator
separator = Frame(root, height=2, bg="white", relief="sunken")
separator.grid(row=1, column=0, columnspan=3, sticky="ew", pady=10, padx=10)
'''

# logo
logo_path = os.path.join(APPDIR, "ConformationLabLogo.png")
if os.path.exists(logo_path):
    logo_img = Image.open(logo_path).resize((100, 100), Image.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_img)
    logo_label = Label(header_frame, image=logo_photo)
    logo_label.image = logo_photo
    logo_label.grid(row=0, column=0, rowspan=2, padx=10, pady=5)
title_frame = Frame(header_frame)
title_frame.grid(row=0, column=1, sticky="w", padx=10, pady=20)
global title_label, subtitle_label
title_label = Label(title_frame, text="ConformationLab Studio", 
                    font=("Arial", 22, "bold"))
title_label.grid(row=0, column=0, sticky="w")
subtitle_label = Label(title_frame, text="Local Protein Structure Prediction for Apple Devices", 
                       font=("Arial", 12))
subtitle_label.grid(row=1, column=0, sticky="w")

header_frame.columnconfigure(0, weight=0)
header_frame.columnconfigure(1, weight=1)
header_frame.columnconfigure(2, weight=0)
header_frame.columnconfigure(3, weight=0) 
# header (end) ==================================================


# scrollbar ==================================================
# define scrollbar when neccessary
# scrollbar (end) ==================================================

# Scrollable main frame ==================================================
main_container = Frame(root)
main_container.grid(row=2, column=0, columnspan=3, sticky="nsew")
main_canvas = Canvas(main_container, highlightthickness=0)
main_canvas.pack(side=LEFT, fill=BOTH, expand=True)
scrollable_frame = Frame(main_canvas)
window_id = main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
# Scrollable main frame (end) ==================================================

# Scrolling main frame and messagebox ==================================================
def on_frame_configure(event):
    bbox = main_canvas.bbox(window_id)
    if bbox:
        main_canvas.configure(scrollregion=bbox)
scrollable_frame.bind("<Configure>", on_frame_configure)
def on_canvas_configure(event):
    main_canvas.itemconfig(window_id, width=event.width)
main_canvas.bind("<Configure>", on_canvas_configure)
# Unified Scroll Handling
def _on_global_mousewheel(event):
    widget = root.winfo_containing(event.x_root, event.y_root)
    if isinstance(widget, tk.Text):
        if sys.platform == "darwin":
            widget.yview_scroll(-1 * event.delta, "units")
        else:
            widget.yview_scroll(-1 * (event.delta // 120), "units")
        return "break"
    if sys.platform == "darwin":
        main_canvas.yview_scroll(-1 * event.delta, "units")
    else:
        main_canvas.yview_scroll(-1 * (event.delta // 120), "units")
    return "break"
root.bind_all("<MouseWheel>", _on_global_mousewheel)
# Scrolling main frame and messagebox (end) ==================================================

# widgets middle
scrollable_frame.grid_columnconfigure(0, weight=1)  # linke Spalte
scrollable_frame.grid_columnconfigure(1, weight=1)  # mittlere Spalte
scrollable_frame.grid_columnconfigure(2, weight=1)  # rechte Spalte

# background image ==================================================
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
# background image (end) ==================================================

# ToolTip i ==================================================
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
# ToolTip i (end) ==================================================

# only numbers ==================================================
def only_numbers(new_value):
    if new_value.isdigit() or new_value == "":
        return True
    root.bell()
    return False
vcmd_numbers = (root.register(only_numbers), "%P")
def numbers_or_auto(new_value):
    if new_value == "" or new_value.lower() == "auto":
        return True
    try:
        float(new_value)
        return True
    except ValueError:
        root.bell()
        return False

vcmd_numbers_or_auto = (root.register(numbers_or_auto), "%P")
def numbers_and_commas(new_value):
    if all(c.isdigit() or c == "," for c in new_value) or new_value == "":
        return True
    root.bell()
    return False
vcmd_numbers_commas = (root.register(numbers_and_commas), "%P")
# only numbers (end) ==================================================

# Placeholders (unused) ==================================================
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
# command example: # add_placeholder(num_relax_entry, "Enter Number")
# Placeholders (end) ==================================================

# Parameters (BASIC) ==================================================
basic_frame = ttk.LabelFrame(scrollable_frame, text="BASIC mode")
basic_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
basic_frame.columnconfigure(0, weight=1)
basic_frame.columnconfigure(1, weight=1)
basic_frame.columnconfigure(2, weight=1)
## Path selection
path_frame = LabelFrame(basic_frame, text="Path", padx=10, pady=10)
path_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
path_frame.columnconfigure(0, weight=1, uniform="inputs")
path_frame.columnconfigure(1, weight=2, uniform="inputs")
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
input_label = Label(path_frame, padx=10, text="Input file:")
input_label.grid(row=0 , column=0, sticky="w")
input_entry = Entry(path_frame, textvariable=inputpath_selected)
input_entry.grid(row=0 , column=1, padx=10, pady=2)
input_button = Button(path_frame, text = "Browse", fg="#000000", command = select_input_path)
input_button.grid(row=0 , column=2)
output_label = Label(path_frame, padx=10, text="Output folder:")
output_label.grid(row=1 , column= 0, sticky="w")
output_entry = Entry(path_frame, textvariable = outputpath_selected)
output_entry.grid(row=1 , column=1, padx=10, pady=2)
output_button = Button(path_frame, text = "Browse", fg="#000000", command = select_output_path)
output_button.grid(row=1 , column=2)
## assembly
assembly_frame = LabelFrame(basic_frame, text="Path and Assembly", padx=10, pady=10)
assembly_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
assembly_frame.columnconfigure(0, weight=1, uniform="inputs")
assembly_frame.columnconfigure(1, weight=2, uniform="inputs")
### assembly type
assembly_type_label = Label(assembly_frame, padx=10, text = "Assembly Type:")
assembly_type_label.grid(row=1, column=0, sticky="w")
assembly_type_options = ["monomer", "multimer"]
assembly_type_var = StringVar(value = "monomer")
assembly_type_dropdown = OptionMenu(assembly_frame, assembly_type_var, *assembly_type_options)
assembly_type_dropdown.grid(row=1 , column=1, padx=10, pady=2)
assembly_type_info = Label(assembly_frame, text="ⓘ", fg="#007acc", cursor="hand2")
assembly_type_info.grid(row=1, column=2)
assembly_type_tooltip = ToolTip(
    assembly_type_info,
    "Monomer: one amino acid chain or Multimer: multiple amino acid chains"
    )
## Seeds
seeds_frame = LabelFrame(basic_frame, text="Seeds", padx=10, pady=10)
seeds_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
seeds_frame.columnconfigure(0, weight=1, uniform="inputs")
seeds_frame.columnconfigure(1, weight=2, uniform="inputs")
### --num-seeds
num_seeds_label = Label(seeds_frame, padx=10, text="Number of Seeds:")
num_seeds_label.grid(row=0 , column=0, sticky="w")
num_seeds_entry = Entry(seeds_frame, validate="key", validatecommand=vcmd_numbers)
num_seeds_entry.grid(row=0 , column=1, padx=10, pady=2)
num_seeds_entry.insert(0, "3")
num_seeds_info = Label(seeds_frame, text="ⓘ", fg="#007acc", cursor="hand2")
num_seeds_info.grid(row=0, column=2)
num_seeds_tooltip = ToolTip(
    num_seeds_info,
    "Possible entries: Integer ≥ 1. Number of independent predictions. Amount of times the five models are computed. Default=3 -> 3 times 5 models and 3 recycles = 45 cycles total."
    )
### --random-seed
random_seeds_label = Label(seeds_frame, padx=10, text="Random Seeds:")
random_seeds_label.grid(row=1, column=0, sticky="w")
random_seeds_entry = Entry(seeds_frame, validate="key", validatecommand=vcmd_numbers)
random_seeds_entry.grid(row=1, column=1, padx=10, pady=2)
random_seeds_entry.insert(0, "")
random_seeds_info = Label(seeds_frame, text="ⓘ", fg="#007acc", cursor="hand2")
random_seeds_info.grid(row=1, column=2)
random_seeds_tooltip = ToolTip(
    random_seeds_info,
    "Set a specific random seed for reproducibility. For random-seed=45 and num-seed=3, seeds 45, 46 and 47 will be used. Leave empty for randome seed choice."
    )
## Modle
model_frame = LabelFrame(basic_frame, text="Model", padx=10, pady=10)
model_frame.grid(row=4, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
model_frame.columnconfigure(0, weight=1, uniform="inputs")
model_frame.columnconfigure(1, weight=2, uniform="inputs")
### --model-type
model_type_label = Label(model_frame, padx=10, text = "Model:")
model_type_label.grid(row=0, column=0, sticky="w")
model_type_options = ["auto", "alphafold2_ptm", "alphafold2_multimer_v1", "alphafold2_multimer_v2", "alphafold2_multimer_v3", "deepfold_v1"]
model_type_var = StringVar(value = "auto")
model_type_dropdown = OptionMenu(model_frame, model_type_var, *model_type_options)
model_type_dropdown.grid(row=0 , column=1, padx=10, pady=2)
model_type_info = Label(model_frame, text="ⓘ", fg="#007acc", cursor="hand2")
model_type_info.grid(row=0, column=2)
model_type_tooltip = ToolTip(
    model_type_info,
    "The default is auto. Usually recommended: 'alphafold2_ptm' for single chains and 'alphafold2_multimer_v3' for multiple chains."
    )
## Recycles
recycles_frame = LabelFrame(basic_frame, text="Recycles", padx=10, pady=10)
recycles_frame.grid(row=5, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
recycles_frame.columnconfigure(0, weight=1, uniform="inputs")
recycles_frame.columnconfigure(1, weight=2, uniform="inputs")
### --num-recycles
num_recycle_label = Label(recycles_frame, padx=10, text="Number of Recycles:")
num_recycle_label.grid(row=0, column=0, sticky="w")
num_recycle_entry = Entry(recycles_frame,  validate="key", validatecommand=vcmd_numbers)
num_recycle_entry.grid(row=0, column=1, padx=10, pady=2)
num_recycle_entry.insert(0, "3")
num_recycle_info = Label(recycles_frame, text="ⓘ", fg="#007acc", cursor="hand2")
num_recycle_info.grid(row=0, column=2)
num_recycle_tooltip = ToolTip(
    num_recycle_info,
    "Number of times each of the five models is refined. Default=3 -> 3 times 5 models = 15 cycles total."
    )
### --recycle-early-stop-tolerance
recycle_early_stop_tolerance_label = Label(recycles_frame, padx=10, text="Recycles early Stop Tolerance:")
recycle_early_stop_tolerance_label.grid(row=1, column=0, sticky="w")
recycle_early_stop_tolerance_entry = Entry(recycles_frame,  validate="key", validatecommand=vcmd_numbers_or_auto)
recycle_early_stop_tolerance_entry.grid(row=1, column=1, padx=10, pady=2)
recycle_early_stop_tolerance_entry.insert(0, "auto")
recycle_early_stop_tolerance_info = Label(recycles_frame, text="ⓘ", fg="#007acc", cursor="hand2")
recycle_early_stop_tolerance_info.grid(row=1, column=2)
recycle_early_stop_tolerance_tooltip = ToolTip(
    recycle_early_stop_tolerance_info,
    "When the difference between plDDT in successive recycles is below this threshhold the recycle process is stopped. Auto: Default for monomers 0.0, Default for multimers 0.5."
    )
## Multi Sequence Alignments
msa_frame = LabelFrame(basic_frame, text="Multi Sequence Alignments", padx=10, pady=10)
msa_frame.grid(row=6, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
msa_frame.columnconfigure(0, weight=1, uniform="inputs")
msa_frame.columnconfigure(1, weight=2, uniform="inputs")
### --max-msa
max_msa_label = Label(msa_frame, padx=10, text="Number of Sequences for Multi Sequence Alignment:")
max_msa_label.grid(row=0, column=0, sticky="w")
max_msa_frame = Frame(msa_frame)
max_msa_frame.grid(row=0, column=1, padx=10, pady=2)
max_msa_entry1 = Entry(max_msa_frame, validate="key", validatecommand=vcmd_numbers)
max_msa_entry1.pack(side=LEFT)
max_msa_entry1.insert(0, "256")
max_msa_label_div = Label(max_msa_frame, text = ":")
max_msa_label_div.pack(side=LEFT)
max_msa_entry2 = Entry(max_msa_frame, validate="key", validatecommand=vcmd_numbers)
max_msa_entry2.pack(side=LEFT)
max_msa_entry2.insert(0, "256")
max_msa_info = Label(msa_frame, text="ⓘ", fg="#007acc", cursor="hand2")
max_msa_info.grid(row=0, column=2)
max_msa_tooltip = ToolTip(
    max_msa_info,
    "Number of multi sequence alignments. <unpaired>:<paired>. Number of alignments of single chains and chain pairs."
    )
### --msa-mode
msa_mode_label = Label(msa_frame, padx=10, text = "MSA Mode:")
msa_mode_label.grid(row=1, column=0, sticky="w")
msa_mode_options = ["mmseqs2_uniref_env", "mmseqs2_uniref", "single_sequence"]
msa_mode_var = StringVar(value = "mmseqs2_uniref_env")
msa_mode_dropdown = OptionMenu(msa_frame, msa_mode_var, *msa_mode_options)
msa_mode_dropdown.grid(row=1, column=1, padx=10, pady=2)
msa_mode_info = Label(msa_frame, text="ⓘ", fg="#007acc", cursor="hand2")
msa_mode_info.grid(row=1, column=2)
msa_mode_tooltip = ToolTip(
    msa_mode_info,
    "Default 'mmseqs2_uniref_env' searches for MSA against UniRef databasses and environmental sequences. 'mmseqs2_uniref' searches uniref only for faster runtimes. 'single-sequence' uses no databases and therefor no MSA."
    )
### --paired-mode
pair_mode_label = Label(msa_frame, padx=10, text = "Pair Mode:")
pair_mode_label.grid(row=2, column=0, sticky="w")
pair_mode_options = ["unpaired_paired", "unpaired", "paired"]
pair_mode_var = StringVar(value = "unpaired_paired")
pair_mode_dropdown = OptionMenu(msa_frame, pair_mode_var, *pair_mode_options)
pair_mode_dropdown.grid(row=2, column=1, padx=10, pady=2)
pair_mode_info = Label(msa_frame, text="ⓘ", fg="#007acc", cursor="hand2")
pair_mode_info.grid(row=2, column=2)
pair_mode_tooltip = ToolTip(
    pair_mode_info,
    "Default 'unpaired_paired' which does both. 'unpaired' uses independent alignments only for each chain and 'paired' only uses paired sequences and can be used when complexes are well preserved."
    )
## Ranking
ranking_frame = LabelFrame(basic_frame, text="Ranking", padx=10, pady=10)
ranking_frame.grid(row=7, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
ranking_frame.columnconfigure(0, weight=1, uniform="inputs")
ranking_frame.columnconfigure(1, weight=2, uniform="inputs")
### --ranking
rank_label = Label(ranking_frame, padx=10, text = "Rank:")
rank_label.grid(row=0, column=0, sticky="w")
rank_options = ["auto", "plddt", "ptm", "iptm", "multimer"]
rank_var = StringVar(value = "auto")
rank_dropdown = OptionMenu(ranking_frame, rank_var, *rank_options)
rank_dropdown.grid(row=0 , column=1, padx=10, pady=2)
rank_info = Label(ranking_frame, text="ⓘ", fg="#007acc", cursor="hand2")
rank_info.grid(row=0, column=2)
rank_tooltip = ToolTip(
    rank_info,
    "Use 'plddt' for single sequences and 'multimer' for complexes."
    )
## Templates
templates_frame = LabelFrame(basic_frame, text="Templates", padx=10, pady=10)
templates_frame.grid(row=8, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
templates_frame.columnconfigure(0, weight=1, uniform="inputs")
templates_frame.columnconfigure(1, weight=2, uniform="inputs")
### --templates
templates_label = Label(templates_frame, padx=10, text = "Templates:")
templates_label.grid(row=0, column=0, sticky="w")
templates_options = ["Yes", "No"]
templates_var = StringVar(value = "Yes")
templates_dropdown = OptionMenu(templates_frame, templates_var, *templates_options)
templates_dropdown.grid(row=0 , column=1, padx=10, pady=2)
templates_info = Label(templates_frame, text="ⓘ", fg="#007acc", cursor="hand2")
templates_info.grid(row=0, column=2)
templates_tooltip = ToolTip(
    templates_info,
    "Used to allow the model to bias against reference sequences from databases."
    )
## Amber Relaxation
relaxation_frame = LabelFrame(basic_frame, text="Relaxation", padx=10, pady=10)
relaxation_frame.grid(row=9, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
relaxation_frame.columnconfigure(0, weight=1, uniform="inputs")
relaxation_frame.columnconfigure(1, weight=2, uniform="inputs")
### --amber
amber_label = Label(relaxation_frame, padx=10, text = "Relaxation with Amber:")
amber_label.grid(row=0, column=0, sticky="w")
amber_options = ["Yes", "No"]
amber_var = StringVar(value = "No")
amber_dropdown = OptionMenu(relaxation_frame, amber_var, *amber_options)
amber_dropdown.grid(row=0 , column=1, padx=10, pady=2)
amber_info = Label(relaxation_frame, text="ⓘ", fg="#007acc", cursor="hand2")
amber_info.grid(row=0, column=2)
amber_tooltip = ToolTip(
    amber_info,
    "Used to relax the prediction by running energy minimisation thereby fixing unrealistic bond lengths and angles caused by steric clashes or strained bond geometrics."
    )
### --num-relax
num_relax_label = Label(relaxation_frame, padx=10, text="Number of Relaxes:")
num_relax_label.grid(row=1 , column=0, sticky="w")
num_relax_entry = Entry(relaxation_frame,  validate="key", validatecommand=vcmd_numbers)
num_relax_entry.grid(row=1 , column=1, padx=10, pady=2)
num_relax_entry.insert(0, "0")
num_relax_info = Label(relaxation_frame, text="ⓘ", fg="#007acc", cursor="hand2")
num_relax_info.grid(row=1, column=2)
num_relax_tooltip = ToolTip(
    num_relax_info,
    "Number of relaxations with amber."
    )
def toggle_num_relax(*args):
    if amber_var.get() == "Yes":
        num_relax_entry.config(state="normal")
    else:
        num_relax_entry.delete(0, tk.END)
        num_relax_entry.insert(0, "0")
        num_relax_entry.config(state="disabled")
amber_var.trace_add("write", toggle_num_relax)
toggle_num_relax()
## Output
output_frame = LabelFrame(basic_frame, text="Output", padx=10, pady=10)
output_frame.grid(row=10, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
output_frame.columnconfigure(0, weight=1, uniform="inputs")
output_frame.columnconfigure(1, weight=2, uniform="inputs")
### --overwrite-existing-results
overwrite_existing_results_label = Label(output_frame, padx=10, text = "Overwrite Existing Results:")
overwrite_existing_results_label.grid(row=6, column=0, sticky="w")
overwrite_existing_results_options = ["Yes", "No"]
overwrite_existing_results_var = StringVar(value = "No")
overwrite_existing_results_dropdown = OptionMenu(output_frame, overwrite_existing_results_var, *overwrite_existing_results_options)
overwrite_existing_results_dropdown.grid(row=6 , column=1, padx=10, pady=2)
overwrite_existing_results_info = Label(output_frame, text="ⓘ", fg="#007acc", cursor="hand2")
overwrite_existing_results_info.grid(row=6, column=2)
overwrite_existing_results_tooltip = ToolTip(
    overwrite_existing_results_info,
    "Choose whether you want a second run to overwrite the old files. Default No."
    )
### --zip
zip_label = Label(output_frame, padx=10, text = "Pack into ZIP-file:")
zip_label.grid(row=7, column=0, sticky="w")
zip_options = ["Yes", "No"]
zip_var = StringVar(value = "Yes")
zip_dropdown = OptionMenu(output_frame, zip_var, *zip_options)
zip_dropdown.grid(row=7 , column=1, padx=10, pady=2)
zip_info = Label(output_frame, text="ⓘ", fg="#007acc", cursor="hand2")
zip_info.grid(row=7, column=2)
zip_tooltip = ToolTip(
    zip_info,
    "Choose whether you want the output to be files, then you should choose a prior generated folder, or a ZIP-file. Default Yes"
    )
# Parameters BASIC (end) ==================================================

# spacer1 ==================================================
spacer1 = Frame(root, height=50)
spacer1.grid(row=2, column=0)
# spacer1 (end) ==================================================

# Parameters ADVANCED ==================================================
advanced_frame = ttk.LabelFrame(scrollable_frame, text="ADVANCED mode")
advanced_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
advanced_frame.columnconfigure(0, weight=1)
advanced_frame.columnconfigure(1, weight=1)
advanced_frame.columnconfigure(2, weight=1)
advanced_frame.grid_remove()
## Model (Advanced)
model_advanced_frame = LabelFrame(advanced_frame, text="Model", padx=10, pady=10)
model_advanced_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
model_advanced_frame.columnconfigure(0, weight=1, uniform="inputs")
model_advanced_frame.columnconfigure(1, weight=2, uniform="inputs")
### --num-models
num_model_label = Label(model_advanced_frame, padx=10, text = "Number of models:")
num_model_label.grid(row=0, column=0, sticky="w")
num_model_entry = Entry(model_advanced_frame, validate="key", validatecommand=vcmd_numbers)
num_model_entry.grid(row=0, column=1, padx=10, pady=2)
num_model_entry.insert(0, "5")
num_model_info = Label(model_advanced_frame, text="ⓘ", fg="#007acc", cursor="hand2")
num_model_info.grid(row=0, column=2)
num_model_tooltip = ToolTip(
    num_model_info,
    "Controls how many of the five internal model weights are used. Enter 1 through 5. Default 5, all models."
    )
### --model-order
model_order_label = Label(model_advanced_frame, padx=10, text = "Model order:")
model_order_label.grid(row=1, column=0, sticky="w")
model_order_entry = Entry(model_advanced_frame, validate="key", validatecommand=vcmd_numbers_commas)
model_order_entry.grid(row=1, column=1, padx=10, pady=2)
model_order_entry.insert(0, "1,2,3,4,5")
model_order_info = Label(model_advanced_frame, text="ⓘ", fg="#007acc", cursor="hand2")
model_order_info.grid(row=1, column=2)
model_order_tooltip = ToolTip(
    model_order_info,
    "Order in which the specified number of models are applied. Enter Permutations of 1 through 'num-models' devided by comma. Default for 5 models 1,2,3,4,5. Enter 0 for default."
    )
## Ensemble (Advanced)
ensemble_advanced_frame = LabelFrame(advanced_frame, text="Ensemble", padx=10, pady=10)
ensemble_advanced_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
ensemble_advanced_frame.columnconfigure(0, weight=1, uniform="inputs")
ensemble_advanced_frame.columnconfigure(1, weight=2, uniform="inputs")
### --num-ensemble
num_ensemble_label = Label(ensemble_advanced_frame, padx=10, text = "Number of ensembles:")
num_ensemble_label.grid(row=0, column=0, sticky="w")
num_ensemble_entry = Entry(ensemble_advanced_frame, validate="key", validatecommand=vcmd_numbers)
num_ensemble_entry.grid(row=0, column=1, padx=10, pady=2)
num_ensemble_entry.insert(0, "1")
num_ensemble_info = Label(ensemble_advanced_frame, text="ⓘ", fg="#007acc", cursor="hand2")
num_ensemble_info.grid(row=0, column=2)
num_ensemble_tooltip = ToolTip(
    num_ensemble_info,
    "Number of ensemble predictions per model, default: 1 (no extra ensembles), use >1 only if instability is suspected."
    )
## Cluster (Advanced)
cluster_advanced_frame = LabelFrame(advanced_frame, text="Cluster", padx=10, pady=10)
cluster_advanced_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
cluster_advanced_frame.columnconfigure(0, weight=1, uniform="inputs")
cluster_advanced_frame.columnconfigure(1, weight=2, uniform="inputs")
### --disable-cluster-profile
disable_cluster_profile_label = Label(cluster_advanced_frame, padx=10, text = "Disable cluster profile:")
disable_cluster_profile_label.grid(row=0, column=0, sticky="w")
disable_cluster_profile_options = ["Yes", "No"]
disable_cluster_profile_var = StringVar(value = "Yes")
disable_cluster_profile_dropdown = OptionMenu(cluster_advanced_frame, disable_cluster_profile_var, *disable_cluster_profile_options)
disable_cluster_profile_dropdown.grid(row=0 , column=1, padx=10, pady=2)
disable_cluster_profile_info = Label(cluster_advanced_frame, text="ⓘ", fg="#007acc", cursor="hand2")
disable_cluster_profile_info.grid(row=0, column=2)
disable_cluster_profile_tooltip = ToolTip(
    disable_cluster_profile_info,
    "Turns off cluster profile in MSA. Default off, turn on when working with very shallow alignments."
    )
## template (Advanced)
template_advanced_frame = LabelFrame(advanced_frame, text="Template", padx=10, pady=10)
template_advanced_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
template_advanced_frame.columnconfigure(0, weight=1, uniform="inputs")
template_advanced_frame.columnconfigure(1, weight=2, uniform="inputs")
### --custom-template-path
def select_template_path():
    path = filedialog.askopenfilename(title="Select input template file")
    if path:
        templatepath_selected.set(path)
templatepath_selected = StringVar()
templatepath_label = Label(template_advanced_frame, padx=10, text="Input template file:")
templatepath_label.grid(row=0 , column=0, sticky="w")
templatepath_entry = Entry(template_advanced_frame, textvariable=templatepath_selected)
templatepath_entry.grid(row=0 , column=1, padx=10, pady=2)
templatepath_button = Button(template_advanced_frame, text = "Browse", fg="#000000", command = select_template_path)
templatepath_button.grid(row=0 , column=2)
def toggle_template_path(*args):
    if templates_var.get() == "Yes":
        templatepath_entry.config(state="normal")
        templatepath_button.config(state="normal")
    else:
        templatepath_entry.delete(0, tk.END)
        templatepath_selected.set("")
        templatepath_entry.config(state="disabled")
        templatepath_button.config(state="disabled")
templates_var.trace_add("write", toggle_template_path)
toggle_template_path()
## output (Advanced)
output_advanced_frame = LabelFrame(advanced_frame, text="Output", padx=10, pady=10)
output_advanced_frame.grid(row=4, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
output_advanced_frame.columnconfigure(0, weight=1, uniform="inputs")
output_advanced_frame.columnconfigure(1, weight=2, uniform="inputs")
### --use-dropout
use_dropout_label = Label(output_advanced_frame, padx=10, text = "Use dropout:")
use_dropout_label.grid(row=0, column=0, sticky="w")
use_dropout_options = ["Yes", "No"]
use_dropout_var = StringVar(value = "No")
use_dropout_dropdown = OptionMenu(output_advanced_frame, use_dropout_var, *use_dropout_options)
use_dropout_dropdown.grid(row=0 , column=1, padx=10, pady=2)
use_dropout_info = Label(output_advanced_frame, text="ⓘ", fg="#007acc", cursor="hand2")
use_dropout_info.grid(row=0, column=2)
use_dropout_tooltip = ToolTip(
    use_dropout_info,
    "Activates dropout during inference and thereby estimates uncertainty, Default No, turn on for uncertainty analysis."
    )
### --stop-at-score
stop_at_score_label = Label(output_advanced_frame, padx=10, text = "Stop at score:")
stop_at_score_label.grid(row=1, column=0, sticky="w")
stop_at_score_entry = Entry(output_advanced_frame, validate="key", validatecommand=vcmd_numbers)
stop_at_score_entry.grid(row=1, column=1, padx=10, pady=2)
stop_at_score_entry.insert(0, "")
stop_at_score_info = Label(output_advanced_frame, text="ⓘ", fg="#007acc", cursor="hand2")
stop_at_score_info.grid(row=1, column=2)
stop_at_score_tooltip = ToolTip(
    stop_at_score_info,
    "Stops once a model reaches the specified confidence threshold (pLDDT or PTM). Enter an integer 0–100. Default = none or 100. Lower values (e.g., 85–90) can reduce runtime."
    )
### --save-all
save_all_label = Label(output_advanced_frame, padx=10, text = "Save all:")
save_all_label.grid(row=2, column=0, sticky="w")
save_all_options = ["Yes", "No"]
save_all_var = StringVar(value = "No")
save_all_dropdown = OptionMenu(output_advanced_frame, save_all_var, *save_all_options)
save_all_dropdown.grid(row=2 , column=1, padx=10, pady=2)
save_all_info = Label(output_advanced_frame, text="ⓘ", fg="#007acc", cursor="hand2")
save_all_info.grid(row=2, column=2)
save_all_tooltip = ToolTip(
    save_all_info,
    "Saves extra intermediate outputs. Default No, can be used for deep analysis."
    )
### --save-recycles (advanced module)
save_recycles_label = Label(output_advanced_frame, padx=10, text = "Save recycles:")
save_recycles_label.grid(row=3, column=0, sticky="w")
save_recycles_options = ["Yes", "No"]
save_recycles_var = StringVar(value = "No")
save_recycles_dropdown = OptionMenu(output_advanced_frame, save_recycles_var, *save_recycles_options)
save_recycles_dropdown.grid(row=3, column=1, padx=10, pady=2)
save_recycles_info = Label(output_advanced_frame, text="ⓘ", fg="#007acc", cursor="hand2")
save_recycles_info.grid(row=3, column=2)
save_recycles_tooltip = ToolTip(
    save_recycles_info,
    "Saves all recycle states instead of only the final. Default no, can be used for analysis of convergence."
    )
# Parameters ADVANCED (end) ==================================================

# spacer2 ==================================================
spacer2 = Frame(root, height=50)
spacer2.grid(row=4, column=0)
# spacer2 (end) ==================================================

# BASIC/ADVANCED mode ==================================================
# toggle
advanced_toggle_frame = LabelFrame(header_frame, text="ADVANCED Mode", padx=10, pady=10)
advanced_toggle_frame.grid(row=0, column=3, sticky="e", padx=10, pady=5)
toggle_canvas = tk.Canvas(advanced_toggle_frame, width=60, height=30, bg=root.cget("bg"), highlightthickness=0)
toggle_canvas.grid(row=0, column=2, pady=10, sticky="e")
'''
toggle_label = ttk.Label(header_frame, text="Advanced Mode:")
toggle_label.grid(row=1, column=1, sticky="e", padx=5)
'''
advanced_visible = tk.BooleanVar(value=False)
def draw_toggle():
    toggle_canvas.delete("all")
    if advanced_visible.get():
        toggle_canvas.create_oval(5, 5, 25, 25, fill="#4CAF50", width=0)
        toggle_canvas.create_oval(35, 5, 55, 25, fill="#4CAF50", width=0)
        toggle_canvas.create_rectangle(15, 5, 45, 25, fill="#4CAF50", width=0)
        toggle_canvas.create_oval(35, 5, 55, 25, fill="white", width=0)
    else:
        toggle_canvas.create_oval(5, 5, 25, 25, fill="#aaa", width=0)
        toggle_canvas.create_oval(35, 5, 55, 25, fill="#aaa", width=0)
        toggle_canvas.create_rectangle(15, 5, 45, 25, fill="#aaa", width=0)
        toggle_canvas.create_oval(5, 5, 25, 25, fill="white", width=0)
def toggle_advanced():
    advanced_visible.set(not advanced_visible.get())
    draw_toggle()
    if advanced_visible.get():
        advanced_frame.grid()
    else:
        advanced_frame.grid_remove()
    print("Advanced mode:", advanced_visible.get())
toggle_canvas.bind("<Button-1>", lambda e: toggle_advanced())
draw_toggle()
if not advanced_visible.get():
    advanced_frame.grid_remove()
# BASIC/ADVANCED mode (end) ==================================================

'''
# Frames for buttons ==================================================
clear_run_frame = LabelFrame(scrollable_frame, text="", padx=10, pady=10)
clear_run_frame.grid(row=11, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
clear_run_frame.columnconfigure(0, weight=1, uniform="inputs")
clear_run_frame.columnconfigure(1, weight=2, uniform="inputs")

cancel_viewer_frame = LabelFrame(scrollable_frame, text="", padx=10, pady=10)
cancel_viewer_frame.grid(row=13, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
cancel_viewer_frame.columnconfigure(0, weight=1, uniform="inputs")
cancel_viewer_frame.columnconfigure(1, weight=2, uniform="inputs")
# Frames fro buttons (end) ==================================================
'''

# buttons ==================================================
# button clear all inputs
def clear_button_command():
    # BASIC
    inputpath_selected.set("")
    outputpath_selected.set("")
    assembly_type_var.set("monomer")
    num_seeds_entry.delete(0, END); num_seeds_entry.insert(0, "3")
    random_seeds_entry.delete(0, END)
    model_type_var.set("auto")
    num_recycle_entry.delete(0, END); num_recycle_entry.insert(0, "3")
    recycle_early_stop_tolerance_entry.delete(0, END); recycle_early_stop_tolerance_entry.insert(0, "auto")
    max_msa_entry1.delete(0, END); max_msa_entry1.insert(0, "256")
    max_msa_entry2.delete(0, END); max_msa_entry2.insert(0, "256")
    msa_mode_var.set("mmseqs2_uniref_env")
    pair_mode_var.set("unpaired_paired")
    rank_var.set("auto")
    templates_var.set("Yes")
    num_relax_entry.delete(0, END); num_relax_entry.insert(0, "0")
    amber_var.set("No")
    overwrite_existing_results_var.set("No")
    zip_var.set("Yes")
    # ADVANCED
    num_model_entry.delete(0, END); num_model_entry.insert(0, "5")
    try:
        num_models = int(num_model_entry.get())
        default_model_order = ",".join(str(i) for i in range(1, num_models + 1))
    except ValueError:
        default_model_order = "1,2,3,4,5"
    model_order_entry.delete(0, END)
    model_order_entry.insert(0, default_model_order)
    num_ensemble_entry.delete(0, END); num_ensemble_entry.insert(0, "1")
    disable_cluster_profile_var.set("Yes")
    templatepath_selected.set("")
    use_dropout_var.set("No")
    stop_at_score_entry.delete(0, END); stop_at_score_entry.insert(0, "")
    save_all_var.set("No")
    save_recycles_var.set("No")
    # clear message box
    output_text.config(state="normal")
    output_text.delete("1.0", END)
    output_text.config(state="disabled")
clear_button = Button(scrollable_frame, text = "clear all", command = clear_button_command)
clear_button.grid(row=11, column=1, padx=10, pady=10)

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
cancel_button.grid(row=13, column=1, padx=5, pady=10)
process = None

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
    molstar_progress.grid(row=13, column=2, padx=5, pady=10)
    molstar_progress.start(10)
    def check_process():
        if molstar_process.poll() is None:
            root.after(500, check_process)
        else:
            reset_button()
    def reset_button():
        molstar_progress.stop()
        molstar_progress.grid_remove()
        molstar_button.grid(row=13, column=2, padx=5, pady=10)
        molstar_button.config(state=NORMAL)
    check_process()
molstar_button = Button(scrollable_frame, text="Open Mol*Viewer", command=open_molstar)
molstar_button.grid(row=13, column=2, padx=5, pady=10)
molstar_progress = ttk.Progressbar(scrollable_frame, orient=HORIZONTAL, length=100, mode='indeterminate')
molstar_progress.grid_remove()

# button run prediction
def run_button_command():
    global process
    conflab_bin = ensure_conflab_env()
    if not os.path.exists(conflab_bin):
        write_output(f"[FATAL ERROR] conflab_batch not found at {conflab_bin}", error=True)
        messagebox.showerror(
            "Error",
            f"conflab_batch executable not found.\n\nExpected at:\n{conflab_bin}\n\n"
            "Please check if the environment archive was included correctly."
        )
        return
    # Collect parameters
    ## BASIC
    inputpath = inputpath_selected.get()
    outputpath = outputpath_selected.get()
    if not inputpath or not outputpath:
        messagebox.showerror("Error", "Please select input and output paths")
        return
    if not os.path.exists(conflab_bin):
        write_output(f"[FATAL ERROR] conflab_batch not found at {conflab_bin}", error=True)
        return
    num_relax = num_relax_entry.get().strip() or "0"
    num_recycle = num_recycle_entry.get().strip() or "3"
    recycle_early_stop_tolerance = recycle_early_stop_tolerance_entry.get().strip().lower()
    if recycle_early_stop_tolerance == "auto":
        if assembly_type_var.get() == "multimer": 
            recycle_early_stop_tolerance = 0.5
        else:
            recycle_early_stop_tolerance = 0.0
    else:
        recycle_early_stop_tolerance = float(recycle_early_stop_tolerance)
    num_seeds = num_seeds_entry.get().strip() or "3"
    random_seeds = random_seeds_entry.get()
    max_msa = max_msa_entry1.get() + ":" + max_msa_entry2.get()
    model_type = model_type_var.get()
    pair_mode = pair_mode_var.get()
    msa_mode = msa_mode_var.get()
    rank = rank_var.get()
    templates = templates_var.get()
    amber = amber_var.get()
    overwrite_existing_results = overwrite_existing_results_var.get()
    zip_choice = zip_var.get()
    ## ADVANCED
    num_model = num_model_entry.get()
    model_order = model_order_entry.get()
    num_ensemble = num_ensemble_entry.get()
    disable_cluster_profile = disable_cluster_profile_var.get()
    templatepath = templatepath_selected.get()
    use_dropout = use_dropout_var.get()
    stop_at_score = stop_at_score_entry.get()
    save_all = save_all_var.get()
    save_recycles = save_recycles_var.get()
    # Create protein prediction command
    prediction_command = [
        conflab_bin, inputpath, outputpath,
        ## BASIC
        "--num-seeds", str(num_seeds),
        "--model-type", model_type,
        "--num-recycle", str(num_recycle),
        "--recycle-early-stop-tolerance", str(recycle_early_stop_tolerance),
        "--msa-mode", msa_mode,
        "--max-msa", str(max_msa),
        "--pair-mode", pair_mode,
        "--rank", rank,
        "--num-relax", str(num_relax),
        ## ADVANCED
        "--num-model", str(num_model),
        "--num-ensemble", str(num_ensemble),
    ]
    if random_seeds_entry.get().strip() != "":
        prediction_command.extend(["--random-seed", random_seeds_entry.get().strip()])
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
    write_output("Running command: " + " ".join(prediction_command))
    safe_status_update("Starting prediction...")
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
            env["PYTHONUNBUFFERED"] = "1"
            process = subprocess.Popen(
                ["caffeinate", "-i", "-m", "-s", "-u"] + prediction_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env
            )
            for line in process.stdout:
                if line.strip():
                    write_output(line.strip())
                    low = line.lower()
                    if "setting max_seq" in low:
                        safe_status_update("Running Multiple Sequence Alignment...")
                    elif "model_1" in low:
                        safe_status_update("Predicting with Model 1...")
                    elif "model_2" in low:
                        safe_status_update("Predicting with Model 2...")
                    elif "model_3" in low:
                        safe_status_update("Predicting with Model 3...")
                    elif "model_4" in low:
                        safe_status_update("Predicting with Model 4...")
                    elif "model_5" in low:
                        safe_status_update("Predicting with Model 5...")
                    elif "relax" in low:
                        safe_status_update("Relaxation step...")
                    elif "finished" in low or "done" in low:
                        safe_status_update("✅ Finished", color="green")
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
            if process and process.returncode == 0:
                safe_status_update("✅ Completed successfully")
            else:
                safe_status_update("❌ Failed", color="red")
            process = None
    threading.Thread(target=run_process, daemon=True).start()
run_button = Button(scrollable_frame, text = "run", command = run_button_command)
run_button.grid(row=11, column=2, padx=10, pady=10)

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
# buttons (end) ==================================================

# status lable ==================================================
status_frame = LabelFrame(scrollable_frame, text="Status", padx=10, pady=10)
status_frame.grid(row=11, column=0, padx=10, pady=10, sticky="w")
status_label = Label(status_frame, text="Idle", width=30, anchor="w", padx=20)
status_label.pack(fill="x")
# status lable ==================================================

# Message widget ==================================================
output_text = Text(scrollable_frame, wrap="word", height=15, state="disabled")
output_text.grid(row=12, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

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
# Message widget(end) ==================================================

# running a task animation ==================================================
loading_frame = LabelFrame(scrollable_frame, width=30, text="Status", padx=10, pady=10)
loading_frame.grid(row=13, column=0, padx=10, pady=10, sticky="w")
loading_label = Label(loading_frame, width=30, anchor="w", padx=20)
loading_label.pack(fill="x")
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
# running a task animation (end) ==================================================

# Footer ==================================================
footer = Frame(root)  
footer.grid(row=4, column=0, columnspan=3, sticky="ew")
footer.grid_columnconfigure(0, weight=1)
footer.grid_columnconfigure(1, weight=1)
footer.grid_columnconfigure(2, weight=1)

#Rights
rights_label = Label(
    footer,
    text="© 2025 Spike Murphy Müller, MIT License, Institute of Biochemistry and Signal Transduction, University-Medical Center Hamburg Eppendorf",
    font=("Arial", 8),
    anchor="w",
    justify="right"
)
rights_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
# Footer (end) ==================================================


# Menu Bar ==================================================
menubar = Menu(root)
root.config(menu=menubar)

# About menu
about_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="About", menu=about_menu)
## About/Disclaimer
def show_about_disclaimer():
    show_about = Toplevel(root)
    show_about.title("About/Disclaimer")
    show_about.geometry(get_centered_geometry(0.6))
    notebook = ttk.Notebook(show_about)
    notebook.pack(expand=True, fill=BOTH)
    info_files = {
        "About": "ABOUT.txt",
        "Disclaimer": "DISCLAIMER.txt",
        "Terms of Use": "TERMS.txt",
        "Privacy Policy": "PRIVACY.txt",
        "Legal Notice": "LEGAL.txt"
    }
    for title, filename in info_files.items():
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=title)
        text = Text(frame, wrap="word", font=("Courier", 10))
        text.pack(expand=True, fill=BOTH, side="left")
        scrollbar = Scrollbar(frame, command=text.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        text.config(yscrollcommand=scrollbar.set)
        try:
            with open(resource_path(filename), "r", encoding="utf-8") as f:
                text.insert(END, f.read())
        except FileNotFoundError:
            text.insert(END, f"{filename} not found.")
        text.config(state="disabled")
about_menu.add_command(label="Licenses", command=show_about_disclaimer)

# Licenses
def resource_path(filename):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath("."), filename)
def show_license():
    show_license = Toplevel(root)
    show_license.title("License")
    show_license.geometry(get_centered_geometry(0.6))
    notebook = ttk.Notebook(show_license)
    notebook.pack(expand=True, fill=BOTH)
    license_files = {
        "ConformationLabStudio (MIT)": "LICENSE_ConformationLabStudio.txt",
        "ColabFold (Third-Party, MIT)": "LICENSE_ColabFold.txt",
        "AlphaFold2 (Third-Party, Apache 2.0)": "LICENSE_AlphaFold2.txt",
    }
    for title, filename in license_files.items():
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=title)
        text = Text(frame, wrap="word", font=("Courier", 10))
        text.pack(expand=True, fill=BOTH, side="left")
        scrollbar = Scrollbar(frame, command=text.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        text.config(yscrollcommand=scrollbar.set)
        try:
            with open(resource_path(filename), "r", encoding="utf-8") as f:
                text.insert(END, f.read())
        except FileNotFoundError:
            text.insert(END, f"{filename} not found.")
        text.config(state="disabled")
about_menu.add_command(label="Licenses", command=show_license)

# Version Notes
def show_version_notes():
    notes = """
ConfigurationLab Studio v1.11.0 - 13.10.2025
-----------------------------------
- automatic implementation with system light/dark mode improvement
- about added
- disclaimer added
- terms of use added
- privacy policy added
- legal notice added
- advanced mode added
- correction of advanced grid remove/show
- not entering sleep mode while running predictions implemented

ConfigurationLab Studio v1.10.0 - 04.10.2025
-----------------------------------
- code clean-up
- button section frames
- windor in front after start
- batch command fixes
- status box
- run animation width fix
- visual enhancements
- info boxes to the left (in frame)
- scrooling fix, don't scroll main frame when in textboxes
- licenses added
- window geometry fix for root & version note & licenses
- test status update syncronised with message box

ConfigurationLab Studio v1.9.0 - 03.10.2025
-----------------------------------
- Rebranding to ConfigurationLab Studio
- new ordering and sectioning for parameters
- three new parameters introduced (--recycle-early-stop-tolerance ,--overwrite-existing-results ,--zip)
- more parameters prepared to introduce with advanced module
- auto added to allowed formatting for automatic value output (--recycle-early-stop-tolerance)
- section frames implemented
- Auth0 Login implemented
    
ShipFold Studio v1.8.0 – 01.10.2025
-----------------------------------
- bug fixes login window
- preparations for ORCID login
- new .py for orcid login window
- new orcid login button
    
ShipFold Studio v1.7.0 – 30.09.2025
-----------------------------------
- login implementation
- system stats menu implemented
- version note window enlarged
- report issue implemented
- updater prepared

ShipFold Studio v1.6.0 – 29.09.2025
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
    version_note = Toplevel(root)
    version_note.title("Version Notes")
    version_note.geometry(get_centered_geometry(0.6))
    frame = Frame(version_note)
    frame.pack(fill="both", expand=True, padx=10, pady=10)
    text = Text(frame, wrap="word", height=15)
    scrollbar = Scrollbar(frame, command=text.yview)
    text.config(yscrollcommand=scrollbar.set)
    text.insert("1.0", notes)
    text.config(state="disabled")
    text.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
about_menu.add_command(label="Version Notes", command=show_version_notes)

# system stats menu
system_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="System", menu=system_menu)
## system stats
def show_system_stats():
    system_stats = Toplevel(root)
    system_stats.title("System Statistics")
    system_stats.geometry("300x150")
    system_stats.attributes('-topmost', True)
    system_stats.update_idletasks()
    screen_width = system_stats.winfo_screenwidth()
    width = system_stats.winfo_width()
    x = screen_width - width
    y = 0
    system_stats.geometry(f"+{x}+{y}")
    cpu_label = Label(system_stats, text="CPU Usage:")
    cpu_label.pack(anchor='w', padx=10, pady=5)
    cpu_progress = ttk.Progressbar(system_stats, orient='horizontal', length=200, mode='determinate', maximum=100)
    cpu_progress.pack(padx=10)
    cpu_percent_label = Label(system_stats, text="0%")
    cpu_percent_label.pack(anchor='e', padx=10)
    ram_label = Label(system_stats, text="RAM Usage:")
    ram_label.pack(anchor='w', padx=10, pady=5)
    ram_progress = ttk.Progressbar(system_stats, orient='horizontal', length=200, mode='determinate', maximum=100)
    ram_progress.pack(padx=10)
    ram_percent_label = Label(system_stats, text="0%")
    ram_percent_label.pack(anchor='e', padx=10)
    # Aktualisierungsfunktion
    def update_stats():
        cpu_pct = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        ram_pct = mem.percent
        cpu_progress['value'] = cpu_pct
        cpu_percent_label.config(text=f"{int(cpu_pct)}%")
        ram_progress['value'] = ram_pct
        ram_percent_label.config(text=f"{int(ram_pct)}%")
        # Alle 1000ms wiederholen
        system_stats.after(1000, update_stats)
    update_stats()
system_menu.add_command(label="System Statistics", command=show_system_stats)

'''# Update Menu
update_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Update", menu=update_menu)
CURRENT_VERSION = "1.7.0"
VERSION_URL = "https://deine-seite.com/version.txt"
def check_for_updates():
    try:
        resp = requests.get(VERSION_URL, timeout=5)
        if resp.status_code == 200:
            data = resp.json()  # falls JSON, sonst resp.text.strip()
            latest = data["version"]
            changelog = data.get("changelog", "")
            download_url = data.get("download", "")
            
            if latest != CURRENT_VERSION:
                if messagebox.askyesno(
                    "Update verfügbar",
                    f"Neue Version {latest} gefunden!\n\nÄnderungen:\n{changelog}\n\nWillst du die neue Version herunterladen?"
                ):
                    import webbrowser
                    webbrowser.open(download_url)
            else:
                messagebox.showinfo("Up to date", f"Du hast die aktuelle Version {CURRENT_VERSION}.")
        else:
            messagebox.showerror("Fehler", "Konnte Versionsdatei nicht laden.")
    except Exception as e:
        messagebox.showerror("Fehler", f"Update-Check fehlgeschlagen:\n{e}")
update_menu.add_command(label="Check for Updates", command=check_for_updates)'''

# Help Menu
help_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Help", menu=help_menu)
## Report Issue
def report_issue():
    subject = "[ConformationLab Studio] Report Issue"
    body = f'''
We are sorry to hear that there is an issue.
Please specify the problem:

    
-----
System Information:
OS: {platform.system()} {platform.release()}
Version: {platform.version()}
Python: {platform.python_version()}
Machine: {platform.machine()}
Processor: {platform.processor()}'''
    mailto_link = f"mailto:conformationlabstudio@gmail.com?subject={subject}&body={body}"
    system = platform.system()
    # Schritt 1: Mailprogramm starten
    if system == "Darwin":  # macOS
        os.system("open -a Mail")  # oder Outlook/Thunderbird
    elif system == "Windows":
        os.system("start outlook")  # falls Outlook Standard ist
    elif system == "Linux":
        os.system("xdg-open mailto:")  # nur Mailprogramm öffnen
    # Schritt 2: Warten
    time.sleep(2)
    # Schritt 3: Mailto-Link öffnen
    webbrowser.open(mailto_link, new=1)
help_menu.add_command(label="Report Issue", command=report_issue)
# Menu Bar (end) ==================================================

update_theme() # light/dark mode
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

'''
python "/Users/spikemurphymuller/ConformationLabGeneration/ConformationLabStudio_v1.10.py"
'''

'''
python '/Users/spikemurphymuller/Library/Mobile Documents/com~apple~CloudDocs/Spike/University/University of Hamburg/Medizinstudium/AG Prof. Dr. M. Jücker/Project_4_ConformationLab/Application Generation/Current version/ConformationLabStudio_v1.11.py'
'''