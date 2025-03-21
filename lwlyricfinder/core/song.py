from html import unescape

from .exceptions import LyricError
from .utils import parse_html_content, clean_lyrics, divide_text, format_text_spacing


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
