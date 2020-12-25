
from . rply import ParserGenerator

from . symbol_table import SymbolTable
from . lolcode_lexer import get_tokens_and_types
from . ast_nodes import *



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

    @pg.production('expression : GIMMEH')
    def gimmeh(p):
        return GimmehExpression()

    @pg.production('expression : WHATEVR')
    def whatevr(p):
        return WhatevrExpression()

    @pg.production('literal : NUMBR_LITERAL')
    def numbr_literal(p):
        return NumbrLiteral(data=p[0].getstr())

    @pg.production('literal : TROOF_LITERAL')
    def troof_literal(p):
        return TroofLiteral(data=p[0].getstr())

    @pg.production('literal : LETTR_LITERAL')
    def lettr_literal(p):
        return LettrLiteral(data=p[0].getstr())

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


    @pg.production('statement : IM IN YR LOOP optional_assignment_expression optional_til_expression newlines code_block NOW IM OUTTA YR LOOP')
    def loop(p):
        assign_expression = p[4]
        til_expression = p[5]
        code_block = p[7]
        return LoopStatement(children=[assign_expression, til_expression, code_block])
    
    @pg.production('optional_til_expression : ')
    @pg.production('optional_til_expression : TIL expression')
    def loop(p):
        if not p:
            return None
        return p[1]
    
    @pg.production('optional_assignment_expression :')
    @pg.production('optional_assignment_expression : assignment_operation')
    def optional_assignment_expression(p):
        if not p:
            return None
        return p[0]


    @pg.production('statement : GTFO')
    def gtfo_clause(p):
        return GTFOStatement()

    
    @pg.production('literal : YARN_LITERAL')
    def yarn_literal(p):
        return YarnLiteral(children=[p[0].getstr()])

    @pg.production('array_type_declaration : ITZ LOTZ A ARRAY_TYPE')
    def array_type_declaration(p):
        array_type_name = p[3].getstr()
        type_name_without_s = array_type_name[:-1]
        subtype = PrimitiveType[type_name_without_s]
        return ArrayType(subtype=subtype)
    
    @pg.production('array_type_declaration : ITZ A YARN')
    def array_type_declaration(p):
        return ArrayType(PrimitiveType.LETTR)
    
    @pg.production('statement : I HAS A IDENTIFIER array_type_declaration optional_an THAR IZ expression')
    def array_declaration(p):
        name = p[3].getstr()
        array_type = p[4]
        size_expr = p[8]
        return ArrayDeclaration(children=[name, array_type, size_expr])
    
    @pg.production('array_index : var_use INDEX_OPERATOR expression')
    def indexing(p):
        array_var = p[0]
        index_expr = p[2]
        return ArrayIndex(children=[array_var, index_expr])

    @pg.production('expression : array_index')
    def array_index_is_expression(p):
        return p[0]
    
    @pg.production('expression : IN array_index PUT expression')
    def array_assignment(p):
        left_side = p[1]
        right_side = p[3]
        return AssignmentExpression(left_side, right_side)
    
    @pg.production('expression : LENGTHZ OF expression')
    def lengthz(p):
        return LengthzExpression(children=[p[2]])
    
    @pg.production('statement :  WTF QUESTION_MARK expression newlines match_cases  OIC')
    def case_statement(p):
        expression = p[2]
        match_cases = p[4]
        return CaseStatement(children=[expression, match_cases])
    
    @pg.production('match_cases : optional_default_case')
    def optional_match_cases_empty(p):
        return p[0]
    
    @pg.production('match_cases : OMG literal newlines code_block match_cases')
    def optional_match_cases(p):
        literal = p[1]
        block = p[3]
        match = [literal, block]
        return [match] + p[4]
    
    @pg.production('optional_default_case : ')
    def optional_default_empty(p):
        return []
    
    @pg.production('optional_default_case : OMGWTF newlines code_block')
    def optional_default(p):
        block = p[2]
        match = [block]
        return [match]
        
    @pg.production('statement : HOW IZ I IDENTIFIER optional_args MKAY newlines code_block IF U SAY SO type_declaration')
    def function(p):
        func_name = p[3].getstr()
        args = p[4]
        code_block = p[7]
        return_type = p[12]
        func = [func_name, args, code_block, return_type]
        return FunctionStatement(children = func)
    
    @pg.production('statement : FOUND YR expression')
    def return_statement(p):
        return ReturnStatement([p[2]])
        
    @pg.production('args : YR IDENTIFIER type_declaration')
    def arguments(p):
        args = [(p[1].getstr(), p[2])]
        return args
        
    @pg.production('optional_args : ')
    @pg.production('optional_args : args optional_an optional_args')
    def optional_args(p):
        if p:
            return p[0] + p[2]
        else:
            return []
    
    @pg.production('type_declaration : literal_type_declaration')
    @pg.production('type_declaration : array_type_declaration')
    def type_declaration(p):
        return p[0]
        
    @pg.production('expression : I IZ IDENTIFIER optional_YR MKAY')
    def function_call(p):
        return FunctionCallExpression([p[2].getstr(), p[3]])
    
    @pg.production('yr : YR expression')
    def func_call_arg(p):
        return [p[1]]
        
    @pg.production('optional_YR : ')
    @pg.production('optional_YR : yr optional_an optional_YR')
    def func_call_arg_optional(p):
        if p:
            return p[0] + p[2] 
        else:
            return []
            
    return pg.build()




def check_for_lexing_errors(tokens):
    for token in tokens:
        if token.name == 'ERROR':
            raise LexError(f'Lexing error on token ({token.value}) at position {token.source_pos}.')


def parse_LOLcode(lolcode_str):

    tokens, token_types = get_tokens_and_types(lolcode_str)

    parser = build_parser(token_types)
    if parser.lr_table.sr_conflicts:
        raise ParseError(f'Shift-reduce conflicts {parser.lr_table.sr_conflicts}')
    if parser.lr_table.rr_conflicts:
        raise ParseError(f'Reduce-reduce conflicts {parser.lr_table.rr_conflicts}')

    check_for_lexing_errors(tokens)
    # pprint([(token, token.source_pos) for token in tokens])
    return parser.parse(iter(tokens))