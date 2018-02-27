import enum

from dataclasses import dataclass


class Keywords(enum.Enum):
    AS = 'as'
    FROM = 'from'
    IMPORT = 'import'
    IN = 'in'

    @classmethod
    def keywords(cls):
        return set([key.value for key in cls])


class Symbols(enum.Enum):
    PAREN_OPEN = '('
    PAREN_CLOSE = ')'
    BACKSLASH = '\\'
    SEMICOLON = ';'
    PERIOD = '.'
    COMMA = ','

    @classmethod
    def symbols(cls):
        return set([key.value for key in cls])


@dataclass
class Identifier:
    value: str


@dataclass
class Indent:
    size: int


@dataclass
class Whitespace:
    size: int
