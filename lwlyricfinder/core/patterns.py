import regex as re

URL_PATTERN = re.compile(r"(https?://)?loveworldlyrics\.com/")
URL_HYPHENATE_PATTERN = re.compile(r"[–\s]+")
CLEAN_PATTERN = re.compile(
    r"\b(?:ad(?:-|\s)libs?|b(?:eat|r(?:eak|idge))|call|cho(?:ir|rus)|coda|drop|echo|falsetto|growl|hook|"
    r"in(?=strument(?:al|s)?|terludes?|tro(?:duction))|loop|middle\seight|outro|post(?:-|\s)chorus|"
    r"pre(?:-|\s)chorus|re(?:frain|prise|sponse)|riff|scat|solo|spoken(?:\sword)?|vamp|verse(?:\s\d+)?|"
    r"whisper)(:\s*)?\b",
    re.IGNORECASE | re.MULTILINE,
)
