from typing import Generator

from selectolax.parser import HTMLParser
from regex import sub

from .patterns import CLEAN_PATTERN


def parse_html_content(content: str) -> str:
    """
    Extracts and returns the text content (lyrics) from an HTML string.

    :param content: The HTML string containing the song lyrics.
    :type content: str
    :return: The extracted lyrics as plain text.
    :rtype: str
    """
    parser: HTMLParser = HTMLParser(content)
    result: str = "\n".join(map(lambda p: p.text(separator="\n"), parser.css("p")))
    if not result:
        result: str = parser.text(deep=False, separator="\n", strip=False).strip()
    return result


def format_text_spacing(text: str):
    """
    Reduces excessive empty lines in the given text,
    ensuring no more than two consecutive newlines,
    and trims leading and trailing whitespace.

    :param text: The input text to format.
    :type text: str
    :return: The formatted text with adjusted spacing.
    :rtype: str
    """
    return sub(r"\n{3,}", "\n\n", text).strip()


def clean_lyrics(lyrics: str):
    """
    Removes instructional text (e.g., [Repeat], <x2>) from song lyrics using a predefined pattern.

    :param lyrics: The lyrics to be cleaned.
    :type lyrics: str
    :return: The cleaned lyrics without additional instructions.
    :rtype: str
    """
    return CLEAN_PATTERN.sub("", lyrics, concurrent=True)


def divide_text(text: str, interval: int = 2) -> str:
    """
    Inserts a blank line into the text at every specified interval of non-empty lines.

    :param text: The input text to modify.
    :type text: str
    :param interval: The number of lines between each inserted blank line, defaults to 2.
    :type interval: int, optional
    :return: The formatted text with inserted blank lines.
    :rtype: str
    """
    lines: tuple[str, ...] = tuple(filter(lambda s: s.strip(), text.split("\n")))
    interleaved_lines: Generator[str, str, None] = (
        line + ("\n" if ((i % interval == 0) and (i != len(lines))) else "")
        for i, line in enumerate(lines, 1)
    )
    return "\n".join(interleaved_lines)
