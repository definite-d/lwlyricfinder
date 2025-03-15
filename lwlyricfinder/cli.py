from .core import fetch_lyrics, LyricError
from typer import Typer, echo, Exit
from pyperclip import copy


app = Typer(rich_markup_mode="rich")


@app.command()
def main(song: str):
    """
    Fetch song lyrics and copy them to the clipboard.
    """
    try:
        lyrics = fetch_lyrics(song)
    except LyricError as e:
        echo(f"{e}")
        raise Exit(code=1)
    copy(lyrics)
    echo("[yellow]Lyrics copied to clipboard![/]")
