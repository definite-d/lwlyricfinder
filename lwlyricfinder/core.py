from selectolax.parser import HTMLParser
from httpx import get, HTTPError


class LyricError(Exception):
    pass


def divide_text(text: str, interval: int = 2) -> str:
    """
    Insert blank lines into the text at every 'interval' lines.
    """
    lines = text.split("\n")
    interleaved_lines = (
        line + ("\n" if (i + 1) % interval == 0 else "") for i, line in enumerate(lines)
    )
    return "\n".join(interleaved_lines)


def fetch_lyrics(song_name: str, divide_interval: int = 0) -> str:
    """
    Fetches lyrics from LoveWorld Lyrics for a given song.
    """
    formatted_song_name = song_name.replace(" ", "-").lower()
    url = f"https://loveworldlyrics.com/{formatted_song_name}/"

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
