import re
from . rply import LexerGenerator
from . ast_nodes import PrimitiveType

def get_tokens_and_types(input_):
    lg = LexerGenerator()
    keywords = set()
    id_to_type = {}

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
    id_to_type['WIN'] = 'TROOF_LITERAL'
    id_to_type['FAIL'] = 'TROOF_LITERAL'

    lg.add('YARN_LITERAL', r'"([^:"]|(:")|(:>)|(::)|(:\)))*"')

    # Program Keywords
    keywords |= {'HAI', 'KTHXBYE'}

    # Array Types
    for primitive_type in PrimitiveType:
        id_to_type[primitive_type.name + 'S'] = 'ARRAY_TYPE'

    # Primitive Types
    for primitive_type in PrimitiveType:
        id_to_type[primitive_type.name] = 'PRIMITIVE_TYPE'

    # IO Keywords
    keywords |= {'VISIBLE', 'GIMMEH', 'WHATEVR'}
    lg.add('BANG', r'!')

    # Declaration and Initialization Keywords
    keywords |= {'I', 'HAS', 'A', 'ITZ', 'AN'}

    # ASSIGNMENT
    keywords |= {'R'}

    

    # MATH OPERATORS
    id_to_type['SUM'] = 'MATH_BINARY_OPERATOR'
    id_to_type['DIFF'] = 'MATH_BINARY_OPERATOR'
    id_to_type['PRODUKT'] = 'MATH_BINARY_OPERATOR'
    id_to_type['QUOSHUNT'] = 'MATH_BINARY_OPERATOR'
    id_to_type['BIGGR'] = 'MATH_BINARY_OPERATOR'
    id_to_type['SMALLR'] = 'MATH_BINARY_OPERATOR'
    id_to_type['FLIP'] = 'MATH_UNARY_OPERATOR'
    id_to_type['SQUAR'] = 'MATH_UNARY_OPERATOR'
    keywords |= {'OF'}

    # LOGICAL OPERATORS
    id_to_type['BOTH'] = 'LOGICAL_BINARY_OPERATOR'
    id_to_type['EITHER'] = 'LOGICAL_BINARY_OPERATOR'
    id_to_type['WON'] = 'LOGICAL_BINARY_OPERATOR'
    id_to_type['NOT'] = 'LOGICAL_UNARY_OPERATOR'
    id_to_type['ALL'] = 'LOGICAL_VARIABLE_OPERATOR'
    id_to_type['ANY'] = 'LOGICAL_VARIABLE_OPERATOR'
    keywords |= {'MKAY'}

    # COMPARISON OPERATORS
    id_to_type['SAEM'] = 'COMPARISON_BINARY_OPERATOR'
    id_to_type['DIFFRINT'] = 'COMPARISON_BINARY_OPERATOR'
    id_to_type['FURSTSMALLR'] = 'COMPARISON_BINARY_OPERATOR'
    id_to_type['FURSTBIGGR'] = 'COMPARISON_BINARY_OPERATOR'

    # ASSIGNMENT OPERATORS
    id_to_type['UPPIN'] = 'ASSIGNMENT_OPERATOR'
    id_to_type['NERFIN'] = 'ASSIGNMENT_OPERATOR'
    keywords |= {'BY'}

    # CONDITIONAL STATEMENT
    keywords |= {'O', 'RLY', 'YA', 'NO', 'WAI', 'OIC'}
    lg.add('QUESTION_MARK', r'\?')


    # LOOPS
    keywords |= {'IM', 'IN', 'YR', 'LOOP', 'OUTTA', 'NOW', 'GTFO'}
    # LOOPS For Project 5
    keywords |= {'TIL'}

    # ARRAYS
    keywords |= {'YARN', 'LOTZ', 'THAR', 'IZ', 'PUT', 'IN', 'LENGTHZ'} 
    lg.add('INDEX_OPERATOR', r"'Z")
    
    # FUNCTIONS
    keywords |= {'HOW', 'IF', 'U', 'SAY', 'SO', 'FOUND'}

    # Other words are variable names
    lg.add('IDENTIFIER', r'[a-zA-Z][a-zA-Z_0-9]*')
    lg.add('ERROR', r'.')

    # CASE
    keywords |= {'WTF', 'OMG', 'OMGWTF', 'OIC'}

    lexer = lg.build()

    tokens = list(lexer.lex(input_))

    for token in tokens:
        lexeme = token.value
        if lexeme in keywords:
            token.name = token.value
        elif lexeme in id_to_type:
            token.name = id_to_type[lexeme]

    rules_to_ignore = {'ERROR'}
    token_types = [rule.name for rule in lexer.rules if rule.name not in rules_to_ignore]
    token_types.extend(keywords)
    token_types.extend(set(id_to_type.values()))
    return tokens, token_types
