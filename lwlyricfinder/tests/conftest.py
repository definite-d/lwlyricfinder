from json import load
from pathlib import Path

from pytest import fixture


@fixture()
def response():
    with open(Path(__file__).parent / "response.json", "rb") as file:
        return load(file)


@fixture
def song(response):
    return response[0]
