from . rply import ParserGenerator
from . symbol_table import SymbolTable
from . lolcode_lexer import build_lexer
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
        return CodeBlock(p[2])

    @pg.production('code_block : statements')
    def code_block(p):
        return p[0]

    @pg.production('program_header : HAI NUMBAR_LITERAL newlines')
    def program_header(p):
        pass

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
        statement = p[0]
        rest = p[2]
        return [statement] + rest

    @pg.production('statements : ')
    def statements_empty(p):
        return []

    @pg.production('literal_type : PRIMITIVE_TYPE')
    def primitive_type(p):
        return p[0].value

    @pg.production('literal_type_declaration : ITZ A literal_type')
    def primitive_type_declaration(p):
        return p[2]

    @pg.production('statement : I HAS A IDENTIFIER literal_type_declaration optional_intialization')
    def declaration_or_intialization(p):
        if p[5]:
            return InitializationNode(p[3].value, p[4], p[5])
        else:
            return DeclarationNode(p[3].value, p[4])
    @pg.production('optional_an : ')
    @pg.production('optional_an : AN')
    def optional_an(p):
        pass

    @pg.production('optional_intialization : ')
    def no_intialization(p):
        pass
    @pg.production('optional_intialization : optional_an ITZ expression')
    def intialization(p):
        return p[2]

    @pg.production('optional_bang : BANG')
    def bang(p):
        return p[0]
    @pg.production('optional_bang : ')
    def no_bang(p):
        pass

    @pg.production('statement : VISIBLE expression an_expressions optional_bang')
    def visible(p):
        expr = p[1]
        rest = p[2]
        bang = p[3]
        entire = [p[1]] + p[2]
        return VisibleNode(entire, bang)

    @pg.production('expression : GIMMEH')
    def gimmeh(p):
        pass

    @pg.production('expression : WHATEVR')
    def whatevr(p):
        return RandomExpression()

    @pg.production('literal : NUMBR_LITERAL')
    def numbr_literal(p):
        value_str = p[0].value
        return NumbrLiteral(value_str)

    @pg.production('expression : literal')
    def literals_are_expressions(p):
        return p[0]

    @pg.production('var_use : IDENTIFIER')
    def variable_use(p):
        return UseVariableNode(p[0].value)
    
    @pg.production('expression : var_use')
    def variable_use_is_expression(p):
        return p[0]

    @pg.production('expression : var_use R expression')
    def assignment(p):
        lhs = p[0]
        rhs = p[2]
        entire = [lhs, rhs]
        return AssignmentNode(entire)
    
    @pg.production('optional_by_clause :')
    @pg.production('optional_by_clause : BY expression')
    def optional_by_clause(p):
        pass

    @pg.production('expression : assignment_operation')
    def assignment_operator_is_expression(p):
        pass

    @pg.production('assignment_operation : ASSIGNMENT_OPERATOR var_use optional_by_clause')
    def assignment_operation(p):
        pass
    
    @pg.production('statement : expression')
    def expression_is_statement(p):
        return p[0]

    @pg.production('expression : MATH_BINARY_OPERATOR OF expression an_expression')
    def math_binary(p):
        factors = [p[2], p[3]]
        if p[0].value == "SUM":
            return SumNode(factors)
        elif p[0].value == "DIFF":
            return SubNode(factors)
        elif p[0].value == "PRODUKT":
            return MultNode(factors)
        else:
            return DivNode(factors)

    @pg.production('expression : MATH_UNARY_OPERATOR OF expression')
    def math_unary(p):
        token = p[0].value
        if token == "FLIP":
            return FlipNode(p[2])
        elif token == "SQUAR":
            return SquareNode(p[2])
    
    @pg.production('expression : LOGICAL_BINARY_OPERATOR OF expression an_expression')
    def logical_binary(p):
        factors = [p[2], p[3]]
        if p[0].value == "BOTH":
            return BothNode(factors)
        elif p[0].value == "EITHER":
            return EitherNode(factors)
        else:
            return WonNode(factors)

    @pg.production('expression : LOGICAL_UNARY_OPERATOR expression')
    def logical_unary(p):
        return NotNode(p[1])
    
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
        factors = p[2]
        if p[0].value == "ALL":
            return AllNode(p[2])
        else:
            return AnyNode(p[2])

    @pg.production('expression : COMPARISON_BINARY_OPERATOR expression an_expression')
    def logical_binary_expression(p):
        factors = [p[1], p[2]]
        if p[0].value == "SAEM":
            return SAEMNode(factors)
        elif p[0].value == "DIFFRINT":
            return DIFFRINTNode(factors)
        elif p[0].value == "FURSTSMALLR":
            return FSMALLRNode(factors)
        else:
            return FBIGGRNode(factors)

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
    # pprint([(token, token.source_pos) for token in tokens])
    return parser.parse(iter(tokens))