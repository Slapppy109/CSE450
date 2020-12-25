import abc
from enum import Enum

PrimitiveType = Enum('PrimitiveType', 'NUMBR NUMBAR LETTR TROOF NUMBRS NUMBARS LETTRS TROOFS YARN')
class CompilerTypeError(Exception): pass
class IndexTypeError(Exception): pass


class ASTNode(abc.ABC):
    def __init__(self, children=None):
        self.children = children if children else []
        
    def __repr__(self):
        result = type(self).__name__ # class name
        if self.children:
            children_reprs = [repr(child) for child in self.children]
            children_lines = '\n'.join(children_reprs)
            children_lines_tabbed = map(lambda x: '\t' + x, children_lines.splitlines())
            result += '\n' + '\n'.join(children_lines_tabbed)
        return result

    @abc.abstractmethod
    def compile(self, symbol_table, compiled_code):
        for child in self.children:
            child.compile(symbol_table, compiled_code)


class CodeBlock(ASTNode):
    """
    Represents a block of statements. 
    For instance, the main program or part of a 
    flow control statement. Its children are a list
    of statements.
    """
    def __init__(self, children):
        super().__init__(children=children)

    def compile(self, symbol_table, compiled_code):
        symbol_table.increment_scope()
        super().compile(symbol_table, compiled_code)
        symbol_table.decrement_scope()

class MainProgram(CodeBlock):
    """
    Represents the entire program, has a CodeBlock as
    its only child, and a version
    """
    def __init__(self, children, version):
        super().__init__(children=children)
        assert version.value == '1.450', version

    def compile(self, symbol_table, compiled_code):
        self.children[0].compile(symbol_table, compiled_code)

class PrimitiveLiteral(ASTNode):
    """
    An abstract base class that represents primitive literals
    The string of the value is stored as its only child.
    """
    def __init__(self, data, expr_type):
        super().__init__(children=[data])
        self.expr_type = expr_type

    def compile(self, symbol_table, compiled_code):
        entry = symbol_table.get_entry(expr_type=self.expr_type)
        compiled_code.append(['VAL_COPY', self.children[0], entry])
        return entry

class NumbrLiteral(PrimitiveLiteral):
    """
    An expression that represents a Numbr (like 5).
    The string of the value is stored as its only child.
    """
    def __init__(self, data):
        PrimitiveLiteral.__init__(self, data=data, expr_type=PrimitiveType.NUMBR)

class TroofLiteral(PrimitiveLiteral):
    """
    An expression that represents a Troof (like WIN).
    The string of the value is stored as its only child.
    Note the enclosing quotes are included in the string.
    """
    def __init__(self, data):
        PrimitiveLiteral.__init__(self, data=data, expr_type=PrimitiveType.TROOF)

    def compile(self, symbol_table, compiled_code):
        entry = symbol_table.get_entry(expr_type=self.expr_type)
        value = 1 if self.children[0] == 'WIN' else 0
        compiled_code.append(['VAL_COPY', value, entry])
        return entry

class LettrLiteral(PrimitiveLiteral):
    """
    An expression that represents a Lettr (like 'a').
    The string of the value is stored as its only child.
    Note the enclosing quotes are included in the string.
    """
    def __init__(self, data):
        PrimitiveLiteral.__init__(self, data=data, expr_type=PrimitiveType.LETTR)
    
    def compile(self, symbol_table, compiled_code):
        entry = symbol_table.get_entry(expr_type=self.expr_type)
        lettr = self.children[0] # like ':)'
        mapping_to_lmao_char = {
            "':)'": r"'\n'",
            "':>'": r"'\t'",
            "':''": r"'\''",
            "'::'": r"':'", 
            r"'\'": r"'\\'", 
        } 
        lmao_char = mapping_to_lmao_char.get(lettr, lettr)
        compiled_code.append(['VAL_COPY', lmao_char, entry])
        return entry

class YarnLiteral(ASTNode):
    """
    An expression that represents a YarnLiteral.
    An array of LETTR_LITERALs
    """
    def compile(self, symbol_table, compiled_code):
        escape = {
            ':)': r'\n',
            ':>': r'\t',
            ':\'': r'\'',
            ':"' : r'"',
            '::': r':', 
            r"'\'": r"'\\\'",
        } 
        char_lst = []
        word = self.children[0][1:-1]
        size = len(word)
        i = 0
        while i < size:
            if word[i] == ':':
                if f"{word[i]}{word[i+1]}" in escape:
                    escp_char = word[i] + word[i+1]
                    char_lst.append(escape[escp_char])
                    i += 2
                else:
                    char_lst.append(word[i])
                    i += 1
            else:
                if word[i] == "'":
                    char_lst.append('\\\'')
                    i += 1
                else:
                    char_lst.append(word[i])
                    i += 1
        ar_size = len(char_lst)   
        ar_name = symbol_table.get_entry(PrimitiveType.LETTRS, "a")
        ar_size_entry = NumbrLiteral(ar_size).compile(symbol_table, compiled_code)
        compiled_code.append(['AR_SET_SIZE', ar_name, ar_size_entry])
        
        for i in range(ar_size):
            compiled_code.append(['AR_SET_IDX', ar_name, i, "'{}'".format(char_lst[i])])
        return ar_name
        
class VisibleStatement(ASTNode):
    """
    A statement generated from "VISIBLE <expr>, <expr>, <expr>".
    The expr node is stored as its only child.
    """
    def __init__(self, children, output_newline=True):
        super().__init__(children=children)
        self.output_newline = output_newline

    def compile(self, symbol_table, compiled_code):
        def print_entry(entry, compiled_code):
            if entry.expr_type in {PrimitiveType.NUMBAR, PrimitiveType.NUMBR, PrimitiveType.TROOF}:
                compiled_code.append(['OUT_NUM', entry])
            elif entry.expr_type == PrimitiveType.LETTR:
                compiled_code.append(['OUT_CHAR', entry])
            elif entry.expr_type == 'LETTRS' or entry.expr_type == PrimitiveType.LETTRS or entry.expr_type == PrimitiveType.YARN:
                start_label = symbol_table.get_unique_label(root='visible_array_loop_start')
                end_label = symbol_table.get_unique_label(root='visible_array_loop_end')
                result = symbol_table.get_entry('NUMBR')
                check = symbol_table.get_entry('NUMBR')
                jresult = symbol_table.get_entry('NUMBR')
                out = symbol_table.get_entry('NUMBR')
                compiled_code.append(['AR_GET_SIZE', entry, result])
                compiled_code.append(['VAL_COPY', 0, check])
                compiled_code.append([f'{start_label}:'])
                compiled_code.append(['TEST_GTE', check, result, jresult])
                compiled_code.append(['JUMP_IF_N0', jresult, end_label])
                compiled_code.append(['AR_GET_IDX', entry, check, out])
                compiled_code.append(['OUT_CHAR', out])
                compiled_code.append(['ADD', 1, check, check])
                compiled_code.append(['JUMP', start_label])
                compiled_code.append([f'{end_label}:'])
            else:
                start_label = symbol_table.get_unique_label(root='visible_array_loop_start')
                end_label = symbol_table.get_unique_label(root='visible_array_loop_end')
                result = symbol_table.get_entry('NUMBR')
                check = symbol_table.get_entry('NUMBR')
                jresult = symbol_table.get_entry('NUMBR')
                out = symbol_table.get_entry('NUMBR')
                compiled_code.append(['AR_GET_SIZE', entry, result])
                compiled_code.append(['VAL_COPY', 0, check])
                compiled_code.append([f'{start_label}:'])
                compiled_code.append(['TEST_GTE', check, result, jresult])
                compiled_code.append(['JUMP_IF_N0', jresult, end_label])
                compiled_code.append(['AR_GET_IDX', entry, check, out])
                compiled_code.append(['OUT_NUM', out])
                compiled_code.append(['ADD', 1, check, check])
                compiled_code.append(['JUMP', start_label])
                compiled_code.append([f'{end_label}:'])

        for child in self.children:
            child_entry = child.compile(symbol_table, compiled_code)
            print_entry(child_entry, compiled_code)

        if self.output_newline:
            compiled_code.append(['OUT_CHAR', r"'\n'"])
            
class ArrayDeclaration(ASTNode):
    """
    Declaration of array objects
    """
    def compile(self, symbol_table, compiled_code):
        name, declaration_type, expression = self.children
        array_entry = symbol_table.declare_array(name, declaration_type)
        num_entry = expression.compile(symbol_table, compiled_code)
        print(num_entry)
        compiled_code.append(["AR_SET_SIZE", array_entry, num_entry])
        return array_entry
        
class ArrayIndex(ASTNode):
    """
    Index array objects
    """
    def compile(self, symbol_table, compiled_code):
        array, index = self.children
        array_entry = array.compile(symbol_table, compiled_code)
        index_entry = index.compile(symbol_table, compiled_code)
        if index_entry.expr_type != PrimitiveType.NUMBR or array_entry.address_type != 'a':
            raise IndexTypeError(f"Can't index on type {index_entry.expr_type}")
        type_check = array_entry.expr_type.name
        if type_check == 'NUMBRS':
            primtype = PrimitiveType.NUMBR
        elif type_check == 'LETTRS' or type_check == 'YARN':
            primtype = PrimitiveType.LETTR
        else:
            primtype = PrimitiveType.TROOF
        result = symbol_table.get_entry(primtype)
        compiled_code.append(['AR_GET_IDX', array_entry, index_entry, result])
        return result

class LengthzExpression(ASTNode):
    """
    Expression for returning array length
    """
    def compile(self, symbol_table, compiled_code):
        var = self.children[0]
        var_entry = var.compile(symbol_table, compiled_code)
        if var_entry.address_type == 's':
            raise CompilerTypeError("Can't find length of a non-array type")
        result = symbol_table.get_entry(PrimitiveType.NUMBR)
        compiled_code.append(['AR_GET_SIZE', var_entry, result])
        return result
        
class VariableDeclaration(ASTNode):
    """
    An expression that represents a varible identifier (like x).
    The string of the variable's name and its type are its children.
    """
    def compile(self, symbol_table, compiled_code):
        name, declaration_type  = self.children
        return symbol_table.declare_variable(name, declaration_type)

class VariableUse(ASTNode):
    """
    An expression that represents a varible identifier (like x).
    The string of the variable's name is stored as its only child.
    """
    def compile(self, symbol_table, compiled_code):
        name = self.children[0]
        return symbol_table.get_entry_for_variable(name)

class MathBinaryExpression(ASTNode):
    """
    An expression that represents a math binary operation 
    (like 'SUM OF josh AN 6'). The children consist of
    the operator as a string (like 'SUM'), the first operand,
    and the second operand.
    """
    def compile(self, symbol_table, compiled_code):
        operator, expr_1, expr_2 = self.children
        entry_1 = expr_1.compile(symbol_table, compiled_code)
        entry_2 = expr_2.compile(symbol_table, compiled_code)

        numeric_types = {PrimitiveType.NUMBR, PrimitiveType.NUMBAR}
        if entry_1.expr_type not in numeric_types:
            raise CompilerTypeError(f'{expr_1} is not a numeric type.')
        if entry_2.expr_type not in numeric_types:
            raise CompilerTypeError(f'{expr_1} is not a numeric type.')
        if entry_1.expr_type != entry_2.expr_type:
            raise CompilerTypeError(f'{expr_1} and {expr_2} do not match types.')

        result_entry = symbol_table.get_entry(expr_type=entry_1.expr_type)
        
        math_lol_to_lmao = {
            'SUM': 'ADD',
            'DIFF': 'SUB',
            'PRODUKT': 'MULT',
            'QUOSHUNT': 'DIV',
        }
        lmao_command = math_lol_to_lmao[operator]
        compiled_code.append([lmao_command, entry_1, entry_2, result_entry])


        return result_entry

class MathUnaryExpression(ASTNode):
    """
    An expression that represents a math unary operation 
    (like 'FLIP OF 6'). The children consist of
    the operator as a string (like 'FLIP') and the operand.
    """
    def compile(self, symbol_table, compiled_code):
        operator, expr = self.children
        entry = expr.compile(symbol_table, compiled_code)

        numeric_types = {PrimitiveType.NUMBR, PrimitiveType.NUMBAR}
        if entry.expr_type not in numeric_types:
            raise CompilerTypeError(f'{entry} is not a numeric type.')

        result_entry = symbol_table.get_entry(expr_type=entry.expr_type)
        
        if operator == 'FLIP':
            compiled_code.append(['DIV', 1, entry, result_entry])
        else: # operator == 'SQUAR':
            compiled_code.append(['MULT', entry, entry, result_entry])
        return result_entry


class AssignmentExpression(ASTNode):
    """
    An expression that represents an assignment (like 'toyz R "us"')
    or intializations (like 'I HAS A x ITZ A NUMBR AN ITZ 5').
    Its expr_type is the type of the right side of the assignment
    (YARN and NUMBR in the above examples).
    The left side (the variable expression) and the right side (the value)
    being assigned compose its two children
    """
    def __init__(self, left_side, right_side):
        super().__init__(children=[left_side, right_side])
        
    
    def compile(self, symbol_table, compiled_code):
        yarn_lettrs = {PrimitiveType.YARN, PrimitiveType.LETTRS}
        left_side, right_side = self.children
        right_entry = right_side.compile(symbol_table, compiled_code)
        left_entry = left_side.compile(symbol_table, compiled_code)
        if left_entry.expr_type != right_entry.expr_type:
            if not (left_entry.expr_type in yarn_lettrs and right_entry.expr_type in yarn_lettrs):
                raise CompilerTypeError(f'{left_entry.expr_type} != {right_entry.expr_type}')
        if right_entry.address_type == 'a':
            compiled_code.append(['AR_COPY', right_entry, left_entry])
        else:
            if isinstance(left_side, ArrayIndex):
                var_name = left_side.children[0].children[0]
                lit_address = left_side.children[1]
                var_address = symbol_table.get_entry_for_variable(var_name)
                last_address = compiled_code[-1][2]
                compiled_code.append(['AR_SET_IDX', var_address, last_address, right_entry])
            compiled_code.append(['VAL_COPY', right_entry, left_entry])
        return left_entry

class LogicalExpressionLazy(ASTNode):
    """
    An expression that represents a logical expression 
    (like 'BOTH OF WIN AN FAIL').
    The first child is the operator, and the rest of the children
    are the TROOF expressions to be evaluated.
    Only evaluates as many operands as needed to determine result.
    """
    def compile(self, symbol_table, compiled_code):
        def check_is_troof_and_get_entry(expr):
            entry = expr.compile(symbol_table, compiled_code)
            if entry.expr_type != PrimitiveType.TROOF:
                raise CompilerTypeError(
                    f'Using non-TROOF type {entry.expr_type} in logical expression')
            return entry

        operator = self.children[0]
        
        result_entry = symbol_table.get_entry(expr_type=PrimitiveType.TROOF)
        child_exprs = self.children[1:]

        
        if operator == 'NOT':
            entry = check_is_troof_and_get_entry(child_exprs[0])
            compiled_code.append(['TEST_EQU', entry, 0, result_entry])
        elif operator in {'BOTH', 'ALL', 'EITHER', 'ANY'}:
            lazy_jump_label = symbol_table.get_unique_label(root='logical_lazy_jump')
            for expr in child_exprs:
                entry = check_is_troof_and_get_entry(expr)
                command = 'JUMP_IF_0' if operator in {'BOTH', 'ALL'} else 'JUMP_IF_N0'
                compiled_code.append([command, entry, lazy_jump_label])
            compiled_code.append(['VAL_COPY', entry, result_entry])

            end_label = symbol_table.get_unique_label(root='logical_end')
            compiled_code.append(['JUMP', end_label])
            compiled_code.append([lazy_jump_label + ':'])
            value = 0 if operator in {'BOTH', 'ALL'} else 1
            compiled_code.append(['VAL_COPY', value, result_entry])
            compiled_code.append([end_label + ':'])
        elif operator in {}:
            pass
        else: # operator == 'WON'
            entry_1 = check_is_troof_and_get_entry(child_exprs[0])
            entry_2 = check_is_troof_and_get_entry(child_exprs[1])
            compiled_code.append(['TEST_NEQU', entry_1, entry_2, result_entry])

        return result_entry

class LogicalExpression(ASTNode):
    """
    An expression that represents a logical expression 
    (like 'BOTH OF WIN AN FAIL').
    The first child is the operator, and the rest of the children
    are the TROOF expressions to be evaluated.
    """
    def compile(self, symbol_table, compiled_code):
        operator = self.children[0]
        entries = [expr.compile(symbol_table, compiled_code) 
            for expr in self.children[1:]]
        result_entry = symbol_table.get_entry(expr_type=PrimitiveType.TROOF)
        if operator == 'NOT':
            compiled_code.append(['TEST_EQU', entries[0], 0, result_entry])
        elif operator in {'BOTH', 'EITHER', 'WON'}:
            compiled_code.append(['ADD', entries[0], entries[1], result_entry])
            if operator == 'BOTH': 
                compiled_code.append(['TEST_EQU', result_entry, 2, result_entry])
            elif operator == 'EITHER': 
                compiled_code.append(['TEST_GTE', result_entry, 1, result_entry])
            else: # operator == 'WON': 
                compiled_code.append(['TEST_EQU', result_entry, 1, result_entry])
        else: # operator in {'ALL', 'ANY'}:
            compiled_code.append(['VAL_COPY', 0, result_entry])
            for entry in entries:
                compiled_code.append(['ADD', entry, result_entry, result_entry])
            if operator == 'ALL':
                compiled_code.append(['TEST_EQU', len(entries), result_entry, result_entry])
            else: # operator == 'ANY'
                compiled_code.append(['TEST_GTE', result_entry, 1, result_entry])
        return result_entry



class ComparisonExpression(ASTNode):
    """
    An expression that represents a comparison expression 
    (like 'BOTH SAEM 5 AN 7').
    The first child is the operator, and the rest of the children
    are the two operands.
    """
    def compile(self, symbol_table, compiled_code):
        operator, expr_1, expr_2 = self.children
        entry_1 = expr_1.compile(symbol_table, compiled_code)
        entry_2 = expr_2.compile(symbol_table, compiled_code)
        result_entry = symbol_table.get_entry(expr_type=PrimitiveType.TROOF)
        
        if entry_1.expr_type != entry_2.expr_type:
            compiled_code.append(['VAL_COPY', 0, result_entry])
            return result_entry

        lol_to_lmao = {
            'SAEM': 'TEST_EQU',
            'DIFFRINT': 'TEST_NEQU',
            'FURSTSMALLR': 'TEST_LESS',
            'FURSTBIGGR': 'TEST_GTR',
        }
        lmao_command = lol_to_lmao[operator]
        compiled_code.append([lmao_command, entry_1, entry_2, result_entry])
        return result_entry


class WhatevrExpression(ASTNode):
    """
    A node representing a random NUMBR.
    """
    def __init__(self):
        super().__init__()
    
    def compile(self, symbol_table, compiled_code):
        result_entry = symbol_table.get_entry(expr_type=PrimitiveType.NUMBR)
        compiled_code.append(['RANDOM', result_entry])
        return result_entry

class GimmehExpression(ASTNode):
    """
    A node representing a request of a LETTR from standard input.
    """
    def __init__(self):
        super().__init__()
    
    def compile(self, symbol_table, compiled_code):
        result_entry = symbol_table.get_entry(expr_type=PrimitiveType.LETTR)
        compiled_code.append(['IN_CHAR', result_entry])
        return result_entry

class ORLYStatement(ASTNode):
    """
    A node representing a O RLY? statement.
    Its children are (in the following order):
        a conditional expression,
        a code block (YA RLY),
        a list (possible empty) of mebbe expresions/block pairs,
        a code block (possibly None) of NO WAI

    """
    def __init__(self, children):
        super().__init__(children=children)
    
    def compile(self, symbol_table, compiled_code):
        def compile_and_check_troof(expr):
            entry = expr.compile(symbol_table, compiled_code)
            if entry.expr_type != PrimitiveType.TROOF:
                raise CompilerTypeError(
                    f'{cond_entry.expr_type} is not an acceptable conditional expression')
            return entry
        expr, if_true_block, otherwise_block = self.children
        
        oic_label = symbol_table.get_unique_label(root='oic')
        
        expr = compile_and_check_troof(expr)
        after_label = symbol_table.get_unique_label(root='after_if_true_block')
        compiled_code.append(['JUMP_IF_0', expr, after_label])
        if_true_block.compile(symbol_table, compiled_code)
        compiled_code.append(['JUMP', oic_label])
        compiled_code.append([after_label + ':'])


        if otherwise_block:
            otherwise_block.compile(symbol_table, compiled_code)

        compiled_code.append([oic_label + ':'])
        
class WTFStatement(ASTNode):
    """
    A node representing a WTF? statement.
    Its children are (in the following order):
        a conditional expresions,
        a OMG conditional
        a code block
        other OMG statements
    """
    def __init__(self, children, omgwtf = False):
        super().__init__(children=children)
        self.omgwtf = omgwtf
        
    def compile(self, symbol_table, compiled_code):
        def compile_and_check(main_con, block_con, block, oic_label, switch):
            next_label = symbol_table.get_unique_label(root='next')
            skip_con_label = symbol_table.get_unique_label(root='skip')
            if isinstance(block_con, VariableUse):
                raise TypeError("Conditional shouldn't be a variable")
            block_con_expr = block_con.compile(symbol_table, compiled_code)
            compiled_code.append(['TEST_EQU', switch, 1, switch])
            compiled_code.append(['JUMP_IF_N0', switch, skip_con_label])
            if block_con_expr.address_type == 'a':
                exit_entry = symbol_table.get_entry(PrimitiveType.TROOF)
                con_lettr_size = symbol_table.get_entry(PrimitiveType.NUMBR)
                main_lettr_size = symbol_table.get_entry(PrimitiveType.NUMBR)
                idx_entry = symbol_table.get_entry(PrimitiveType.NUMBR)
                main_lettr = symbol_table.get_entry(PrimitiveType.LETTR)
                cond_lettr = symbol_table.get_entry(PrimitiveType.LETTR)
                
                com_letter_label_start = symbol_table.get_unique_label(root="Compare_Letter_Start")
                com_letter_label_end = symbol_table.get_unique_label(root="Compare_Letter_End")
                
                compiled_code.append(['AR_GET_SIZE', block_con_expr, con_lettr_size])
                compiled_code.append(['AR_GET_SIZE', main_con, main_lettr_size])
                compiled_code.append(['TEST_EQU', con_lettr_size, main_lettr_size, switch])
                compiled_code.append(['JUMP_IF_0', switch, next_label])
                compiled_code.append(['VAL_COPY', 0, idx_entry])
                compiled_code.append([com_letter_label_start + ':'])
                compiled_code.append(['AR_GET_IDX', block_con_expr, idx_entry, cond_lettr])
                compiled_code.append(['AR_GET_IDX', main_con, idx_entry, main_lettr])
                compiled_code.append(['TEST_EQU', cond_lettr, main_lettr, switch])
                compiled_code.append(['ADD', 1, idx_entry, idx_entry])
                compiled_code.append(['JUMP_IF_0', switch, next_label])
                compiled_code.append(['TEST_EQU', idx_entry, main_lettr_size, switch])
                compiled_code.append(['JUMP_IF_N0', switch, com_letter_label_end])
                compiled_code.append(['JUMP', com_letter_label_start])
                compiled_code.append([com_letter_label_end + ':'])
            else:
                compiled_code.append(['TEST_EQU', block_con_expr, main_con, switch])
                compiled_code.append(['JUMP_IF_0', switch, next_label])
                
            yarn_lit = {PrimitiveType.LETTRS, PrimitiveType.YARN}
            if main_con.expr_type != block_con_expr.expr_type:
                if (not(main_con.expr_type in yarn_lit) and not(block_con_expr.expr_type in yarn_lit)):
                    raise TypeError("Wrong type being used for case statement")
            compiled_code.append([skip_con_label + ':'])
            block.compile(symbol_table, compiled_code)
            compiled_code.append([next_label + ':'])
            
        
        condtional = self.children[0]
        omg_blocks = self.children[1:]
        
        switch = symbol_table.get_entry(PrimitiveType.TROOF)
        compiled_code.append(['VAL_COPY', 0, switch])
        oic_label = symbol_table.get_unique_label(root='oic')
        
        symbol_table.push_GTFO_stack(oic_label)
        conditional_expr = condtional.compile(symbol_table, compiled_code)
        while len(omg_blocks):
            if len(omg_blocks) == 1 and self.omgwtf:
                omg_blocks[0].compile(symbol_table,compiled_code)
                compiled_code.append(['JUMP', oic_label])
                break
            else:
                omg_block_conditional = omg_blocks[0]
                omg_block = omg_blocks[1]
                omg_blocks = omg_blocks[2:]
                compile_and_check(conditional_expr, omg_block_conditional, omg_block, oic_label, switch)
        compiled_code.append([oic_label + ':'])
        symbol_table.pop_GTFO_stack()
        
        

class LoopStatement(ASTNode):
    """
    A node representing a loop statement.
    Its children are (in the following order):
        a code block representing the body of the loop
    """
    def compile(self, symbol_table, compiled_code):
        body, expr = self.children

        start_label = symbol_table.get_unique_label(root='loop_start')
        end_label = symbol_table.get_unique_label(root='loop_end')
        compiled_code.append([start_label + ':'])
        if expr:
            if len(expr) > 1:
                exit_entry = expr[1].compile(symbol_table, compiled_code)
                if exit_entry.expr_type != PrimitiveType.TROOF:
                    raise CompilerTypeError("TIL expression not TROOF")
                compiled_code.append(['JUMP_IF_N0', exit_entry, end_label])
            if not isinstance(expr[0], AssignmentExpression):
                exit_entry = expr[0].compile(symbol_table, compiled_code)
                if exit_entry.expr_type != PrimitiveType.TROOF:
                    raise CompilerTypeError("TIL expression not TROOF")
                compiled_code.append(['JUMP_IF_N0', exit_entry, end_label])
        symbol_table.push_GTFO_stack(end_label)

        body.compile(symbol_table, compiled_code)
        if expr:
            if isinstance(expr[0], AssignmentExpression):
                expr[0].compile(symbol_table, compiled_code)
                
        compiled_code.append(['JUMP', start_label])
        compiled_code.append([end_label + ':'])
        symbol_table.pop_GTFO_stack()

class GTFOStatement(ASTNode):
    """
    A node representing a GTFO (break) statement.
    It has no children. It relies on the Symbol Table to determine
    jump destination.
    """
    def compile(self, symbol_table, compiled_code):
        destination = symbol_table.read_GTFO_stack()
        compiled_code.append(['JUMP', destination])