from urllib.parse import quote

from httpx import HTTPError, HTTPStatusError, get
from rich.progress import Progress, SpinnerColumn, TextColumn

from .exceptions import LyricError
from .patterns import HOST, URL_PATTERN
from .song import Song

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


def find(
    query: str,
    matches: int = 5,
    division_interval: int = 0,
    clean: bool = False,
) -> tuple[Song, ...]:
    """
    Searches for songs matching the given query and returns them as Song objects.

    :param query: The search term or a direct song URL.
    :type query: str
    :param matches: The maximum number of matching songs to retrieve, defaults to 5.
    :type matches: int, optional
    :param division_interval: The interval at which blank lines are inserted in the lyrics, defaults to 0.
    :type division_interval: int, optional
    :param clean: Whether to remove instructional text from the lyrics, defaults to False.
    :type clean: bool, optional
    :return: A tuple containing the found Song objects.
    :rtype: tuple[Song, ...]
    :raises LyricError: If an HTTP error occurs or no songs are found.
    """
    with Progress(
        SpinnerColumn(spinner_name="line"),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task_id = progress.add_task("Forming URL.", total=None)
        if m := URL_PATTERN.match(query):
            progress.update(
                task_id,
                description="Whole song URL detected. Navigating.",
                total=None,
            )
            slug = m["slug"]
            url = f"https://{HOST}/wp-json/wp/v2/posts?slug={slug}"
        else:
            url = (
                f"https://{HOST}/wp-json/wp/v2/posts"
                f"?per_page={matches}"
                f"&orderby=relevance"
                f"&search={quote(query)}"
            )
        try:
            progress.update(task_id, description="Finding.", total=None)
            response = get(url, headers=HEADERS)
            response.raise_for_status()
        except HTTPStatusError:
            raise LyricError(
                f"[ERROR] HTTP {response.status_code} error.\n"
                f"Visit https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/{response.status_code} "
                f"for more information."
            )
        except HTTPError as e:
            raise LyricError(f"[ERROR] {e}")

        progress.update(
            task_id,
            description="Receiving songs.",
            total=None,
        )
        songs: tuple[Song, ...] = tuple(
            Song(song, division_interval, clean) for song in response.json()
        )
        if not songs:
            raise LyricError("[ERROR] No songs found.")
        return songs
