from enum import Enum

class ContentType(Enum):
    TEXT = "text"
    QUESTION = "question"
    CODE = "code"
    COMMAND = "command"
    UNKNOWN = "unknown"