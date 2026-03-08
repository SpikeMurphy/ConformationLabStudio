from pytest import raises, fail

from ConformationLabStudio import *
import ConformationLabStudio


def test_configure_grid():
    with raises (ValueError):
        configure_grid(1)
    with raises (ValueError):
        configure_grid("string")
    with raises (ValueError):
        configure_grid(False)


def test_get_centered_geometry():
    with raises (ValueError):
        get_centered_geometry(-1)
    with raises (ValueError):
        get_centered_geometry(2)
    with raises (ValueError):
        get_centered_geometry(False)
    # does not raise error with true as true = 1
    with raises (TypeError):
        get_centered_geometry("string")


def test_get_app_paths():
    ...


def test_create_validation_commands():
    with raises (ValueError):
        create_validation_commands(1)
    with raises (ValueError):
        create_validation_commands("string")
    with raises (ValueError):
        create_validation_commands(False)

    def test_only_numbers():
        ...

    def test_numbers_or_auto():
        ...

    def test_numbers_and_commas():
        ...


def test_configure_header_frame():
    frame = Frame()

    # To few or to many arguments
    with raises (ValueError):
        configure_header_frame(frame, 1)
    with raises (ValueError):
        configure_header_frame(frame, False)

    # Test second argumanet
    with raises (ValueError):
        configure_header_frame(1, "correct_string")
    with raises (ValueError):
        configure_header_frame("string", "correct_string")
    with raises (ValueError):
        configure_header_frame(False, "correct_string")

    # To few or to many arguments
    with raises (TypeError):
        configure_header_frame(frame)
    with raises (TypeError):
        configure_header_frame("correct_string")
    with raises (TypeError):
        configure_header_frame()
    with raises (TypeError):
        configure_header_frame(frame, "correct_string", "correct_string")


def test_on_global_mousewheel():
    class TestEvent:
        def __init__(self, x=0, y=0, delta=120):
            self.x_root = x
            self.y_root = y
            self.delta = delta
    event = TestEvent()
    window = Tk()
    canvas = Canvas()

    with raises (ValueError):
        on_global_mousewheel(event, 1, canvas)
    with raises (ValueError):
        on_global_mousewheel(event, "string", canvas)
    with raises (ValueError):
        on_global_mousewheel(event, False, canvas)
    with raises (ValueError):
        on_global_mousewheel(event, window, 1)
    with raises (ValueError):
        on_global_mousewheel(event, window, "string")
    with raises (ValueError):
        on_global_mousewheel(event, window, False)

def test_create_path_selectors():
    ...

def test_ensure_conflab_env():
    ...

def test_build_basic_mode():
    frame = Frame()

    path_selectors = {
        "input": ("", lambda: None),
        "output": ("", lambda: None),
    }
    validation_cmd = {
        "vcmd_numbers": ("", "%P"),
        "vcmd_numbers_or_auto": ("", "%P"),
        "vcmd_numbers_commas": ("", "%P"),
    }

    try:
        build_basic_mode(frame, path_selectors, validation_cmd)
    except Exception:
        fail("Exception was raised unexpectedly")

    with raises (AttributeError):
        build_basic_mode("string", path_selectors, validation_cmd)
    with raises (AttributeError):
        build_basic_mode(1, path_selectors, validation_cmd)
    with raises (AttributeError):
        build_basic_mode(("", ""), path_selectors, validation_cmd)

    with raises (TypeError):
        build_basic_mode(frame, "string", validation_cmd)
    with raises (TypeError):
        build_basic_mode(frame, 1, validation_cmd)
    with raises (TypeError):
        build_basic_mode(frame, ("", ""), validation_cmd)
    with raises (TypeError):
        build_basic_mode(frame, path_selectors, "string")
    with raises (TypeError):
        build_basic_mode(frame, path_selectors, 1)
    with raises (TypeError):
        build_basic_mode(frame, path_selectors, ("", ""))

    with raises (KeyError):
        build_basic_mode(frame, {}, {})


def test_build_advanced_mode():
    frame = Frame()

    path_selectors = {
        "template": ("", lambda: None),
    }
    validation_cmd = {
        "vcmd_numbers": ("", "%P"),
        "vcmd_numbers_or_auto": ("", "%P"),
        "vcmd_numbers_commas": ("", "%P"),
    }

    try:
        build_advanced_mode(frame, path_selectors, validation_cmd)
    except Exception:
        fail("Exception was raised unexpectedly")

    with raises (AttributeError):
         build_advanced_mode("string", path_selectors, validation_cmd)
    with raises (AttributeError):
         build_advanced_mode(1, path_selectors, validation_cmd)
    with raises (AttributeError):
         build_advanced_mode(("", ""), path_selectors, validation_cmd)

    with raises (TypeError):
         build_advanced_mode(frame, "string", validation_cmd)
    with raises (TypeError):
         build_advanced_mode(frame, 1, validation_cmd)
    with raises (TypeError):
         build_advanced_mode(frame, ("", ""), validation_cmd)
    with raises (TypeError):
         build_advanced_mode(frame, path_selectors, "string")
    with raises (TypeError):
         build_advanced_mode(frame, path_selectors, 1)
    with raises (TypeError):
         build_advanced_mode(frame, path_selectors, ("", ""))

    with raises (KeyError):
         build_advanced_mode(frame, {}, {})


def test_advanced_toggle():
    window = Tk()
    frame = Frame()
    bool = BooleanVar(value=False)

    try:
        advanced_toggle(window, frame, frame, bool)
    except Exception:
        fail("Exception was raised unexpectedly")
    
    with raises (AttributeError):
        advanced_toggle(1, frame, frame, bool)
    with raises (AttributeError):
        advanced_toggle("string", frame, frame, bool)

    with raises (AttributeError):
        advanced_toggle(window, 1, frame, bool)
    with raises (AttributeError):
        advanced_toggle(window, "string", frame, bool)

    # second frame not used in function alone but in subfunction
    try:
        advanced_toggle(window, frame, 1, bool)
    except Exception:
        fail("Exception was raised unexpectedly")
    try:
        advanced_toggle(window, frame, "string", bool)
    except Exception:
        fail("Exception was raised unexpectedly")

    with raises (AttributeError):
        advanced_toggle(window, frame, frame, 1)
    with raises (AttributeError):
        advanced_toggle(window, frame, frame, "string")


def test_build_clear_button():
    frame = Frame()
    state = {}

    with raises (AttributeError):
        build_clear_button(1, state)
    with raises (AttributeError):
        build_clear_button("string", state)


def test_clear_button_command():
    with raises(KeyError):
        clear_button_command({})


def test_build_cancel_button():
    frame = Frame()
    state = {}

    with raises (AttributeError):
        build_cancel_button(1, state)
    with raises (AttributeError):
        build_cancel_button("string", state)


def test_cancel_process():
    ...


def test_build_molstar_button():
    frame = Frame()
    state = {}

    with raises (AttributeError):
        build_molstar_button(1, state)
    with raises (AttributeError):
        build_molstar_button("string", state)
        
def test_molstar_button_command():
    with raises(KeyError):
        molstar_button_command({})


def test_build_run_button():
    frame = Frame()
    state = {}

    with raises (AttributeError):
        build_run_button(1, state)
    with raises (AttributeError):
        build_run_button("string", state)


def test_safe_status_update():
    label = Label()

    safe_status_update(label, "test")
    assert label.cget("text") == "test"

    safe_status_update(label, 1)
    assert label.cget("text") == "1"


def test_write_output():
    ...


def test_run_button_command():
    with raises(KeyError):
        run_button_command({})

    with raises(TypeError):
        run_button_command(1)
    with raises(TypeError):
        run_button_command("string")
    with raises(TypeError):
        run_button_command(("string", "string"))


def test_run_process():
    with raises(NameError):
        run_process({})

    with raises(NameError):
        run_process(1)
    with raises(NameError):
        run_process("string")


def test_start_loading_animation():
    loading_label = Label()
    loading_label.loading_animation_running = False

    start_loading_animation(loading_label)
    assert loading_label.loading_animation_running == True


def test_stop_loading_animation():
    loading_label = Label()
    loading_label.loading_animation_running = True

    stop_loading_animation(loading_label)
    assert loading_label.loading_animation_running == False


def test_apply_hover_effect():
    ...

def test_hover_effect():
    button = Button()
        
    try:
        hover_effect(button, "#868686")
    except Exception:
        fail("Exception was raised unexpectedly")

    with raises(AttributeError):
        hover_effect(1, "blue")
    with raises(AttributeError):
        hover_effect("string", "blue")


def test_build_output_wiget():
    frame = Frame()

    with raises(AttributeError):
        build_output_wiget(1)
    with raises(AttributeError):
        build_output_wiget("string")


def test_build_status_frame():
    frame = Frame()

    with raises(AttributeError):
        build_status_frame(1)
    with raises(AttributeError):
        build_status_frame("string")


def test_build_loading_frame():
    frame = Frame()

    with raises(AttributeError):
        build_loading_frame(1)
    with raises(AttributeError):
        build_loading_frame("string")


def test_configure_footer():
    frame = Frame()

    with raises(AttributeError):
        configure_footer(1)
    with raises(AttributeError):
        configure_footer("string")

def test_bind_shortcuts():
    window = Tk()

    try:
        bind_shortcuts(window, {})
    except Exception:
        fail("Exception was raised unexpectedly")

    with raises(AttributeError):
        bind_shortcuts(1, {})
    with raises(AttributeError):
        bind_shortcuts("string", {})

def test_create_shortcut_overlay():
    window = Tk()

    try:
        configure_footer(window)
    except Exception:
        fail("Exception was raised unexpectedly")

    with raises(AttributeError):
        configure_footer(1)
    with raises(AttributeError):
        configure_footer("string")

def test_bind_shortcut_overlay():
    window = Tk()

    try:
        bind_shortcut_overlay(window)
    except Exception:
        fail("Exception was raised unexpectedly")

    with raises(AttributeError):
        bind_shortcut_overlay(1)
    with raises(AttributeError):
        bind_shortcut_overlay("string")

def test_build_menubar():
    window = Tk()

    try:
        build_menubar(window)
    except Exception:
        fail("Exception was raised unexpectedly")

    with raises(AttributeError):
        build_menubar(1)
    with raises(AttributeError):
        build_menubar("string")

def test_configure_about():
    ...

def test_configure_system():
    ...

def test_configure_help():
    ...

def test_resource_path():
    ...

def test_show_about_disclaimer():
    ...

def test_show_license():
    ...

def test_show_version_notes():
    ...

def test_show_system_stats():
    ...

def test_report_issue():
    ...

def test_on_closing():
    window = Tk()
    ConformationLabStudio.process = subprocess.Popen(["python", "-c", "import time; time.sleep(10)"])
    
    with raises(AttributeError):
        on_closing(1)

    with raises(AttributeError):
        on_closing("string")

    on_closing(window)
    with raises(TclError):
            window.winfo_exists()