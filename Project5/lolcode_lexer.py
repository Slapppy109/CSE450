import re
from . rply import LexerGenerator
import pprint
def build_lexer():
    rules = {}
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
    lg.add('LETTR_LITERAL', r"'([^:']|(:')|(:>)|(::)|(:\)))'")

    lg.add('YARN_LITERAL', r'(\"([^\":]|(:\")|(::)|(:\))|(:>))*\")')

    # Program Keywords
    keywords |= {'HAI', 'KTHXBYE'}

    primitive_types = ['NUMBRS', 'NUMBARS', 'LETTRS', 'TROOFS', 'NUMBR', 'NUMBAR', 'LETTR', 'TROOF', 'YARN']

    # Primitive Types
    for primitive_type in primitive_types:
        lg.add('PRIMITIVE_TYPE', primitive_type)
    
    lg.add('RLY','RLY')
        # Other words are variable names
    lg.add('IDENTIFIER', r'[a-zA-Z|?][a-zA-Z_0-9|?]*')
    lg.add('QUESTION_MARK', r'\?')
    
    lg.add('TROOF_LITERAL', r'WIN')
    lg.add('TROOF_LITERAL', r'FAIL')
    
    rules['WIN'] = 'TROOF_LITERAL'
    rules['FAIL'] = 'TROOF_LITERAL'
    # IO Keywords
    keywords |= {'VISIBLE', 'GIMMEH', 'WHATEVR'}
    lg.add('BANG', r'!')

    # Declaration and Initialization Keywords
    keywords |= {'I', 'HAS', 'A', 'ITZ', 'AN'}
    
    #ARRAYS
    keywords |= {'LOTZ', 'THAR', 'IZ', '\'Z', 'IN', 'PUT', 'LENGTHZ'}

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
    
    rules['SUM'] = 'MATH_BINARY_OPERATOR'
    rules['DIFF'] = 'MATH_BINARY_OPERATOR'
    rules['PRODUKT'] = 'MATH_BINARY_OPERATOR'
    rules['QUOSHUNT'] = 'MATH_BINARY_OPERATOR'
    rules['BIGGR'] = 'MATH_BINARY_OPERATOR'
    rules['SMALLR'] = 'MATH_BINARY_OPERATOR'
    
    rules['FLIP'] = 'MATH_UNARY_OPERATOR'
    rules['SQUAR'] = 'MATH_UNARY_OPERATOR'

    # LOGICAL OPERATORS
    lg.add('LOGICAL_BINARY_OPERATOR', r'BOTH')
    lg.add('LOGICAL_BINARY_OPERATOR', r'EITHER')
    lg.add('LOGICAL_BINARY_OPERATOR', r'WON')
    lg.add('LOGICAL_UNARY_OPERATOR', r'NOT')
    lg.add('LOGICAL_VARIABLE_OPERATOR', r'ALL')
    lg.add('LOGICAL_VARIABLE_OPERATOR', r'ANY')
    keywords |= {'MKAY'}
    
    rules['BOTH'] = 'LOGICAL_BINARY_OPERATOR'
    rules['EITHER'] = 'LOGICAL_BINARY_OPERATOR'
    rules['WON'] = 'LOGICAL_BINARY_OPERATOR'
    
    rules['NOT'] = 'LOGICAL_UNARY_OPERATOR'
    
    rules['ALL'] = 'LOGICAL_VARIABLE_OPERATOR'
    rules['ANY'] = 'LOGICAL_VARIABLE_OPERATOR'

    # COMPARISON OPERATORS
    lg.add('COMPARISON_BINARY_OPERATOR', r'SAEM')
    # lg.add('COMPARISON_BINARY_OPERATOR', r'DIFFRINT')
    lg.add('COMPARISON_BINARY_OPERATOR', r'FURSTSMALLR')
    lg.add('COMPARISON_BINARY_OPERATOR', r'FURSTBIGGR')
    
    rules['SAEM'] = 'COMPARISON_BINARY_OPERATOR'
    rules['DIFFRINT'] = 'COMPARISON_BINARY_OPERATOR'
    rules['FURSTSMALLR'] = 'COMPARISON_BINARY_OPERATOR'
    rules['FURSTBIGGR'] = 'COMPARISON_BINARY_OPERATOR'

    # ASSIGNMENT OPERATORS
    lg.add('ASSIGNMENT_OPERATOR', r'UPPIN')
    lg.add('ASSIGNMENT_OPERATOR', r'NERFIN')
    keywords |= {'BY'}
    
    rules['UPPIN'] = 'ASSIGNMENT_OPERATOR'
    rules['NERFIN'] = 'ASSIGNMENT_OPERATOR'
    
    # CONDITIONAL STATEMENT
    keywords |= {'O', 'YA', 'NO', 'WAI', 'OIC', 'MEBBE', 'TIL'}
    
    rules[r'?'] = 'QUESTION_MARK'


    # LOOPS
    keywords |= {'IM', 'IN', 'YR', 'LOOP', 'OUTTA', 'NOW', 'GTFO'}
    

    
    for keyword in sorted(keywords, reverse=True):
        lg.add(keyword, keyword)
        
    keywords = sorted(keywords)
    
    lg.add('ERROR', r'.')
    return lg.build(), keywords, rules