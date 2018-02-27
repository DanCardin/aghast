from aghast.ast import ImportModuleSection, ImportStatement, SingleImport
from aghast.param import x
from aghast.parser import AbstractParser
from aghast.tokens import Identifier, Indent, Keywords, Symbols, Whitespace


class ImportParser(AbstractParser):
    def __iter__(self):
        token = self.token_stream.peek(Keywords('import'), Keywords('from'))
        self.tokens.append(self.token_stream.next())

        needs_module_section = False
        if token == Keywords('from'):
            needs_module_section = True

        self.token_stream.peek(Whitespace(x))
        self.tokens.append(self.token_stream.next())

        if needs_module_section:
            module_section = yield from ModuleSection(self.token_stream)

        token = self.token_stream.peek(Keywords('import'))
        self.tokens.append(self.token_stream.next())

        imports = yield from ImportSection(self.token_stream)

        return ImportStatement(
            tokens=self.tokens,
            module_section=module_section,
            imports=imports,
        )


class ModuleSection(AbstractParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.local = False
        self.local_path_index = 0

        self.seen_first_module = False
        self.last_token = None
        self.modules = []

    def __iter__(self):
        token = self.token_stream.peek()

        if token == Symbols.PERIOD:
            self.local = True
            token = self.token_stream.next()

        while self.token_stream:
            token = self.token_stream.peek(Whitespace(x), Identifier(x), Symbols.PERIOD)

            if token == Whitespace(x):
                # So the module section is done now!
                self.token_stream.next()
                yield ImportModuleSection(
                    self.tokens,
                    self.local,
                    self.local_path_index,
                    self.modules,
                )
                break

            if token == Symbols.PERIOD:
                if self.seen_first_module and self.last_token == Symbols.PERIOD:
                    raise ValueError('period invalid here')

                if not self.seen_first_module:
                    self.local = True
                    self.local_path_index -= 1

            elif token == Identifier(x):
                self.seen_first_module = True
                self.modules.append(token)

            self.tokens.append(self.token_stream.next())


class ImportSection(AbstractParser):
    """Parse the import section of an import statement.

    e.g. from a import <this section>

    TODO:
    * as
    * like all the edge cases, currently only handles the one happy path.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.require_close_parens = False
        self.need_comma = False
        self.imports = []

    def __iter__(self):
        token = self.token_stream.peek()
        if token == Whitespace(x):
            self.token_stream.next()

        token = self.token_stream.peek()
        if token == Symbols.PAREN_OPEN:
            self.require_close_parens = True
            self.token_stream.next()

        while self.token_stream:
            token = self.token_stream.peek(
                Identifier(x), Symbols.COMMA, Whitespace(x), Indent(x), Symbols.PAREN_CLOSE,
            )
            if token == Whitespace(x):
                self.tokens.append(self.token_stream.next())
                continue

            if token == Indent(x):
                if not self.require_close_parens:
                    break

                self.tokens.append(self.token_stream.next())
                continue

            if token == Identifier(x):
                self.imports.append(token)
                self.tokens.append(self.token_stream.next())
                self.need_comma = True
                continue

            if token == Symbols.COMMA:
                self.tokens.append(self.token_stream.next())
                self.need_comma = False
                continue

            if token == Symbols.PAREN_CLOSE:
                self.tokens.append(self.token_stream.next())
                if self.require_close_parens:
                    break
                raise ValueError('wat')

        yield [
            SingleImport(self.tokens, import_name, alias=None)
            for import_name in self.imports
        ]
