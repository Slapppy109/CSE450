import re
from . rply import LexerGenerator

def build_lexer():
    lg = LexerGenerator()
    keywords = set()

    # Comments
    lg.ignore(r'OBTW.*?TLDR', flags=re.DOTALL)
    lg.ignore(r'BTW.*')

    # Whitespace
    lg.add('NEWLINE', r'\r|\n|(\n\r)|,')
    lg.ignore(r'[ \t]+')

    # Literals
    lg.add('NUMBAR_LITERAL', r'-?[0-9]*\.[0-9]+')
    lg.add('NUMBR_LITERAL', r'-?[0-9]+')
    lg.add('LETTR_LITERAL', r"'(:\'|:\)|:\>|::)'|'[^\']'")
    lg.add('TROOF_LITERAL', r'WIN')
    lg.add('TROOF_LITERAL', r'FAIL')

    lg.add('YARN_LITERAL', r'"[^"\n]*"')

    # Program Keywords
    keywords |= {'HAI', 'KTHXBYE'}

    primitive_types = ['NUMBR', 'NUMBAR', 'LETTR', 'TROOF']

    # Primitive Types
    for primitive_type in primitive_types:
        lg.add('PRIMITIVE_TYPE', primitive_type)

    # IO Keywords
    keywords |= {'VISIBLE', 'GIMMEH', 'WHATEVR'}
    lg.add('BANG', r'!')

    # Declaration and Initialization Keywords
    keywords |= {'I', 'HAS', 'A', 'ITZ', 'AN'}

    # ASSIGNMENT
    keywords |= {'R'}

    # Must be before DIFF
    lg.add('COMPARISON_BINARY_OPERATOR', r'DIFFRINT')

    # MATH OPERATORS
    lg.add('MATH_BINARY_OPERATOR', r'SUM')
    lg.add('MATH_BINARY_OPERATOR', r'DIFF')
    lg.add('MATH_BINARY_OPERATOR', r'PRODUKT')
    lg.add('MATH_BINARY_OPERATOR', r'QUOSHUNT')
    lg.add('MATH_BINARY_OPERATOR', r'BIGGR')
    lg.add('MATH_BINARY_OPERATOR', r'SMALLR')
    lg.add('MATH_UNARY_OPERATOR', r'FLIP')
    lg.add('MATH_UNARY_OPERATOR', r'SQUAR')
    keywords |= {'OF'}

    # LOGICAL OPERATORS
    lg.add('LOGICAL_BINARY_OPERATOR', r'BOTH')
    lg.add('LOGICAL_BINARY_OPERATOR', r'EITHER')
    lg.add('LOGICAL_BINARY_OPERATOR', r'WON')
    lg.add('LOGICAL_UNARY_OPERATOR', r'NOT')
    lg.add('LOGICAL_VARIABLE_OPERATOR', r'ALL')
    lg.add('LOGICAL_VARIABLE_OPERATOR', r'ANY')
    keywords |= {'MKAY'}
    
    # If statements_empty
    lg.add('IF_START', r'O RLY\?')
    lg.add('IF_END', r'OIC')
    lg.add('THEN', r'YA RLY')
    lg.add('ELSE', r'NO WAI')
    
    # Loops
    lg.add('BEGIN_LOOP', r'IM IN YR LOOP')
    lg.add('END_LOOP', r'NOW IM OUTTA YR LOOP')
    lg.add('GTFO', r'GTFO')

    # COMPARISON OPERATORS
    lg.add('COMPARISON_BINARY_OPERATOR', r'SAEM')
    # lg.add('COMPARISON_BINARY_OPERATOR', r'DIFFRINT')
    lg.add('COMPARISON_BINARY_OPERATOR', r'FURSTSMALLR')
    lg.add('COMPARISON_BINARY_OPERATOR', r'FURSTBIGGR')

    # ASSIGNMENT OPERATORS
    lg.add('ASSIGNMENT_OPERATOR', r'UPPIN')
    lg.add('ASSIGNMENT_OPERATOR', r'NERFIN')
    keywords |= {'BY'}

    for keyword in sorted(keywords, reverse=True):
        lg.add(keyword, keyword)

    # Other words are variable names
    lg.add('IDENTIFIER', r'[a-zA-Z][a-zA-Z_0-9]*')
    lg.add('ERROR', r'.')

    return lg.build()