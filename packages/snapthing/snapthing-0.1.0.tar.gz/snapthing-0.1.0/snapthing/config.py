from dataclasses import dataclass, field
from typing import Literal
from .keys import KeyPress, press, Keys

type StartPositionOption = Literal[
        "center",
        "center-at-cursor"
]

type ScreenshotActionOption = Literal[
        "copy-image",
        "close-window",
        "resize-left",
        "resize-right",
        "resize-up",
        "resize-down",
        "translate-left",
        "translate-right",
        "translate-up",
        "translate-down",
        "prev-window-size",
        "next-window-size",
        "reset-default-window-size",
]

type Key = str

def default_actions():
    return [
        ("exit", press('q')),
        ("exit", Keys.ESCAPE),
        ("copy-image", Keys.ENTER),
    ]

def default_quickchange_sizes():
    return [
        (400, 400),
        (600, 300),
        (1200, 720),
        (1000, 100),
        (1920, 1080),
    ]


@dataclass
class SnapConfig:
    start_dimentions: tuple[int, int]
    shortcuts: list[tuple[str, KeyPress]] = field(default_factory=default_actions)
    window_alpha: float = 0.1
    start_position: StartPositionOption = "center-at-cursor"
    resize_increment: int = 20
    translate_increment: int = 20
    quick_change_dimensions: list[tuple[int, int]] = field(default_factory=default_quickchange_sizes)

    def __post_init__(self):
        if not (0 <= self.window_alpha <= 1):
            raise ValueError("window_alpha must be set between 0 and 1")
