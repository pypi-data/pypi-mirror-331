import tkinter as tk
import pyautogui
from io import BytesIO
from collections import deque
from .config import SnapConfig
from .platforms import LinuxXClip
from .eventhandling import ActionContext, onaction, App, action

platform = LinuxXClip()
platform.assert_dependencies()

def screenshot(root: tk.Tk) -> BytesIO:
    w = root.winfo_width()
    h = root.winfo_height()
    y = root.winfo_y()
    x = root.winfo_x()
    
    # Capture the screenshot of the specified region
    # TODO: play the clipboard noise
    # TODO: support other formats -- png, webp, etc.
    image = pyautogui.screenshot(region=(x, y, w, h))
    output = BytesIO()
    image.save(output, format="PNG")
    _ = output.seek(0)
    return output


@action
def copy_image(ctx: ActionContext):
    ctx.platform.copy_image_to_clipboard(screenshot(ctx.window))
    ctx.window.destroy()

@action
def copy_ocr(ctx: ActionContext):
    text = ctx.platform.extract_image_text_ocr(screenshot(ctx.window))
    platform.copy_text_to_clipboard(text)
    ctx.window.destroy()


@onaction('exit')
def exit_window(ctx: ActionContext):
    ctx.window.destroy()


def resize(root: tk.Tk, dx: int, dy: int):
    w = root.winfo_width()
    h = root.winfo_height()
    y = root.winfo_y()
    x = root.winfo_x()

    root.geometry('%dx%d+%d+%d' % (w + dx, h + dy, x - 1, y - 28))

@onaction("resize-left")
def resize_left(ctx: ActionContext):
    resize(ctx.window, -ctx.config.resize_increment, 0)

@onaction("resize-right")
def resize_right(ctx: ActionContext):
    resize(ctx.window, ctx.config.resize_increment, 0)

@onaction("resize-down")
def resize_down(ctx: ActionContext):
    resize(ctx.window, 0, ctx.config.resize_increment)

@onaction("resize-up")
def resize_up(ctx: ActionContext):
    resize(ctx.window, 0, -ctx.config.resize_increment)

def resize_absolute(root: tk.Tk, w: int, h: int):
    y = root.winfo_y()
    x = root.winfo_x()
    root.geometry('%dx%d+%d+%d' % (w, h, x - 1, y - 28))

def configure_window_size_quickswitch(config: SnapConfig, root: tk.Tk):
    sizes = deque(config.quick_change_dimensions)

    def next_window_size(_: ActionContext):
        sizes.rotate(1)
        w, h = sizes[0]
        resize_absolute(root, w, h)

    def prev_window_size(_: ActionContext):
        sizes.rotate(-1)
        w, h = sizes[0]
        resize_absolute(root, w, h)

    def default_window_size(_: ActionContext):
        w, h = config.start_dimentions
        resize_absolute(root, w, h)

    _ = action(next_window_size)
    _ = action(prev_window_size)
    _ = action(default_window_size)


def translate(root: tk.Tk, dx: int, dy: int):
    w = root.winfo_width()
    h = root.winfo_height()
    y = root.winfo_y()
    x = root.winfo_x()

    root.geometry('%dx%d+%d+%d' % (w, h, x + dx - 1, y + dy - 28))

@action
def translate_right(ctx: ActionContext):
    translate(ctx.window, ctx.config.translate_increment, 0)

@action
def translate_left(ctx: ActionContext):
    translate(ctx.window, -ctx.config.translate_increment, 0)

@action
def translate_down(ctx: ActionContext):
    translate(ctx.window, 0, ctx.config.translate_increment)

@action
def translate_up(ctx: ActionContext):
    translate(ctx.window, 0, -ctx.config.translate_increment)


def open_screenshot_window(config: SnapConfig):
    root: tk.Tk = tk.Tk()
    _ = root.attributes('-topmost', True)
    root.wait_visibility(root)
    root.wm_attributes('-alpha',0.1)

    w, h = config.start_dimentions

    # get screen width and height
    ws = root.winfo_screenwidth() # width of the screen
    hs = root.winfo_screenheight() # height of the screen

    # calculate x and y coordinates for the Tk root window
    if config.start_position == 'center':
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
    elif config.start_position == "center-at-cursor":
        cursor = pyautogui.position()
        x = cursor.x - w/2
        y = cursor.y - h/2
    else:
        raise RuntimeError("unexpected start_position config")


    # set the dimensions of the screen 
    # and where it is placed
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))


    root.focus_force()  # Ensure the window has focus

    startx, starty, endx, endy = (0, 0, 0, 0)
    
    def onpress(e: tk.Event):
        nonlocal startx, starty
        startx, starty = (e.x, e.y)

    def onrelease(e: tk.Event):
        nonlocal endx, endy
        endx, endy = (e.x, e.y)

    def onmove(e: tk.Event):
        w = root.winfo_width()
        h = root.winfo_height()
        y = root.winfo_y()
        x = root.winfo_x()

        # absolute co-ordinates of mouse on the screen
        absx = x + e.x
        absy = y + e.y
        # position is set to the top left corner, so we need to 
        # adjust by the window size to center
        posx = absx - startx
        posy = absy - starty

        root.geometry('%dx%d+%d+%d' % (w, h, posx, posy))

    _ = root.bind("<ButtonPress-1>", onpress)
    _ = root.bind("<ButtonRelease-1>", onrelease)
    _ = root.bind("<B1-Motion>", onmove)

    configure_window_size_quickswitch(config, root)

    _ = App(
        config=config,
        platform=LinuxXClip(),
        window=root
    )

    root.mainloop()
