"""Simple CLI application for searching keywords/phrases or regular expression
patterns in text files.

This script can be useful, e.g., for analyzing log files. When used without the
--regex flag, it traverses through directories starting from the
<base_directory> and prints the name of the file containing <search_string> and
the line that it is on. This is handy if you want to quickly find the files
that contain the string you are looking for. When used with the --regex flag,
it searches for the <search_string> with Python regular expression function
re.findall() in the files, and prints a summary containing the matches and
their number. This allows you to search for all occurrences of a pattern in
files. If the --whole-line flag is used, the whole line is printed instead of
just the match (does nothing without the --regex flag).
"""

import os
import re
import argparse
import json
from colorama import Fore, Back, Style, init as colorama_init, deinit as colorama_deinit
from typing import Dict, TextIO, TypedDict
from find_from_files.ansi_safe_split import ansi_safe_split
from find_from_files.is_binary import is_binary
from find_from_files.constants import ERASE_TO_THE_END_OF_LINE

SINGLE_INDENT_WIDTH = 4
INDENT_LEVEL_FOLDER_FIRST_LINE = 0
INDENT_LEVEL_FOLDER_NEXT_LINES = SINGLE_INDENT_WIDTH
INDENT_LEVEL_FILE_FIRST_LINE = SINGLE_INDENT_WIDTH
INDENT_LEVEL_FILE_NEXT_LINES = SINGLE_INDENT_WIDTH * 2
INDENT_LEVEL_MATCH_FIRST_LINE = SINGLE_INDENT_WIDTH * 2
INDENT_LEVEL_MATCH_NEXT_LINES = SINGLE_INDENT_WIDTH * 3


def get_terminal_width():
    try:
        columns, _ = os.get_terminal_size()
    except OSError:
        columns = 80
    return columns


def get_indented_str(
    string, first_line_indent_width, indent_width, line_width
) -> str:
    first_line = ansi_safe_split(string, line_width - first_line_indent_width)[
        0
    ]
    output = " " * first_line_indent_width + first_line
    rest = ansi_safe_split(string[len(first_line) :], line_width - indent_width)
    for line in rest:
        output += " " * indent_width + line
    return output


def print_indented(string, first_line_indent_width, indent_width, line_width):
    print(
        get_indented_str(
            string, first_line_indent_width, indent_width, line_width
        )
    )


def traverse_directories(
    base_directory,
    file_suffixes,
    skip_prefixes,
    search_string,
    whole_line,
    quiet,
    quieter,
    search_func,
):
    """Goes through directories starting from base_directory and applies
    search_func function to each file having one of the file_suffixes.

    Args:
        base_directory: The directory to start the search from.
        file_suffixes: List of file suffixes to skip.
        skip_prefixes: List of directory prefixies. A directory is skipped if
            it starts with one of these.
        search_string: String/regexp to search for.
        whole_line: Boolean indicating whether to print the whole matched line
            or just a count and line numbers.
        quiet: Boolean to indicate quiet mode (skipped folders or files are not
            printed).
        quieter: Boolean to indicate quieter mode (in addition to quiet mode,
            only files with matches are printed).
        search_func: Function to use for checking the files.
    """

    def check_file(root, file_path, search_func, only_matches=False):
        file_path = os.path.join(root, file)
        match_output = ""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                match_output = search_func(search_string, f, whole_line)
        except OSError as e:
            print(f"ERROR reading {file_path}: {e}")
        if not only_matches or (only_matches and match_output):
            print_indented(
                f"{Fore.BLUE}Checking file: {Fore.YELLOW}"
                f"{file_path}{Style.RESET_ALL}",
                INDENT_LEVEL_FILE_FIRST_LINE,
                INDENT_LEVEL_FILE_NEXT_LINES,
                columns,
            )
            if match_output:
                print(match_output)

    if skip_prefixes is not None:
        skip_prefixes = tuple(skip_prefixes)
    if file_suffixes is not None:
        file_suffixes = tuple(file_suffixes)
    sub_dirs_to_skip = []

    for root, dirs, files in os.walk(base_directory):
        # Skip folders that don't start with any of the skip_prefixes
        dirs.sort()
        files.sort()
        columns = get_terminal_width()
        if skip_prefixes is not None and len(skip_prefixes) > 0:
            if os.path.basename(root).startswith(skip_prefixes):
                sub_dirs_to_skip.extend(dirs)
                if not quiet:
                    print_indented(
                        f"{Fore.RED}Skipping folder: {Fore.YELLOW}"
                        f"{root}{Style.RESET_ALL}",
                        INDENT_LEVEL_FOLDER_FIRST_LINE,
                        INDENT_LEVEL_FOLDER_NEXT_LINES,
                        columns,
                    )
                continue
            elif os.path.basename(root) in sub_dirs_to_skip:
                sub_dirs_to_skip.remove(os.path.basename(root))
                sub_dirs_to_skip.extend(dirs)
                continue
        print_indented(
            f"{Fore.GREEN}Checking folder: {Fore.YELLOW}{root}"
            f"{Style.RESET_ALL}",
            INDENT_LEVEL_FOLDER_FIRST_LINE,
            INDENT_LEVEL_FOLDER_NEXT_LINES,
            columns,
        )

        for file in files:
            file_path = os.path.join(root, file)
            if is_binary(open(file_path, "rb").read(2048)):
                if not quiet:
                    print_indented(
                        f"{Fore.RED}Skipping file: {Fore.YELLOW}"
                        f"{file_path} {Fore.WHITE}(probably binary)"
                        f"{Style.RESET_ALL}",
                        INDENT_LEVEL_FILE_FIRST_LINE,
                        INDENT_LEVEL_FILE_NEXT_LINES,
                        columns,
                    )
                continue
            if file_suffixes is not None and len(file_suffixes) > 0:
                if file.endswith(file_suffixes):
                    check_file(root, file, search_func, quieter)
                else:
                    if not quiet:
                        print_indented(
                            f"{Fore.RED}Skipping file: {Fore.YELLOW}"
                            f"{file_path}{Style.RESET_ALL}",
                            INDENT_LEVEL_FILE_FIRST_LINE,
                            INDENT_LEVEL_FILE_NEXT_LINES,
                            columns,
                        )
            else:
                check_file(root, file, search_func, quieter)


def color_matches(string, matches):
    for match in matches:
        string = string.replace(match, f"{Back.RED}{match}{Style.RESET_ALL}")
    return string


def find_folders_with_string(search_string: str, file: TextIO, _) -> str:
    columns = get_terminal_width()
    output = ""
    for i, line in enumerate(file):
        if search_string in line:
            output += get_indented_str(
                f"Found on line {i+1}: "
                f"{color_matches(line.strip(), [search_string])}"
                f"{ERASE_TO_THE_END_OF_LINE}",
                INDENT_LEVEL_MATCH_FIRST_LINE,
                INDENT_LEVEL_MATCH_NEXT_LINES,
                columns,
            )
            break
    return output


def regex_search_with_string(
    search_string: str, file: TextIO, whole_line: bool
) -> str:
    columns = get_terminal_width()
    output = ""

    class Match(TypedDict):
        number_of_occurrences: int
        line_numbers: list[int]

    def get_whole_lines(matches: dict[str, Match]):
        local_output = get_indented_str(
            f"{Fore.GREEN}{len(matches)} line(s) found:" f"{Style.RESET_ALL}",
            INDENT_LEVEL_MATCH_FIRST_LINE,
            INDENT_LEVEL_MATCH_NEXT_LINES,
            columns,
        )
        for match in matches:
            line_number = str(matches[match]["line_numbers"][0])
            local_output += "\n" + get_indented_str(
                f"{line_number}: {match}{ERASE_TO_THE_END_OF_LINE}",
                INDENT_LEVEL_MATCH_FIRST_LINE,
                INDENT_LEVEL_MATCH_FIRST_LINE + (len(line_number) + 2),
                columns,
            )
        return local_output

    pattern = re.compile(search_string)
    matches: Dict[str, Match] = {}
    for i, line in enumerate(file):
        new_matches = pattern.findall(line)
        line_number = i + 1
        if new_matches:
            if whole_line:
                match_string = color_matches(line.strip(), new_matches)
                matches[match_string] = {
                    "number_of_occurrences": len(new_matches),
                    "line_numbers": [line_number],
                }
                continue
            else:
                for match in new_matches:
                    if match not in matches:
                        matches[match] = {
                            "number_of_occurrences": 1,
                            "line_numbers": [line_number],
                        }
                    else:
                        matches[match]["number_of_occurrences"] += 1
                        matches[match]["line_numbers"].append(line_number)

    if len(matches) > 0:
        if whole_line:
            output += get_whole_lines(matches)
        else:
            matches_string = f"Matches: {json.dumps(matches)}"
            output += get_indented_str(
                matches_string,
                INDENT_LEVEL_MATCH_FIRST_LINE,
                INDENT_LEVEL_MATCH_NEXT_LINES,
                columns,
            )
    return output


def main():
    parser = argparse.ArgumentParser(
        prog="find-from-files",
        description="""
            This script can be useful, e.g., for analyzing log files. When used
            without the --regex flag, it traverses through directories starting
            from the <base_directory> and prints the name of the file
            containing <search_string> and the line that it is on. This is
            handy if you want to quickly find the files that contain the string
            you are looking for. When used with the --regex flag, it searches
            for the <search_string> with Python regular expression function
            re.findall() in the files, and prints a summary containing the
            matches and their number. This allows you to search for all
            occurrences of a pattern in files. If the --whole-line flag is
            used, the whole line is printed instead of just the match (does
            nothing without the --regex flag).
        """,
    )

    parser.add_argument(
        "base_directory", help="Base directory to start the " "search from."
    )
    parser.add_argument("search_string", help="String/regex to search for.")
    parser.add_argument(
        "-l",
        "--whole-line",
        action="store_true",
        help="Search for the whole line containing the search string. "
        "Only works with the --regexp flag.",
    )
    parser.add_argument(
        "-r",
        "--regexp",
        action="store_true",
        help="Search using regular expression.",
    )
    parser.add_argument(
        "-s",
        "--suffix",
        nargs="*",
        default=None,
        help="File suffix to search for. Files without this suffix will be "
        "skipped.",
    )
    parser.add_argument(
        "-S",
        "--skip",
        nargs="*",
        default=None,
        help="Skip folders that start with this prefix.",
    )
    parser.add_argument(
        "-a",
        "--no-ansi",
        action="store_true",
        help="Do not use ANSI codes for output. Redirections never contain "
        "ANSI codes.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Do not print skipped folders or files.",
    )
    parser.add_argument(
        "-qq",
        "--quieter",
        action="store_true",
        help="Do not print skipped folders or files, and only print the files "
        "that contain the search string/pattern.",
    )

    args = parser.parse_args()

    if args.base_directory is None:
        print("No base directory!")
        exit(1)

    if args.search_string is None:
        print("No search string!")
        exit(1)

    if args.no_ansi:
        Fore.GREEN = ""
        Fore.YELLOW = ""
        Fore.BLUE = ""
        Fore.RED = ""
        Back.RED = ""
        Style.RESET_ALL = ""

    if args.quieter:
        args.quiet = True

    search_func = None
    if args.regexp:
        search_func = regex_search_with_string
    else:
        search_func = find_folders_with_string
    traverse_directories(
        args.base_directory,
        args.suffix,
        args.skip,
        args.search_string,
        args.whole_line,
        args.quiet,
        args.quieter,
        search_func,
    )


if __name__ == "__main__":
    colorama_init()
    main()
    colorama_deinit()
