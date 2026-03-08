from AppKit import NSScreen
from tkinter import *
import webview # Mol*Viewer

def get_centered_geometry(scale=0.8):
    # Temporär Tk-Fenster für Bildschirmmaße
    tmp_root = Tk()
    tmp_root.withdraw()
    tmp_root.update_idletasks()
    try:
        # macOS: verfügbare Fläche ohne Menü/Dock
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

def main():
    window_width, window_height, window_x, window_y = get_centered_geometry(0.9)

    webview.create_window(
        title="ConformationLab Studio Mol* Viewer",
        url="https://molstar.org/viewer/",
        width=window_width,
        height=window_height,
        resizable=True,
        x=window_x,
        y=window_y
        )
    webview.start()

if __name__ == "__main__":
    main()