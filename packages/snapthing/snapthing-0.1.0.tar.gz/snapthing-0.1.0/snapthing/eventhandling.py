from collections import defaultdict
import tkinter as tk
from typing import Callable
from .config import ScreenshotActionOption, SnapConfig
from dataclasses import dataclass
from .platforms import Platform
from .keys import KeyPress


@dataclass
class ActionContext:
    action_name: ScreenshotActionOption
    window: tk.Tk
    event: tk.Event
    platform: Platform
    config: SnapConfig

type ActionHandler = Callable[[ActionContext], None]

_action_handlers = defaultdict(list)

def onaction(name: str):
    def _deco(f: ActionHandler):
        _action_handlers[name].append(f)
        return f
    return _deco

def action(f: ActionHandler):
    return onaction(f.__name__.replace('_', '-'))(f)

@dataclass
class App:
    config: SnapConfig
    window: tk.Tk
    platform: Platform

    def __post_init__(self):
        self._bindings = defaultdict(set)
        self.window.bind('<Key>', self._handle_key)

        for _action, trigger in self.config.shortcuts:
            self.assign(_action, trigger)


    def assign(
        self, 
        action: str, 
        key: KeyPress
    ):
        self._bindings[key].add(action)

    def _handle_key(self, event: tk.Event):
        for key, actions in self._bindings.items():
            if event.keycode != key.keycode and event.keysym != key.key:
                continue

            if event.state != key.state:
                continue

            for action in actions:
                self._exec_action(action, event)

    def _exec_action(self, name: str, event: tk.Event):
        ctx = ActionContext(
            action_name=name,
            window=self.window,
            event=event,
            platform=self.platform,
            config=self.config, 
        )
        for handler in _action_handlers[name]:
            handler(ctx)


