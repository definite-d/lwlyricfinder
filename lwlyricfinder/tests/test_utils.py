from ..core.utils import (
    parse_html_content,
    clean_lyrics,
    format_text_spacing,
    divide_text,
    Song,
)
from pytest import fixture, mark
from json import load
from pathlib import Path


@fixture
def response():
    with open(Path(__file__).parent / "response.json", "rb") as file:
        return load(file)


@fixture
def song(response):
    return response[0]


@mark.dependency()
def test_format_text_spacing():
    assert (
        format_text_spacing("\nLine 1\n\n\n\nLine 2\nLine 3\n\nLine 4\n")
        == "Line 1\n\nLine 2\nLine 3\n\nLine 4"
    )


@mark.dependency()
def test_parse_html_content(song):
    assert parse_html_content(song.get("content").get("rendered")) == (
        "[Verse]\nFor all that You have done\nJesus, I magnify Your Name\nFor all that You have done\nJesus, I Magnify "
        "Your Name\n\n\n\n\n[Chorus]\nEndless Praise\nEndless thanks\nBelongs to You, My God\nEndless Praise\nEndless "
        "thanks\nBelongs to You, My God\n\n\n\n\n[Repeat Verse]\nFor all that You have done\nJesus, I magnify Your Name"
        "\nFor all that You have done\nJesus, I magnify Your Name\nFor all that You have done\nJesus, I magnify Your "
        "Name\n\n\n\n\n[Repeat Chorus]\n{Endless Praise\nEndless thanks\nBelongs to You, My God\nEndless Praise\n"
        "Endless thanks\nBelongs to You, My God} [Loop]\n\n\n\n[Repeat Verse]\n{For all that You have done\nJesus, I "
        "magnify Your Name\nFor all that You have done\nJesus, I magnify Your Name} [x2]\n\n\n\n[ ♪…♪ Spontaneous ♪…♪]"
        "\n\n\n\n[Outro]\nEndless praise\nEndless thanks\nBelongs to You My God\nEndless praise\nEndless thanks\n"
        "Belongs to You My God"
    )


@mark.dependency()
def test_clean_lyrics(song):
    assert (
        clean_lyrics("[Verse 2]\n[Refrain]\n{Chorus}\nGlory in the Highest [x482]\n")
        == "\nGlory in the Highest\n"
    )


@mark.dependency()
def test_divide_text():
    assert divide_text(
        "\nLine 1\nLine 2\n\n\n\n\nLine 3\n\nLine 4\nLine 5\nLine 6\nLine 7\n    \n\n",
        2,
    ) == ("Line 1\nLine 2\n\nLine 3\nLine 4\n\nLine 5\nLine 6\n\nLine 7")


@mark.dependency(
    depends=[
        "test_format_text_spacing",
        "test_parse_html_content",
        "test_clean_lyrics",
        "test_divide_text",
    ]
)
def test_song_object(song):
    song_1 = Song(song, 2, True)
    assert song_1.content == (
        "For all that You have done\nJesus, I magnify Your Name\n\nFor all that You have done\nJesus, I Magnify Your "
        "Name\n\nEndless Praise\nEndless thanks\n\nBelongs to You, My God\nEndless Praise\n\nEndless thanks\nBelongs "
        "to You, My God\n\nFor all that You have done\nJesus, I magnify Your Name\n\nFor all that You have done\nJesus,"
        " I magnify Your Name\n\nFor all that You have done\nJesus, I magnify Your Name\n\nEndless Praise\nEndless "
        "thanks\n\nBelongs to You, My God\nEndless Praise\n\nEndless thanks\nBelongs to You, My God\n\nFor all that "
        "You have done\nJesus, I magnify Your Name\n\nFor all that You have done\nJesus, I magnify Your Name\n\n"
        "Endless praise\nEndless thanks\n\nBelongs to You My God\nEndless praise\n\nEndless thanks\nBelongs to You "
        "My God"
    )
