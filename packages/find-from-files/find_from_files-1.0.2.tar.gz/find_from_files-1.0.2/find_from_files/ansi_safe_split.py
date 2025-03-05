"""Splits an ANSI-colored string into parts of a given visible width.

Function ansi_safe_split() can be used for splitting ANSI-colored strings into
parts of a given visible width.

Typical usage example:

    colored_text = '\x1b[31mThis is \x1b[32mcolored\x1b[43m text\x1b[0m'
    str_part_list = ansi_safe_split(colored_text, 10)
"""

import re
from colorama import Fore, Back, Style
from .constants import ERASE_TO_THE_END_OF_LINE

ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
FORE_COLOR_CODES = [
    Fore.BLACK,
    Fore.BLUE,
    Fore.CYAN,
    Fore.GREEN,
    Fore.MAGENTA,
    Fore.RED,
    Fore.WHITE,
    Fore.YELLOW,
]
BACK_COLOR_CODES = [
    Back.BLACK,
    Back.BLUE,
    Back.CYAN,
    Back.GREEN,
    Back.MAGENTA,
    Back.RED,
    Back.WHITE,
    Back.YELLOW,
]


class ColorCodeState:
    """Used for keeping track of open/not-reset ANSI color codes of a slice."""

    def __init__(self, fore: str = "", back: str = ""):
        self.fore = fore
        self.back = back

    def has_open_codes(self) -> bool:
        if self.fore or self.back:
            return True
        return False


def ansi_safe_split(text, width, one_line=False) -> list[str]:
    """Splits an ANSI-colored string into parts of a given visible width.

    Args:
        text: Input string containing ANSI escape sequences.
        width: Desired visible width per slice.
        one_line: If True, returns only the first slice that fits the width.

    Returns:
        A list of ANSI-colored substrings.
    """
    slices, current_slice, current_length = [], "", 0
    open_color_codes = ColorCodeState()
    index = 0  # index of the next visible character

    def check_open_codes(
        match_str: str, open_codes: ColorCodeState
    ) -> ColorCodeState:
        """Updates the status of ANSI color codes of the line.

        Keeps track of color codes that are open/not-reset, so that they can be
        closed/reset at the end of the slice and opened again at the beginning
        of the next slice.
        """
        if match_str in FORE_COLOR_CODES:
            open_codes.fore = match_str
        if match_str in BACK_COLOR_CODES:
            open_codes.back = match_str
        if match_str == Fore.RESET:
            open_codes.fore = ""
        if match_str == Back.RESET:
            open_codes.back = ""
        if match_str == Style.RESET_ALL:
            open_codes.fore = ""
            open_codes.back = ""
        return open_codes

    for i, char in enumerate(text):
        # Skip if next visible character is not reached
        if i < index:
            continue

        # Check for ANSI escape sequences
        if text[i : i + 2] == "\x1b[":  # ESC + [ = Control Sequence Introducer
            match = ANSI_ESCAPE.match(text, i)
            if match:
                current_slice += match.group()
                index += len(match.group())
                open_color_codes = check_open_codes(
                    match.group(), open_color_codes
                )
                continue

        # Add regular character
        current_slice += char
        current_length += 1
        index += 1

        # If we reach the width limit, store the slice
        if current_length >= width:
            # Reset open color codes at the end of line
            if open_color_codes.has_open_codes():
                current_slice += Style.RESET_ALL + ERASE_TO_THE_END_OF_LINE

            if one_line:
                return [current_slice]
            slices.append(current_slice)
            current_slice, current_length = "", 0

            # Start the next slice with color codes that were left open
            if open_color_codes.has_open_codes():
                current_slice += open_color_codes.back + open_color_codes.fore

    # Append the last slice if not empty
    if current_slice:
        slices.append(current_slice)

    return slices


if __name__ == "__main__":
    colored_text = (
        f"{Fore.RED}This is a {Fore.GREEN}colored{Back.YELLOW} "
        f"text with ANSI codes{Style.RESET_ALL}"
        f"{ERASE_TO_THE_END_OF_LINE}"
    )
    result = ansi_safe_split(colored_text, 10)

    print(colored_text)
    print(repr(colored_text))

    for part in result:
        print(part)

    for part in result:
        print(repr(part))  # Use repr() to visualize ANSI codes
