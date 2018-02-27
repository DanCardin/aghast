import logging
from typing import Callable, Iterable

from dataclasses import dataclass

log = logging.getLogger('errors')


@dataclass
class Context:
    line: int = 0
    pos: int = 0


class TokenStream:
    """The stream of tokens!

    Provide transparent interation over the input stream of tokens.

    But ALSO inject each token into all series of patterns which are registered to
    facilitate the pattern-matching matching.

    TODO:
    * transparently ignore useless garbage like whitespace, and such.
    * transparently ignore line continuations by silently eating the line continuation
      AS WELL AS the following indent token.
    * add something like `self.open()` which should (transparently) open a new context
      so we can just "get_tokens()" (for all tokens nexted in that context) for
      that context for each ast node.
    """
    def __init__(self, stream):
        self.stream = iter(stream)
        self.iterator = iter(self)

        self.matched_patterns = []
        self.pending_patterns = []

        self.next_token = None
        self.done = False

    def __bool__(self):
        return not self.done

    def __iter__(self):
        for item in self.stream:
            for pattern in self.matched_patterns:
                gen = iter(pattern)
                next(gen)
                self.pending_patterns.append(gen)

            pending_patterns = []
            for pending_pattern in self.pending_patterns:
                try:
                    pending_pattern.send(item)
                    pending_patterns.append(pending_pattern)
                except NoMatch:
                    pass
                except StopIteration as e:
                    callback = e.value
                    context = Context()
                    callback(context, item)

            self.pending_patterns = pending_patterns

            yield item

    def one_of(self, token, *one_of):
        if not one_of:
            return token
        for one_of_token in one_of:
            if token == one_of_token:
                return token
        raise ValueError(f'token {token} must be one of {one_of}')

    def next(self, *one_of):
        if self.next_token:
            next_token = self.next_token
            self.next_token = None
            return self.one_of(next_token, *one_of)

        try:
            return self.one_of(next(self.iterator), *one_of)
        except StopIteration:
            self.done = True
            return None

    def peek(self, *one_of):
        self.next_token = self.next(*one_of)
        return self.next_token

    def match_error_pattern(self, *sequence):
        def _match_pattern(callback):
            def error_handler(*args, **kwargs):
                log.error(callback(*args, **kwargs))
            self.matched_patterns.append(Pattern(error_handler, sequence))
        return _match_pattern

    def match_pattern(self, *sequence):
        def _match_pattern(callback):
            self.matched_patterns.append(Pattern(callback, sequence))
        return _match_pattern


class NoMatch(Exception):
    pass


@dataclass
class Pattern:
    callback: Callable
    sequence: Iterable

    def __iter__(self):
        for item in self.sequence:
            input_token = yield
            if item != input_token:
                raise NoMatch()
        return self.callback
