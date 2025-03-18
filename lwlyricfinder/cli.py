from typing import Annotated

from pyperclip import copy
from typer import Argument, Exit, Option, Typer, prompt
from rich import print

from .core.lyrics import fetch_lyrics, search_lyrics
from .core.exceptions import LyricError

app = Typer(rich_markup_mode="rich")


@app.command()
def find(
    song: Annotated[str, Argument(help="The song to search for.")],
    division_interval: Annotated[
        int,
        Option(
            "--division-interval",
            "-d",
            help="The number of lines to space the lyrics by.\n"
            "Defaults to 0 to use the default spacing from the site.",
        ),
    ] = 0,
    clean: Annotated[
        bool,
        Option(
            "--clean",
            "-c",
            help="Whether to clean the lyrics of instructional words, such as 'Chorus' or 'Solo'.",
        ),
    ] = False,
    show: Annotated[
        bool,
        Option(
            "--show",
            "-s",
            help="Print the final result to stdout.",
        ),
    ] = False,
):
    """
    Fetch song lyrics and copy them to the clipboard.
    """
    try:
        title, lyrics = fetch_lyrics(song, division_interval, clean)
    except LyricError as e:
        print(f"{e}")
        raise Exit(code=1)
    else:
        copy(lyrics)
        if show:
            print("Copied the following song's lyrics to clipboard.")
            print(f"Title: {title}\n")
            print(lyrics)
        else:
            print(
                f"Copied the following song's lyrics to clipboard: [green]{title}[/]."
            )


@app.command("search")
def search(
    query: Annotated[
        str,
        Argument(
            help="The search query. Could be a phrase from the song, or its title."
        ),
    ],
    matches: Annotated[
        int,
        Option(
            "--matches",
            "-m",
            min=1,
            max=10,
            help="The number of search results to show. Min 1. Max 10.",
        ),
    ] = 5,
    division_interval: Annotated[
        int,
        Option(
            "--division-interval",
            "-d",
            help="The number of lines to space the lyrics by.\n"
            "Defaults to 0 to use the default spacing from the site.",
        ),
    ] = 0,
    use_first_result: Annotated[
        bool,
        Option(
            "--use-first-result",
            "-f",
            help="Return the lyrics of the first search result automatically, if any result exists.",
        ),
    ] = False,
    clean: Annotated[
        bool,
        Option(
            "--clean",
            "-c",
            help="Clean the lyrics of instructional words, such as 'Chorus' or 'Solo'.",
        ),
    ] = False,
    show: Annotated[
        bool,
        Option(
            "--show",
            "-s",
            help="Print the final result to stdout.",
        ),
    ] = False,
):
    """Search for a specific song query."""
    try:
        songs = search_lyrics(query, use_first_result or matches)
    except LyricError as e:
        print(f"{e}")
        raise Exit(code=1)

    if not songs:
        print("No songs found.")
        raise Exit(code=1)

    total: int = len(songs)
    if use_first_result or (total == 1):
        name, link = next(iter(songs.items()))
        print(f"Using first {'(and only) ' if total == 1 else ''}result.")
        find(link, division_interval, clean, show)
        raise Exit(code=0)

    print(f"Showing {total} results.")
    index_song_map: dict[int, str] = dict()

    for index, title in enumerate(songs, 1):
        print(f"→ [blue]{index}[/]. [green]{title}[/]")
        index_song_map[index] = title

    answer: int = prompt(f"==> Choose from 1 to {total}", type=int)
    link = songs.get(index_song_map.get(answer, None), None)

    if 0 < int(answer) < total + 1:
        find(link, division_interval, clean, show)
    else:
        print("Invalid number chosen. Exiting.")
        raise Exit(code=0)
