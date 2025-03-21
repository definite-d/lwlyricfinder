import regex as re

HOST: str = "loveworldlyrics.com"
URL_PATTERN = re.compile(rf"(?:https?://)?{re.escape(HOST)}/(?P<slug>[\w-]+)/?")
CLEAN_PATTERN = re.compile(
    r"(?:\s)?(?:[\{\}\<\>\[\]])|(?:♪…♪)|(?:\b(?:ad(?:-|\s)libs?|b(?:eat|r(?:eak|idge))|call|cho(?:ir|rus)|coda|drop|"
    r"echo|falsetto|growl|hook|in(?=strument(?:al|s)?|terludes?|tro(?:duction))|loop|middle\seight|outro|"
    r"post(?:-|\s)chorus|pre(?:-|\s)chorus|re(?:frain|peat(?:\s(?:verse|chorus))?|prise|sponse)|riff|scat|solo|"
    r"spo(?:(?:ken(?:\sword))|ntaneous)?|vamp|verse(?:\s\d+)?|whisper|(?:x\d+))(:\s*)?\b)",
    re.IGNORECASE | re.MULTILINE,
)
