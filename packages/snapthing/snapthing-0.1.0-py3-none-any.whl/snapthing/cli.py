from .snap import open_screenshot_window
from .keys import Keys
from .config import SnapConfig


vim_keybinds = [
        ("copy-image", Keys.ENTER),
        ("exit", Keys.ESCAPE),
        ("exit", Keys.q),
        ("resize-left", Keys.SHIFT_H),
        ("resize-right", Keys.SHIFT_L),
        ("resize-down", Keys.SHIFT_J),
        ("resize-up", Keys.SHIFT_K),
        ("resize-left", Keys.SHIFT_LEFT),
        ("resize-right", Keys.SHIFT_RIGHT),
        ("resize-down", Keys.SHIFT_DOWN),
        ("resize-up", Keys.SHIFT_UP),
        ("translate-left", Keys.h),
        ("translate-right", Keys.l),
        ("translate-down", Keys.j),
        ("translate-up", Keys.k),
        ("translate-left", Keys.LEFT),
        ("translate-right", Keys.RIGHT),
        ("translate-down", Keys.DOWN),
        ("translate-up", Keys.UP),
        ("next-window-size", Keys.TAB),
        ("prev-window-size", Keys.SHIFT_TAB),
        ("copy-ocr", Keys.c)
]

config = SnapConfig(
        start_dimentions=(800, 400),
        window_alpha=0.3,
        start_position="center-at-cursor",
        shortcuts=vim_keybinds,
        resize_increment = 15,
        translate_increment = 15,
)


def main():
    open_screenshot_window(config)
