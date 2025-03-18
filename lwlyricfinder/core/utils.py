from lwlyricfinder.core.patterns import URL_HYPHENATE_PATTERN


def format_song_query(query: str):
    return URL_HYPHENATE_PATTERN.sub(
        "-",
        "".join(
            filter(
                lambda char: char
                if (char.isalnum() or char in (" ", "-", "–"))
                else "",
                query,
            )
        ),
    )


def divide_text(text: str, interval: int = 2) -> str:
    """
    Insert blank lines into the text at every 'interval' lines.
    """
    lines = text.split("\n")
    interleaved_lines = (
        line + ("\n" if (i % interval == 0) else "")
        for i, line in enumerate(filter(lambda s: s.strip(), lines), 1)
    )
    return "\n".join(interleaved_lines)
