## Nuitka Options:
# nuitka-project-if: {OS} in ("Windows", "Linux", "Darwin", "FreeBSD"):
#    nuitka-project: --onefile
# nuitka-project-else:
#    nuitka-project: --mode=standalone
# nuitka-project: --company-name="Afam-Ifediogor, U. Divine"
# nuitka-project: --enable-plugin=pylint-warnings
# nuitka-project: --follow-import-to=httpx
# nuitka-project: --follow-import-to=pyperclip
# nuitka-project: --follow-import-to=regex
# nuitka-project: --follow-import-to=selectolax
# nuitka-project: --follow-import-to=typer
# nuitka-project: --lto=yes
# nuitka-project: --no-deployment-flag=self-execution
# nuitka-project: --nofollow-import-to=PIL
# nuitka-project: --nofollow-import-to=matplotlib
# nuitka-project: --nofollow-import-to=tests
# nuitka-project: --nofollow-import-to=tkinter
# nuitka-project: --noinclude-pytest-mode=nofollow
# nuitka-project: --output-dir=dist
# nuitka-project: --product-name="LW Lyric Finder"
# nuitka-project: --python-flag=-m
# nuitka-project: --remove-output
# nuitka-project: --trademarks="Copyright 2025, Afam-Ifediogor, U. Divine."


from .cli import app

if __name__ == "__main__":
    app()
