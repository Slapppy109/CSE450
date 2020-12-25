if __name__ == "__main__":
    from rply import LexerGenerator
    from rply import Token
else:
    from . rply import LexerGenerator
    from . rply import Token
import re


def build_lexer():
    lg = LexerGenerator()
    
    # Ignore whitespaces, tabs, single comments, and multi comments
    lg.ignore(r"\t| ")
    lg.ignore(r"BTW.*")
    lg.ignore(r"OBTW(.|\n)*?TLDR")
    
    # Added before keywords to account for rule order
    lg.add('LOGICAL_VARIABLE_OPERATOR', r"ALL|ANY")    
    
    # Adding keywords
    lg.add("HAI", r"HAI")
    lg.add("KTHXBYE", r"KTHXBYE")
    lg.add("VISIBLE", r"VISIBLE")
    lg.add("GIMMEH", r"GIMMEH")
    lg.add("WHATEVR", r"WHATEVR")
    lg.add("ITZ", r"ITZ")
    lg.add("I", r"I")
    lg.add("HAS", r"HAS")
    lg.add("AN", r"AN")
    lg.add("A", r"A")
    lg.add("R", r"R")
    lg.add("OF", r"OF")
    lg.add("MKAY", r"MKAY")
    lg.add("BY", r"BY")
    
    # Adding rules for tokens
    lg.add('PRIMITIVE_TYPE', r"NUMBR|NUMBAR|LETTR|TROOF")
    lg.add('BANG', r'!')
    lg.add('NUMBAR_LITERAL', r"-?[0-9]*(\.[0-9]+)")
    lg.add('NUMBR_LITERAL', r"-?[0-9]+")
    lg.add('LETTR_LITERAL', r"(\'.\')")
    lg.add('TROOF_LITERAL', r"WIN|FAIL")
    lg.add('YARN_LITERAL', r"(\".*?\")")
    lg.add('COMPARISON_BINARY_OPERATOR', r"SAEM|DIFFRINT|FURSTSMALLR|FURSTBIGGR")
    lg.add('MATH_BINARY_OPERATOR', r"SUM|DIFF|PRODUKT|QUOSHUNT|BIGGR|SMALLR")
    lg.add('MATH_UNARY_OPERATOR', r"FLIP|SQUAR")
    lg.add('LOGICAL_BINARY_OPERATOR', r"BOTH|EITHER|WON")
    lg.add('LOGICAL_UNARY_OPERATOR', r"NOT")
    lg.add('ASSIGNMENT_OPERATOR', r"UPPIN|NERFIN")
    lg.add('NEWLINE', r"\n")
    lg.add('IDENTIFIER', r"[a-zA-Z][a-zA-Z0-9_]*")
    lg.add('ERROR',r'.')
    
    lexer = lg.build()
    return lexer


def tokenize_LOLcode(lolcode_str):
    lexer = build_lexer()
    tokens = list(lexer.lex(lolcode_str))
    return tokens

def test():
    tokens = tokenize_LOLcode("""HAI 1.450
    I HAS A result ITZ A NUMBR BTW I like apples
    result R 14

    VISIBLE result
    OBTW This is a 
    multiline comment
    TLDR
    KTHXBYE""")

    print(tokens)
    example_token = tokens[1]
    print(example_token.gettokentype())
    print(example_token.getstr())

    expected = [Token('HAI', 'HAI'), Token('NUMBAR_LITERAL', '1.450'), Token('NEWLINE', '\n'), Token('I', 'I'), Token('HAS', 'HAS'), Token('A', 'A'), Token('IDENTIFIER', 'result'), Token('ITZ', 'ITZ'), Token('A', 'A'), Token('PRIMITIVE_TYPE', 'NUMBR'), Token('NEWLINE', '\n'), Token('IDENTIFIER', 'result'), Token('R', 'R'), Token('NUMBR_LITERAL', '14'), Token('NEWLINE', '\n'), Token('NEWLINE', '\n'), Token('VISIBLE', 'VISIBLE'), Token('IDENTIFIER', 'result'), Token('NEWLINE', '\n'), Token('NEWLINE', '\n'), Token('KTHXBYE', 'KTHXBYE')]
    assert expected == tokens

    import pprint
    pprint.pprint(expected)


if __name__ == "__main__":
    test()