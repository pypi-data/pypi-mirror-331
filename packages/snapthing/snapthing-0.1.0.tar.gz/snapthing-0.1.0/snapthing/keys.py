from dataclasses import dataclass
from typing import final

@final
class States:
    NOTHING = 0
    SHIFT = 1

@dataclass(frozen=True)
class KeyPress:
    key: str | None = None
    keycode: int | None = None
    state: int = States.NOTHING

    def __post_init__(self):
        assert self.key or self.keycode


def press(key: str, keycode: int | None = None):
    return KeyPress(key=key, keycode=keycode)

def keycode(code: int, key: str | None = None):
    return KeyPress(keycode=code, key=key)

def shift(key: str, keycode: int | None = None):
    return KeyPress(key=key, keycode=keycode, state=States.SHIFT)


@final
class Keys:
    ESCAPE = press('Escape', keycode=24)
    ENTER = press('Return', keycode=36)
    TAB = press('Tab', keycode=23)
    SHIFT_TAB = shift('Tab', keycode=23)
    LEFT = press('Left')
    RIGHT = press('Right')
    UP = press('Up')
    DOWN = press('Down')
    SHIFT_LEFT = shift('Left')
    SHIFT_RIGHT = shift('Right')
    SHIFT_UP = shift('Up')
    SHIFT_DOWN = shift('Down')
    a = press('a')
    b = press('b')
    a = press('a')
    b = press('b')
    c = press('c')
    d = press('d')
    e = press('e')
    f = press('f')
    g = press('g')
    h = press('h')
    i = press('i')
    j = press('j')
    k = press('k')
    l = press('l')
    m = press('m')
    n = press('n')
    o = press('o')
    p = press('p')
    q = press('q')
    r = press('r')
    s = press('s')
    t = press('t')
    u = press('u')
    v = press('v')
    w = press('w')
    x = press('x')
    y = press('y')
    z = press('z')
    A = press('a')
    B = press('b')
    SHIFT_A = shift('A')
    SHIFT_B = shift('B')
    SHIFT_C = shift('C')
    SHIFT_D = shift('D')
    SHIFT_E = shift('E')
    SHIFT_F = shift('F')
    SHIFT_G = shift('G')
    SHIFT_H = shift('H')
    SHIFT_I = shift('I')
    SHIFT_J = shift('J')
    SHIFT_K = shift('K')
    SHIFT_L = shift('L')
    SHIFT_M = shift('M')
    SHIFT_N = shift('N')
    SHIFT_O = shift('O')
    SHIFT_P = shift('P')
    SHIFT_Q = shift('Q')
    SHIFT_R = shift('R')
    SHIFT_S = shift('S')
    SHIFT_T = shift('T')
    SHIFT_U = shift('U')
    SHIFT_V = shift('V')
    SHIFT_W = shift('W')
    SHIFT_X = shift('X')
    SHIFT_Y = shift('Y')
    SHIFT_Z = shift('Z')

