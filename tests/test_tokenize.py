from aghast.param import Param
from aghast.parser import Parser
from aghast.pattern_match import TokenStream
from aghast.tokenizer import tokenize
from aghast.tokens import Identifier, Indent, Keywords, Symbols, Whitespace


def test_tokenize(caplog):
    result = tokenize('from  module  import (\n     meow,\n    hah\n)')
    expected_result = [
        Keywords('from'),
        Whitespace(2),
        Identifier('module'),
        Whitespace(2),
        Keywords('import'),
        Whitespace(1),
        Symbols('('),
        Indent(5),
        Identifier('meow'),
        Symbols(','),
        Indent(4),
        Identifier('hah'),
        Indent(0),
        Symbols(')'),
    ]
    result = list(result)
    assert result == expected_result

    ts = TokenStream(result)

    @ts.match_error_pattern(Keywords('from'), Whitespace(2))
    def nonsense_chorded_rule(context, symbol):
        return 'from followed by 2 spaces...'

    @ts.match_error_pattern(Symbols('\\'))
    @ts.match_error_pattern(Symbols(';'))
    def bad_tokens(context, symbol):
        return 'Dont ever use the {symbol.value} character!'

    x = Param()

    @ts.match_error_pattern(Whitespace(x > 1))
    def too_much_whitespace(context, x):
        return f'Too much ({x} chars of) whitespace at position ({context.line}, {context.pos})'

    @ts.match_error_pattern(Indent(x / 4 == 0))
    def all_indents_must_be_multiples_of_4(context, x):
        return f'All indentation must be multiples of 4 at position ({context.line}, {context.pos})'

    parser = Parser(ts)
    for node in parser:
        pass

    logs = [record.msg for record in caplog.records]
    assert logs == [
        'from followed by 2 spaces...',
        'Too much (Whitespace(size=2) chars of) whitespace at position (0, 0)',
        'Too much (Whitespace(size=2) chars of) whitespace at position (0, 0)',
        'Too much (Whitespace(size=1) chars of) whitespace at position (0, 0)',
        'All indentation must be multiples of 4 at position (0, 0)',
        'All indentation must be multiples of 4 at position (0, 0)',
        'All indentation must be multiples of 4 at position (0, 0)',
    ]
