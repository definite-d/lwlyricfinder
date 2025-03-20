from html import unescape
from typing import Generator

from selectolax.parser import HTMLParser
from regex import sub

from .exceptions import LyricError
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
    return parser.text(deep=False, separator="\n", strip=False).strip()


def format_text_spacing(text: str):
    """
    Formats given text to avoid multiple empty lines and trailing ones.
    """
    return sub(r"\n{3,}", "\n\n", text).strip()


def clean_lyrics(lyrics: str):
    """
    Cleans given lyrics of all additional "instructions", e.g. [Repeat] or <x2>.
    """
    return CLEAN_PATTERN.sub("", lyrics, concurrent=True)


def divide_text(text: str, interval: int = 2) -> str:
    """
    Insert blank lines into the text at every 'interval' lines.
    """
    lines: tuple[str, ...] = tuple(filter(lambda s: s.strip(), text.split("\n")))
    interleaved_lines: Generator[str, str, None] = (
        line + ("\n" if ((i % interval == 0) and (i != len(lines))) else "")
        for i, line in enumerate(lines, 1)
    )
    return "\n".join(interleaved_lines)


class Song:
    def __init__(self, response: dict, division_interval: int = 0, clean: bool = False):
        try:
            self.title: str = unescape(response.get("title").get("rendered"))
            self._raw_content: str = response.get("content").get("rendered")
        except (KeyError, AttributeError):
            raise LyricError("Invalid content.")
        self._content: str | None = None
        self.division_interval: int = division_interval
        self.clean: bool = clean

    @property
    def content(self):
        if not self._content:
            self._content = parse_html_content(self._raw_content)
            if self.clean:
                self._content = clean_lyrics(self._content)
            if self.division_interval:
                self._content = divide_text(self._content, self.division_interval)
            else:
                self._content = format_text_spacing(self._content)
        return self._content

    def __str__(self):
        return f"Title: {self.title}"
