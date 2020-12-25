from . rply import LexerGenerator
from . rply import ParserGenerator
from . rply import Token
import pprint
import re

#Was at help room with Josh 9/25/18

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

def build_parser(possible_tokens):
    pg = ParserGenerator(possible_tokens)
    sym_table = {}
    
    @pg.error
    def error_handler(token):
        raise Exception(f"{token} at position {token.source_pos} is unexpected.")
    
    #open/close rule
    @pg.production('start : HAI NUMBAR_LITERAL NEWLINE statements KTHXBYE')
    def start(p):
        pass
    @pg.production('statements : statement NEWLINE statements')
    @pg.production('statements : ')
    @pg.production('statement : expr')
    @pg.production('statement : ')
    def statement(p):
        pass
    
    @pg.production('init : op_an ITZ expr')
    @pg.production('init : ')
    def itz(p):
        pass
    @pg.production('expr : IDENTIFIER')
    @pg.production('expr : IDENTIFIER R expr')
    def check_id(p):
        print(p)
        if p[0].value not in sym_table:
            raise Exception("Variable doesn't exist")
    @pg.production('expr : NUMBR_LITERAL')
    @pg.production('expr : BY expr')
    @pg.production('expr : ASSIGNMENT_OPERATOR expr')
    @pg.production('expr : MATH_BINARY_OPERATOR OF expr op_an expr')
    @pg.production('expr : COMPARISON_BINARY_OPERATOR expr op_an expr')
    @pg.production('expr : LOGICAL_BINARY_OPERATOR OF expr op_an expr')
    @pg.production('expr : LOGICAL_UNARY_OPERATOR expr')
    @pg.production('expr : LOGICAL_VARIABLE_OPERATOR OF collexpr MKAY')
    @pg.production('expr : WHATEVR')
    def exp(p):
        pass
    
    @pg.production('collexpr : expr collexpr')
    @pg.production('collexpr : ')
    def collexpr(p):
        pass
    
    @pg.production('op_an : AN')
    @pg.production('op_an : ')
    def op_an(p):
        pass
    
    @pg.production('statement : I HAS A IDENTIFIER ITZ A PRIMITIVE_TYPE init')
    def initialize(p):
        if p[3].value not in sym_table:
            sym_table[p[3].value] = p[6].value
        else:
            raise Exception('Variable already exists')
    @pg.production('statement : ASSIGNMENT_OPERATOR IDENTIFIER expr')
    def assign(p):
        pass
    @pg.production('statement : MATH_UNARY_OPERATOR OF expr')
    def math_uni(p):
        pass
    @pg.production('statement : VISIBLE expr')
    def visible(p):
        pass
    
    return pg.build()

def check_for_lexing_errors(tokens):
    for token in tokens:
        if token.name == 'ERROR':
            raise LexError(f'Lexing error on token ({token.value}) at position {token.source_pos}.')
def parse_LOLcode(lolcode_str):
    lexer = build_lexer()
    #pprint([rule.re for rule in lexer.rules])

    rules_to_ignore = {'LETTR_LITERAL', 'TROOF_LITERAL', 'YARN_LITERAL', 'ERROR'}
    possible_tokens = [rule.name for rule in lexer.rules if rule.name not in rules_to_ignore]
    #pprint(possible_tokens)
    parser = build_parser(possible_tokens)
    if parser.lr_table.sr_conflicts:
        raise ParseError(f'Shift-reduce conflicts {parser.lr_table.sr_conflicts}')
    if parser.lr_table.rr_conflicts:
        raise ParseError(f'Reduce-reduce conflicts {parser.lr_table.rr_conflicts}')

    tokens = list(lexer.lex(lolcode_str))
    check_for_lexing_errors(tokens)
    pprint.pprint(tokens)
    parser.parse(iter(tokens))
