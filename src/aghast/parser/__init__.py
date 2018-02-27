from aghast.tokens import Keywords


class AbstractParser:
    def __init__(self, token_stream):
        self.token_stream = token_stream
        self.tokens = []


class Parser(AbstractParser):
    def __iter__(self):
        while self.token_stream:
            token = self.token_stream.peek()
            if token is None:
                break

            if token == Keywords('import') or token == Keywords('from'):
                yield from ImportParser(self.token_stream)
            else:
                raise ValueError(f'unhandled {token}')


from aghast.parser.parse_import import ImportParser  # noqa, isort:skip
