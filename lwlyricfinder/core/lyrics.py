from httpx import HTTPError, get
from rich.progress import Progress, SpinnerColumn, TextColumn
from selectolax.parser import HTMLParser, Node

from .exceptions import LyricError
from .patterns import URL_PATTERN, CLEAN_PATTERN
from .utils import format_song_query, divide_text

HOST: str = "loveworldlyrics.com"
HEADERS: dict[str, str] = {
    "Host": HOST,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Sec-GPC": "1",
    "Alt-Used": HOST,
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "DNT": "1",
    "Priority": "u=0, i",
    "TE": "trailers",
}


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
        # The query isn't formatted because it appears to alter the results.
        # Searching with the raw query seems to work better, and is definitely faster.
        url = f"https://{HOST}/?s={query}"
        try:
            progress.update(task_id, description="Performing search.", total=None)
            response = get(url, headers=HEADERS)
            response.raise_for_status()
        except HTTPError as e:
            raise LyricError(f"Error searching for lyrics: {e}")

        progress.update(
            task_id,
            description="Receiving search page contents.",
            total=None,
        )
        text = response.text.encode("utf-8")

        progress.update(task_id, description="Parsing HTML.", total=None)
        parser = HTMLParser(text)
        all_nodes: list[Node] = parser.css(".post-box-title a")
        if not all_nodes:
            raise LyricError("Error searching for lyrics: No songs found.")
        nodes = all_nodes[: min(len(all_nodes), matches)]
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
            url = f"https://{HOST}/{format_song_query(query_or_url)}/"
        else:
            url = query_or_url

        try:
            progress.update(task_id, description="Fetching page.", total=None)
            response = get(url, follow_redirects=True, headers=HEADERS)
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
