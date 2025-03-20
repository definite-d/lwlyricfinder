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


class Song:
    """
    Represents a song with its title and lyrics, supporting optional formatting and cleaning.

    :param response: A dictionary containing song metadata, including the title and content.
    :type response: dict
    :param division_interval: The interval at which blank lines are inserted in the lyrics, defaults to 0.
    :type division_interval: int, optional
    :param clean: Whether to remove instructional text from the lyrics, defaults to False.
    :type clean: bool, optional
    :raises LyricError: If the response does not contain valid song content.
    """

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
    def content(self) -> str:
        """
        Processes and returns the song lyrics, applying optional cleaning and formatting.

        :return: The formatted lyrics as a string.
        :rtype: str
        """
        if not self._content:
            self._content = parse_html_content(self._raw_content)
            if self.clean:
                self._content = clean_lyrics(self._content)
            if self.division_interval:
                self._content = divide_text(self._content, self.division_interval)
            else:
                self._content = format_text_spacing(self._content)
        return self._content

    def __str__(self) -> str:
        """
        Returns a string representation of the song, displaying its title.

        :return: The song's title.
        :rtype: str
        """
        return f"Title: {self.title}"
