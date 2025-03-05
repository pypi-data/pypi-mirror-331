"""Detects if a given byte sequence is binary or text.

Function is_binary can be used for detecting whether the given byte sequence is
binary or not. It tries first decoding the data using UTF-8, UTF-16, and
UTF-32. If the sequence decodes successfully, it's considered text. If decoding
fails, the sequence is checked for non-printable characters. If the percentage
of these characters is above 30%, the sequence is considered binary. Otherwise,
chardet is used to detect the encoding. If chardet detects an encoding and is
confident enough, the sequence is considered text. Otherwise, it is considered
binary.

Typical usage example:

    if is_binary(open(file_path, "rb").read(2048)):
        print('file is binary')
"""

import chardet


def is_binary(data: bytes) -> bool | None:
    """Detects if a given byte sequence sample is binary or text.

    Tries first decoding the sequence using UTF-8, UTF-16, and UTF-32. If it
    decodes successfully, it is considered text. If decoding fails, the
    sequence is checked for non-printable characters. If the percentage of
    these characters is above 30%, the sequence is considered binary.
    Otherwise, chardet is used to detect the encoding. If chardet detects an
    encoding and is confident enough, the sequence is considered text.
    Otherwise, it is considered binary.

    Args:
        data: The byte sequence to be checked.

    Returns:
        True if the data sample is binary, False if it's text, None if it's
        empty.
    """
    # Sample is empty
    if len(data) == 0:
        return None

    # Attempt decoding in UTF encodings
    for encoding in ["utf-8", "utf-16", "utf-32"]:
        try:
            data.decode(encoding)
            return False
        except UnicodeDecodeError:
            pass  # Try next encoding

    # Heuristic: Check for non-printable bytes (based on Unix file command
    # behavior, see: https://stackoverflow.com/a/7392391).
    # Define a set of text-like characters (ASCII control + printable ASCII
    # + Latin-1 - DEL)
    textchars = bytearray(
        {7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7F}
    )
    nontext_ratio = float(len(data.translate(None, textchars))) / len(data)
    if nontext_ratio > 0.3:
        return True  # Threshold: 30% non-text => check with chardet

    # Use chardet to guess encoding
    detected = chardet.detect(data)
    if detected["confidence"] > 0.7:  # Chardet is confident => text
        return False
    else:
        return True  # Otherwise binary
