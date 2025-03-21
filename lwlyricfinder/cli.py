from typing import Annotated

from pyperclip import copy
from rich import print
from typer import Argument, Exit, Option, Typer, prompt

from .core.exceptions import LyricError
from .core.find import find
from .core.song import Song

app = Typer(rich_markup_mode="rich")


def finalize(song: Song, show: bool = False):
    print(song)
    if show:
        print(">\n", song.content)
    print("Copied song contents to clipboard.")
    copy(song.content)


@app.command()
def find_lyrics(
    query: Annotated[
        str,
        Argument(
            help="Search query for the song. Can be a link, full or partial title, or lyrics snippet."
        ),
    ],
    matches: Annotated[
        int,
        Option(
            "--matches",
            "-m",
            min=1,
            max=30,
            help="The maximum number of matching songs to retrieve, defaults to 5.",
        ),
    ] = 5,
    division_interval: Annotated[
        int | None,
        Option(
            "--division-interval",
            "-d",
            help="If specified, blank lines are inserted in the lyrics by the interval.",
        ),
    ] = None,
    clean: Annotated[
        bool,
        Option(
            "--clean",
            "-c",
            help="Whether to remove instructional text from the lyrics (e.g., [Repeat], {x2}, etc.), defaults to False.",
        ),
    ] = False,
    show: Annotated[
        bool,
        Option(
            "--show",
            "-s",
            help="Whether to print the final result to stdout. Defaults to False.",
        ),
    ] = False,
    use_first_result: Annotated[
        bool,
        Option(
            "--use-first-result",
            "-f",
            help="Whether to return the lyrics of the first result automatically, even if multiple results exist.",
        ),
    ] = False,
):
    try:
        songs: tuple[Song, ...] = find(query, matches, division_interval, clean)
    except LyricError as e:
        print(f"[red]{e}[/]")
        raise Exit(code=1)

    total: int = len(songs)

    if use_first_result or (total == 1):
        query = songs[0]
        print(f"Using first {'(and only) ' if total == 1 else ''}result.")
        finalize(query, show)
        raise Exit(code=0)

    print(f"Showing {total} results.")
    for index, query in enumerate(songs, 1):
        print(f"→ [blue]{index}[/]. [green]{query.title}[/]")

    answer: int = prompt(f"==> Choose from 1 to {total}", type=int)

    if 0 < int(answer) < total + 1:
        finalize(songs[answer - 1], show)
        raise Exit(code=0)
    else:
        print("[red]Invalid number chosen.[/]")
        raise Exit(code=1)
