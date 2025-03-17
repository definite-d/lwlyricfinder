from typing import Annotated

from pyperclip import copy
from typer import Argument, Exit, Option, Typer, prompt
from rich import print

from lwlyricfinder.core import LyricError, fetch_lyrics, search_lyrics

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
        print(f"Copied the following song's lyrics to clipboard: [green]{title}[/].")


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
            help="Returns the lyrics of the first search result automatically, if any result exists.",
        ),
    ] = False,
    clean: Annotated[
        bool,
        Option(
            "--clean",
            "-c",
            help="Whether to clean the lyrics of instructional words, such as 'Chorus' or 'Solo'.",
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

    if use_first_result or ((total := len(songs)) == 1):
        name, link = next(iter(songs.items()))
        print(f"Using first {'(and only) ' if total == 1 else ''}result.")
        find(link, division_interval, clean)
        raise Exit(code=0)

    print(f"{total} songs found.")
    index_song_map = {}

    for index, title in enumerate(songs, 1):
        print(f"↪ {index}. {title}")
        index_song_map[str(index)] = title

    answer = prompt(f"=> Choose from 1 to {total}: ")
    print(answer + " chosen")
    link = songs.get(index_song_map.get(answer, None), None)

    try:
        if 0 < int(answer) < total + 1:
            find(link, division_interval, clean)
    except (TypeError, ValueError):
        print("Exiting.")
        raise Exit(code=0)
    else:
        print("Exiting.")
        raise Exit(code=0)
