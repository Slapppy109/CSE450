
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

    @pg.production('literal_type_declaration : ITZ opt_lot A literal_type')
    def primitive_type_declaration(p):
        return p[3]
        
    @pg.production('opt_lot : ')
    @pg.production('opt_lot : LOTZ')
    def opt_lot(p):
        pass
        
    @pg.production('statement : I HAS A IDENTIFIER literal_type_declaration optional_intialization')
    def declaration_or_intialization(p):
        name = p[3].getstr()
        declaration_type = p[4]
        array_types = {PrimitiveType.TROOFS, PrimitiveType.NUMBRS,PrimitiveType.LETTRS,PrimitiveType.NUMBARS, PrimitiveType.YARN}
        right_side = p[5]
        if declaration_type in array_types:
            array_node = ArrayDeclaration(children = [name, declaration_type, right_side])
            return array_node
        else:
            left_side = VariableDeclaration(children=[name, declaration_type])
            if not right_side:
                return left_side
            return AssignmentExpression(left_side, right_side)

    @pg.production('optional_an : ')
    @pg.production('optional_an : AN')
    def optional_an(p):
        pass

    @pg.production('optional_intialization : ')
    def empty_init(p):
        return None
    @pg.production('optional_intialization : optional_an ITZ expression')
    def intialization(p):
        return p[2]
        
    @pg.production('optional_intialization : AN THAR IZ expression')
    def array_intialization(p):
        return p[3]

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

    @pg.production('expression : IN ar_idx PUT expression')
    def idx_assignment(p):
        left_side = p[1]
        right_side = p[3]
        return AssignmentExpression(left_side, right_side)
    
    @pg.production('expression : GIMMEH')
    def gimmeh(p):
        return GimmehExpression()

    @pg.production('expression : WHATEVR')
    def whatevr(p):
        return WhatevrExpression()
        
    @pg.production('expression : ar_idx')
    def ar_idx(p):
        return p[0]
    
    @pg.production('ar_idx : var_use \'Z expression')
    def array_index(p):
        array = p[0]
        idx = p[2]
        return ArrayIndex(children=[array, idx])
        
    @pg.production('expression : LENGTHZ OF expression')
    def length_arr(p):
        var_arr = p[2]
        return LengthzExpression(children=[p[2]])

    @pg.production('literal : NUMBR_LITERAL')
    def numbr_literal(p):
        return NumbrLiteral(data=p[0].getstr())

    @pg.production('literal : TROOF_LITERAL')
    def troof_literal(p):
        return TroofLiteral(data=p[0].getstr())

    @pg.production('literal : LETTR_LITERAL')
    def lettr_literal(p):
        return LettrLiteral(data=p[0].getstr())
        
    @pg.production('literal : YARN_LITERAL')
    def yarn_literal(p):
        return YarnLiteral(children=[p[0].getstr()])

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

        delta = by_clause if by_clause else NumbrLiteral('1')
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
        return LogicalExpressionLazy(children=[name, first_operand, second_operand])

    @pg.production('expression : LOGICAL_UNARY_OPERATOR expression')
    def logical_unary(p):
        name = p[0].getstr()
        operand = p[1]
        return LogicalExpressionLazy(children=[name, operand])
    
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
        return LogicalExpressionLazy(children=[name, *expressions])

    @pg.production('expression : COMPARISON_BINARY_OPERATOR expression an_expression')
    def logical_binary_expression(p):
        name = p[0].getstr()
        first_expression = p[1]
        second_expression = p[2]
        return ComparisonExpression(children=[name, first_expression, second_expression])

    @pg.production('statement :  O RLY QUESTION_MARK expression newlines YA RLY newlines code_block optional_no_wai OIC')
    def if_statement(p):
        conditional = p[3]
        if_true_code_block = p[8]
        otherwise_block = p[9]
        return ORLYStatement(children=[conditional, if_true_code_block, otherwise_block])

    @pg.production('optional_no_wai : NO WAI newlines code_block')
    @pg.production('optional_no_wai : ')
    def optional_no_wai(p):
        return p[3] if p else None


    @pg.production('statement : IM IN YR LOOP opt_loop_expr newlines code_block NOW IM OUTTA YR LOOP')
    def loop(p):
        code_block = p[6]
        expr = p[4]
        return LoopStatement(children=[code_block, expr])
    
    @pg.production('opt_loop_expr : ')
    @pg.production('opt_loop_expr : TIL expression')
    def til(p):
        return [p[1]] if p else None
    
    @pg.production('opt_loop_expr : assignment_operation')
    def loop_assign(p):
        return [p[0]]
        
    @pg.production('opt_loop_expr : assignment_operation TIL expression')
    def loop_assign_til(p):
        return [p[0], p[2]]
        
    @pg.production('statement : GTFO')
    def gtfo_clause(p):
        return GTFOStatement()

    return pg.build()




def check_for_lexing_errors(tokens):
    for token in tokens:
        if token.name == 'ERROR':
            raise LexError(f'Lexing error on token ({token.value}) at position {token.source_pos}.')


def parse_LOLcode(lolcode_str):
    lexer, keywords, rules = build_lexer()
    tokens = list(lexer.lex(lolcode_str))
    for token in tokens:
        if token.value in keywords:
            token.name = token.value
        elif token.value in rules:
            token.name = rules[token.value]
    rules_to_ignore = {'ERROR'}
    possible_tokens = [rule.name for rule in lexer.rules if rule.name not in rules_to_ignore]

    parser = build_parser(possible_tokens)
    if parser.lr_table.sr_conflicts:
        raise ParseError(f'Shift-reduce conflicts {parser.lr_table.sr_conflicts}')
    if parser.lr_table.rr_conflicts:
        raise ParseError(f'Reduce-reduce conflicts {parser.lr_table.rr_conflicts}')

    
    #pprint.pprint(tokens)
    check_for_lexing_errors(tokens)

    return parser.parse(iter(tokens))