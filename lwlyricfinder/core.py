from urllib.parse import quote

import regex as re
from httpx import HTTPError, get
from rich.progress import Progress, SpinnerColumn, TextColumn
from selectolax.parser import HTMLParser

URL_PATTERN = re.compile(r"(https?://)?loveworldlyrics\.com/")
CLEAN_PATTERN = re.compile(
    r"^(?:ad(?:-|\s)libs?|b(?:eat|r(?:eak|idge))|call|chorus|coda|drop|echo|falsetto|growl|hook|"
    r"in(?=strument(?:al|s)?|terludes?|tro(?:duction))|loop|middle\seight|outro|post(?:-|\s)chorus|"
    r"pre(?:-|\s)chorus|refrain|reprise|response|riff|scat|solo|spoken(?:\sword)?|vamp|verse(?:\s\d+)?|"
    r"whisper)(?::?)$",
    re.IGNORECASE | re.MULTILINE,
)


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
        line + (f"\t(Line {i})\n" if (i % interval == 0) else f"\t(Line {i})")
        for i, line in enumerate(filter(lambda s: s.strip(), lines), 1)
    )
    return "\n".join(interleaved_lines)


def search_lyrics(query: str, matches: int = 5) -> dict[str, str | None]:
    """
    Searches for a song which contains a given query.
    """
    with Progress(
        SpinnerColumn(spinner_name="line"),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task_id = progress.add_task("Forming URL.", total=None)
        url = f"https://loveworldlyrics.com/?s={format_song_query(query)}"
        try:
            progress.update(task_id, description="Fetching page.", total=None)
            response = get(url)
            response.raise_for_status()
        except HTTPError as e:
            raise LyricError(f"Error searching for lyrics: {e}")

        progress.update(task_id, description="Receiving page contents.", total=None)
        text = response.text.encode("utf-8")

        progress.update(task_id, description="Parsing HTML.", total=None)
        parser = HTMLParser(text)
        nodes = parser.css(".post-box-title a")[:matches]
        return dict(map(lambda x: (x.text(), x.attributes.get("href", None)), nodes))


def fetch_lyrics(
    query_or_url: str,
    division_interval: int = 0,
    clean=False,
) -> tuple[str, str]:
    """
    Fetches title and lyrics from LoveWorld Lyrics for a given song.
    """
    with Progress(
        SpinnerColumn(spinner_name="line"),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task_id = progress.add_task("Forming URL.", total=None)
        if not URL_PATTERN.match(query_or_url):
            url = f"https://loveworldlyrics.com/{format_song_query(query_or_url)}/"
        else:
            url = query_or_url

        try:
            progress.update(task_id, description="Performing search.", total=None)
            response = get(url, follow_redirects=True)
            response.raise_for_status()
        except HTTPError as e:
            raise LyricError(f"Error fetching lyrics: {e}")

        progress.update(task_id, description="Receiving page contents.", total=None)
        text = response.text.encode("utf-8")
        progress.update(task_id, description="Parsing HTML.", total=None)
        parser = HTMLParser(text, use_meta_tags=False)
        progress.update(task_id, description="Locating relevant nodes.", total=None)
        nodes = parser.css("div.post-inner div.entry p")

        progress.update(task_id, description="Merging lyric blocks.", total=None)
        lyrics = ("\n" if division_interval else "\n\n").join(
            map(lambda node: node.text(separator="\n", strip=True), nodes)
        )

        progress.update(task_id, description="Extracting song title.", total=None)
        title = parser.css_first(".name").text().strip()

        if clean:
            lyrics = CLEAN_PATTERN.sub("", lyrics, concurrent=True)
        if division_interval:
            progress.update(task_id, description="Dividing text.", total=None)
            return title, divide_text(lyrics, division_interval)
        return title, lyrics
