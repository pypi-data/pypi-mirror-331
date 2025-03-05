import enum
from typing import Any

from colorama import Fore

colors = [30, 31, 32, 33, 34, 35, 36, 37, 90, 91, 92, 93, 94, 95, 96, 97]
styles = [1, 2, 3, 4]


class Colors(enum.Enum):
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    LIGHT_GRAY = 37
    DARK_GRAY = 90
    BRIGHT_RED = 91
    BRIGHT_GREEN = 92
    BRIGHT_YELLOW = 93
    BRIGHT_BLUE = 94
    BRIGHT_MAGENTA = 95
    BRIGHT_CYAN = 96
    WHITE = 97


class Styles(enum.Enum):
    BOLD = 1
    REGULAR = 2
    ITALIC = 3
    UNDERLINE = 4


def cprint(message: Any, color: int = Colors.WHITE.value, style: int = Styles.REGULAR.value, fore: Fore = None) -> None:
    if fore:
        color_message = f"{fore}{message}\033[0m"
    else:
        color_message = f"\033[{style};{color}m{message}\033[0m"
    print(color_message, flush=True)
