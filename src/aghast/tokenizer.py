from aghast.tokens import Identifier, Indent, Keywords, Symbols, Whitespace

alphabetic = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_')
numeric = set('0123456789')
alphanumeric = alphabetic | numeric

equality_modifiers = set('<>!~=')
infix_operators = set('@|%*^/+-')
other_symbols = set('()[]{}:;,.\\')
symbol = equality_modifiers | infix_operators | other_symbols

equal = '='
whitespace = ' '
newline = '\n'


class Character(str):
    def __new__(cls, content):
        if content is None:
            content = ''
        else:
            assert len(content) == 1
        return str.__new__(cls, content)

    @property
    def is_newline(self):
        return self == '\n'

    @property
    def is_whitespace(self):
        return self == ' '

    @property
    def is_alphanumeric(self):
        return self in alphanumeric

    @property
    def is_alphabetic(self):
        return self in alphabetic

    @property
    def is_numeric(self):
        return self in numeric

    @property
    def is_symbol(self):
        return self in symbol


class CharStream:
    def __init__(self, source):
        self.source = iter(source)
        self.next_token = None
        self.done = False
        self.pos = 0

    def _next(self):
        if self.next_token:
            next_token = self.next_token
            self.next_token = None
            return next_token

        try:
            return next(self.source)
        except StopIteration:
            self.done = True
            return None

    def next(self):
        next = self._next()
        return Character(next)

    def peek(self):
        self.next_token = self.next()
        return self.next_token

    def __bool__(self):
        return not self.done


def consume_newline(char_stream):
    count = 0

    c = char_stream.next()
    assert c.is_newline

    while char_stream:
        c = char_stream.peek()
        if c.is_whitespace:
            count += 1
            char_stream.next()
        else:
            break
    return Indent(count)


def consume_whitespace(char_stream):
    count = 1

    c = char_stream.next()
    assert c.is_whitespace

    while char_stream:
        c = char_stream.peek()
        if c.is_whitespace:
            count += 1
            char_stream.next()
        else:
            break
    return Whitespace(count)


def consume_identifier(char_stream):
    ident_chars = []
    while char_stream:
        c = char_stream.peek()
        if c.is_alphanumeric:
            ident_chars.append(char_stream.next())
        else:
            break

    ident = ''.join(ident_chars)
    if ident in Keywords.keywords():
        return Keywords(ident)
    return Identifier(ident)


def consume_symbol(char_stream):
    c = char_stream.next()
    if c in other_symbols:
        return Symbols(c)
    raise NotImplementedError(c)


def tokenize(raw_input):
    char_stream = CharStream(raw_input)
    while char_stream:
        c = char_stream.peek()

        if not c:
            break
        elif c.is_newline:
            yield consume_newline(char_stream)
        elif c.is_whitespace:
            yield consume_whitespace(char_stream)
        elif c.is_alphabetic:
            yield consume_identifier(char_stream)
        elif c.is_symbol:
            yield consume_symbol(char_stream)
        else:
            raise NotImplementedError(c)
