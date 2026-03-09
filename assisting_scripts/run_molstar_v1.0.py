APP_NAME = "ConformationLab Studio"
SCRIPT_NAME = "MolStar Viewer"
APP_VERSION = "1.1.0"
APP_AUTHOR = "Spike Murphy Müller"

from tkinter import *
import webview

def main():
    window_width, window_height, window_x, window_y = get_centered_geometry(0.9)

    # create webview window for mol* viewer
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


def get_centered_geometry(scale=0.8):
    # Create temporary window
    tmp_root = Tk()
    # Hide window
    tmp_root.withdraw()
    # Process pending GUI events
    tmp_root.update_idletasks()
    try:
        from AppKit import NSScreen
        # Create visible fraim
        frame = NSScreen.mainScreen().visibleFrame()
        # Set dimentions
        screen_width = int(frame.size.width)
        screen_height = int(frame.size.height)
    except ImportError:
        # Fallback to full screen
        screen_width = tmp_root.winfo_screenwidth()
        screen_height = tmp_root.winfo_screenheight()

    # destroy temporary window (was necessary for getting dimentions)
    tmp_root.destroy()

    # set window dimensions
    window_width = int(screen_width * scale)
    window_height = int(screen_height * scale)
    window_x = (screen_width - window_width) // 2
    window_y = (screen_height - window_height) // 2
    return window_width, window_height, window_x, window_y


if __name__ == "__main__":
    main()
