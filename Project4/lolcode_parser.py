
from . rply import ParserGenerator

from . symbol_table import SymbolTable
from . lolcode_lexer import build_lexer
from . ast_nodes import *

import pprint 

class ParseError(Exception): pass
class LexError(Exception): pass


def build_parser(possible_tokens):
    pg = ParserGenerator(possible_tokens)
    symbol_table = SymbolTable()

    @pg.error
    def error_handler(token):
        raise ParseError(f'{token} at position {token.source_pos} is unexpected.')

    @pg.production('program : optional_newlines program_header code_block program_footer optional_newlines')
    def program(p):
        version = p[1]
        return MainProgram(children=[p[2]], version=version)

    @pg.production('code_block : statements')
    def code_block(p):
        return CodeBlock(children=p[0])

    @pg.production('program_header : HAI NUMBAR_LITERAL newlines')
    def program_header(p):
        return p[1]

    @pg.production('program_footer : KTHXBYE')
    def program_footer(p):
        pass

    @pg.production('optional_newlines : newlines')
    @pg.production('optional_newlines : ')
    @pg.production('newlines : NEWLINE')
    @pg.production('newlines : NEWLINE newlines')
    def optional_newlines(p):
        pass

    @pg.production('statements : statement newlines statements')
    def statements_nonempty(p):
        return [p[0]] + p[2]

    @pg.production('statements : ')
    def statements_empty(p):
        return []
    @pg.production('literal_type : PRIMITIVE_TYPE')
    def primitive_type(p):
        return PrimitiveType[p[0].getstr()]

    @pg.production('literal_type_declaration : ITZ A literal_type')
    def primitive_type_declaration(p):
        return p[2]

    @pg.production('statement : I HAS A IDENTIFIER literal_type_declaration optional_intialization')
    def declaration_or_intialization(p):
        name = p[3].getstr()
        declaration_type = p[4]
        left_side = VariableDeclaration(children=[name, declaration_type])
        right_side = p[5]

        if not right_side:
            return left_side
        return AssignmentExpression(left_side, right_side)

    @pg.production('optional_an : ')
    @pg.production('optional_an : AN')
    def optional_an(p):
        pass

    @pg.production('optional_intialization : ')
    @pg.production('optional_intialization : optional_an ITZ expression')
    def intialization(p):
        return p[2] if p else None

    @pg.production('optional_bang : BANG')
    @pg.production('optional_bang : ')
    def bang(p):
        return p # p is treated as a boolean

    @pg.production('statement : VISIBLE expression an_expressions optional_bang')
    def visible(p):
        first_expr = p[1]
        other_exprs = p[2]
        output_newline = not p[3]
        return VisibleStatement(children=[p[1], *other_exprs], output_newline=output_newline)
        
    @pg.production('statement : IF_START expression newlines THEN newlines code_block opt_else IF_END')
    def if_statement(p):
        condition = p[1]
        return ORLYStatement(children=[condition, p[5], p[6]])
    @pg.production('opt_else : ELSE newlines code_block')
    def opt_else(p):
        return p[2]
    @pg.production('opt_else : ')
    def opt_else_none(p):
        return CodeBlock(children = None)
        
    @pg.production('statement : BEGIN_LOOP newlines code_block END_LOOP')
    def loop(p):
        return LoopStatement(children = [p[2]])
    @pg.production('expression : GTFO')
    def gtfo(p):
        return GTFOStatement()
    @pg.production('expression : WHATEVR')
    def whatevr(p):
        return WhatevrExpression()
    @pg.production('expression : GIMMEH')
    def gimmeh(p):
        return GimmehExpression()

    @pg.production('literal : NUMBR_LITERAL')
    def numbr_literal(p):
        data = [p[0].value, p[0].name]
        return NumbrLiteral(data=data)
        
    @pg.production('literal : TROOF_LITERAL')
    def troof_literal(p):
        if p[0].value == "WIN":
            value = 1
        else:
            value = 0
        data = [value, p[0].name]
        return TroofLiteral(data=data)
        
    @pg.production('literal : LETTR_LITERAL')
    def lettr_literal(p):
        escape = {
                '\':)\'' : '\'\\n\'',
                '\':>\'' : '\'\\t\'',
                '\':\'\'' : '\'\\\'\'',
                '\'::\'' : '\':\''
            }
        value = p[0].value
        if value in escape:
            value = escape[value]
        data = [value, p[0].name]
        return LettrLiteral(data=data)
        
    @pg.production('expression : literal')
    def literals_are_expressions(p):
        return p[0]

    @pg.production('var_use : IDENTIFIER')
    def variable_use(p):
        return VariableUse(children=[p[0].getstr()])
    
    @pg.production('expression : var_use')
    def variable_use_is_expression(p):
        return p[0]

    @pg.production('expression : var_use R expression')
    def assignment(p):
        left_side = p[0]
        right_side = p[2]
        return AssignmentExpression(left_side, right_side)
    
    @pg.production('optional_by_clause :')
    @pg.production('optional_by_clause : BY expression')
    def optional_by_clause(p):
        if p:
            return p[1]
        return None

    @pg.production('expression : assignment_operation')
    def assignment_operator_is_expression(p):
        return p[0]

    @pg.production('assignment_operation : ASSIGNMENT_OPERATOR var_use optional_by_clause')
    def assignment_operation(p):
        operator = p[0].getstr()
        variable = p[1]
        by_clause = p[2]

        delta = by_clause if by_clause else NumbrLiteral(['1', 'NUMBR'])
        math_operator = 'SUM' if operator == 'UPPIN' else 'DIFF'

        expression = MathBinaryExpression(children=[math_operator, variable, delta])
        return AssignmentExpression(left_side=variable, right_side=expression)
    
    @pg.production('statement : expression')
    def expression_is_statement(p):
        return p[0]

    @pg.production('expression : MATH_BINARY_OPERATOR OF expression an_expression')
    def math_binary(p):
        name = p[0].getstr()
        first_operand = p[2]
        second_operand = p[3]
        return MathBinaryExpression(children=[name, first_operand, second_operand])

    @pg.production('expression : MATH_UNARY_OPERATOR OF expression')
    def math_unary(p):
        name = p[0].getstr()
        operand = p[2]
        return MathUnaryExpression(children=[name, operand])
    
    @pg.production('expression : LOGICAL_BINARY_OPERATOR OF expression an_expression')
    def logical_binary(p):
        name = p[0].getstr()
        first_operand = p[2]
        second_operand = p[3]
        return LogicalLazyExpression(children=[name, first_operand, second_operand])

    @pg.production('expression : LOGICAL_UNARY_OPERATOR expression')
    def logical_unary(p):
        name = p[0].getstr()
        operand = p[1]
        return LogicalLazyExpression(children=[name, operand])
    
    @pg.production('an_expression : optional_an expression')
    def an_expression(p):
        return p[1]

    @pg.production('an_expressions : ')
    def an_expressions_empty(p):
        return []
    
    @pg.production('an_expressions : an_expression an_expressions')
    def an_expressions(p):
        return [p[0]] + p[1]

    @pg.production('expression : LOGICAL_VARIABLE_OPERATOR OF an_expressions MKAY')
    def logical_variable_expression(p):
        name = p[0].getstr()
        expressions = p[2]
        return LogicalLazyExpression(children=[name, *expressions])

    @pg.production('expression : COMPARISON_BINARY_OPERATOR expression an_expression')
    def logical_binary_expression(p):
        name = p[0].getstr()
        first_expression = p[1]
        second_expression = p[2]
        return ComparisonExpression(children=[name, first_expression, second_expression])

    return pg.build()




def check_for_lexing_errors(tokens):
    for token in tokens:
        if token.name == 'ERROR':
            raise LexError(f'Lexing error on token ({token.value}) at position {token.source_pos}.')


def parse_LOLcode(lolcode_str):
    lexer = build_lexer()

    rules_to_ignore = {'YARN_LITERAL', 'ERROR'}
    possible_tokens = [rule.name for rule in lexer.rules if rule.name not in rules_to_ignore]

    parser = build_parser(possible_tokens)
    if parser.lr_table.sr_conflicts:
        raise ParseError(f'Shift-reduce conflicts {parser.lr_table.sr_conflicts}')
    if parser.lr_table.rr_conflicts:
        raise ParseError(f'Reduce-reduce conflicts {parser.lr_table.rr_conflicts}')
    tokens = list(lexer.lex(lolcode_str))
    #pprint.pprint(tokens)
    check_for_lexing_errors(tokens)
    return parser.parse(iter(tokens))