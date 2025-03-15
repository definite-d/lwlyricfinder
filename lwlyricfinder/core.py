from httpx import get, HTTPError
from selectolax.parser import HTMLParser
from urllib.parse import quote


class LyricError(Exception):
    pass


def format_song_query(query: str):
    return quote(query.replace(" ", "-"))


def divide_text(text: str, interval: int = 2) -> str:
    """
    Insert blank lines into the text at every 'interval' lines.
    """
    lines = text.split("\n")
    interleaved_lines = (
        line + ("\n" if (i + 1) % interval == 0 else "") for i, line in enumerate(lines)
    )
    return "\n".join(interleaved_lines)


def search_lyrics(query: str, matches: int = 5):
    """
    Searches for a song which contains a given query.
    """
    url = f"https://loveworldlyrics.com/{format_song_query(query)}/"


def fetch_lyrics(query: str, divide_interval: int = 0) -> str:
    """
    Fetches lyrics from LoveWorld Lyrics for a given song.
    """

    url = f"https://loveworldlyrics.com/{format_song_query(query)}/"

    try:
        response = get(url, follow_redirects=True)
        response.raise_for_status()
    except HTTPError as e:
        raise LyricError(f"Error fetching lyrics: {e}")

    text = response.text
    parser = HTMLParser(text)
    nodes = parser.css("div.post-inner div.entry p")

    lyrics = ("\n" if divide_interval else "\n\n").join(
        map(lambda node: node.text(separator="\n", strip=True), nodes)
    )

    if divide_interval:
        return divide_text(lyrics, divide_interval)
    return lyrics
