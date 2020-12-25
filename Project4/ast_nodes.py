import abc
from . symbol_table import Data
import inspect

from enum import Enum

class TypeError(Exception): pass

PrimitiveType = Enum('PrimitiveType', 'NUMBR LETTR TROOF')

class ASTNode(abc.ABC):
    def __init__(self, children=None):
        self.children = children if children else []

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
    
    def __repr__(self):
        return f"CodeBlock({self.children})"

    def compile(self, symbol_table, compiled_code):
        super().compile(symbol_table, compiled_code)

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
    def __init__(self, data):
        super().__init__(children=[data])

    def compile(self, symbol_table, compiled_code):
        entry = symbol_table.get_entry()
        compiled_code.append(['VAL_COPY', self.children[0][0], entry])
        #print(self.children[0])
        node_data = Data(entry, self.children[0][1])
        return node_data

class LettrLiteral(PrimitiveLiteral):
    def __init__(self, data):
        PrimitiveLiteral.__init__(self, data=data)
        
    def __repr__(self):
        return f"LettrLiteral({self.children})"
        
class NumbrLiteral(PrimitiveLiteral):
    """
    An expression that represents a Numbr (like 5).
    The string of the value is stored as its only child.
    """
    def __init__(self, data):
        PrimitiveLiteral.__init__(self, data=data)
    
    def __repr__(self):
        return f"NumbrLiteral({self.children})"
        
class TroofLiteral(PrimitiveLiteral):
    def __init__(self, data):
        PrimitiveLiteral.__init__(self, data=data)
        
    def __repr__(self):
        return f"TroofLiteral({self.children})"
        
class VisibleStatement(ASTNode):
    """
    A statement generated from "VISIBLE <expr>, <expr>, <expr>".
    The expr node is stored as its only child.
    """
    def __init__(self, children, output_newline=True):
        super().__init__(children=children)
        self.output_newline = output_newline
        
    def __repr__(self):
        return f"VisibleStatement({self.children})"

    def compile(self, symbol_table, compiled_code):
        def print_entry_num(entry, compiled_code):
            compiled_code.append(['OUT_NUM', entry])
            
        def print_entry_char(entry, compiled_code):
            compiled_code.append(['OUT_CHAR', entry])

        for child in self.children:
            child_entry = child.compile(symbol_table, compiled_code)
            child_entry_address = child_entry.address
            try:
                prim_type = child_entry.data_type.name
            except:
                prim_type = ''
            
            if child_entry.data_type == 'LETTR_LITERAL' or prim_type== 'LETTR':
                print_entry_char(child_entry_address,compiled_code)
            else:
                print_entry_num(child_entry_address, compiled_code)

        if self.output_newline:
            compiled_code.append(['OUT_CHAR', r"'\n'"])

class ORLYStatement(ASTNode):
    def __init__(self, children):
        super().__init__(children=children)
        
    def __repr__(self):
        return f"ORLYStatement({self.children})"
        
    def compile(self, symbol_table, compiled_code):
        symbol_table.scope += 1
        oic_label = symbol_table.get_oic_label()
        if_con_label = symbol_table.get_if_true_jump_label()
        condition_node = self.children[0].compile(symbol_table, compiled_code)
        condition_node_type = condition_node.data_type
        try:
            condition_node_type = condition_node_type.name
        except:
            pass
        troof = {'TROOF_LITERAL', 'TROOF'}
        if not(condition_node_type in troof):
            raise TypeError("Incorrect Typing")
        condition_node_address = condition_node.address
        compiled_code.append(['JUMP_IF_0', condition_node_address, if_con_label])
        then_statement = self.children[1].compile(symbol_table, compiled_code)
        compiled_code.append(['JUMP', oic_label])
        compiled_code.append([f"{if_con_label}:"])
        else_statement = self.children[2].compile(symbol_table, compiled_code)
        compiled_code.append([f"{oic_label}:"])
        symbol_table.scope -= 1

class LoopStatement(ASTNode):
    def __init__(self, children):
        super().__init__(children=children)
        
    def __repr__(self):
        return f"LoopStatement({self.children})"
        
    def compile(self, symbol_table, compiled_code):
        symbol_table.scope += 1
        startlabel = symbol_table.get_loop_start_label()
        endlabel = symbol_table.get_loop_end_label()
        symbol_table.loop_stack.append(endlabel)
        compiled_code.append([f'{startlabel}:'])
        self.children[0].compile(symbol_table, compiled_code)
        compiled_code.append(['JUMP', startlabel])
        compiled_code.append([f'{endlabel}:'])
        
class GTFOStatement(ASTNode):
    
    def __repr__(self):
        return f"GTFOStatement({self.children})"
        
    def compile(self,symbol_table, compiled_code):
        symbol_table.scope -= 1
        endlabel = symbol_table.loop_stack.pop()
        compiled_code.append(['JUMP', endlabel])

class VariableDeclaration(ASTNode):
    """
    An expression that represents a varible identifier (like x).
    The string of the variable's name and its type are its children.
    """
    
    def __repr__(self):
        return f"VariableDeclaration({self.children})"
        
    def compile(self, symbol_table, compiled_code):
        name, declaration_type  = self.children
        node_data = symbol_table.declare_variable(name, declaration_type)
        return node_data

class VariableUse(ASTNode):
    """
    An expression that represents a varible identifier (like x).
    The string of the variable's name is stored as its only child.
    """
    def __repr__(self):
        return f"UseVariableNode({self.children})"
        
    def compile(self, symbol_table, compiled_code):
        name = self.children[0]
        node_data = symbol_table.get_entry_for_variable(name)
        return node_data

class MathBinaryExpression(ASTNode):
    """
    An expression that represents a math binary operation 
    (like 'SUM OF josh AN 6'). The children consist of
    the operator as a string (like 'SUM'), the first operand,
    and the second operand.
    """
    def __repr__(self):
        return f"MathBinaryExpression({self.children})"
        
    def compile(self, symbol_table, compiled_code):
        operator, expr_1, expr_2 = self.children
        entry_1 = expr_1.compile(symbol_table, compiled_code)
        entry_2 = expr_2.compile(symbol_table, compiled_code)

        result_entry = symbol_table.get_entry()
        
        try:
            prim1 = entry_1.data_type.name
        except:
            prim1 = entry_1.data_type
            
        try:
            prim2 = entry_2.data_type.name
        except:
            prim2 = entry_2.data_type

        NUMBR = ['NUMBR_LITERAL', 'NUMBR']

        if not (prim1 in NUMBR) or not (prim2 in NUMBR):
            raise TypeError("Incorrect Typing")
            
            

        if isinstance(entry_1, Data):
            entry_1 = entry_1.address
        if isinstance(entry_2, Data):
            entry_2 = entry_2.address
            
        math_lol_to_lmao = {
            'SUM': 'ADD',
            'DIFF': 'SUB',
            'PRODUKT': 'MULT',
            'QUOSHUNT': 'DIV',
        }
        lmao_command = math_lol_to_lmao[operator]
        compiled_code.append([lmao_command, entry_1, entry_2, result_entry])

        node_data = Data(result_entry, "NUMBR_LITERAL")
        return node_data

class MathUnaryExpression(ASTNode):
    """
    An expression that represents a math unary operation 
    (like 'FLIP OF 6'). The children consist of
    the operator as a string (like 'FLIP') and the operand.
    """
    def __repr__(self):
        return f"MathUnaryExpression({self.children})"
        
    def compile(self, symbol_table, compiled_code):
        operator, expr = self.children
        entry = expr.compile(symbol_table, compiled_code)

        result_entry = symbol_table.get_entry()
        
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
        
    def __repr__(self):
        return f"AssignmentExpression({self.children})"
        
    def compile(self, symbol_table, compiled_code):
        left_side, right_side = self.children
        right_entry = right_side.compile(symbol_table, compiled_code)
        left_entry = left_side.compile(symbol_table, compiled_code)
        left_reformat = left_entry.data_type.name
        left_reformat = left_reformat + "_LITERAL"
        if left_reformat != right_entry.data_type:
            raise TypeError("Incorrect Typing")
        left_address = left_entry.address
        right_address = right_entry.address
        compiled_code.append(['VAL_COPY', right_address, left_address])
        return left_entry
'''
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
        result_entry = symbol_table.get_entry()
        if operator == 'NOT':
            if isinstance(entries[0], Data):
                entries[0] = entries[0].address
            compiled_code.append(['TEST_EQU', entries[0], 0, result_entry])
        elif operator in {'BOTH', 'EITHER', 'WON'}:
            if entries[0].data_type != entries[1].data_type:
                raise TypeError("Incorrect Typing")
            entry_1_address = entries[0].address
            entry_2_addres = entries[1].address
            lazy_label = symbol_table.get_logical_lazy_jump_label()
            end_lazy = symbol_table.get_logical_end_label()
            if operator == 'BOTH': 
                compiled_code.append(['JUMP_IF_0', entry_1_address, 0, lazy_label])
                 compiled_code.append(['JUMP_IF_0', entry_2_address, 0, lazy_label])
            elif operator == 'EITHER': 
                compiled_code.append(['TEST_GTE', result_entry, 1, result_entry])
            else: # operator == 'WON': 
                compiled_code.append(['TEST_EQU', result_entry, 1, result_entry])
        else: # operator in {'ALL', 'ANY'}:
            compiled_code.append(['VAL_COPY', 0, result_entry])
            for entry in entries:
                if isinstance(entry, Data):
                    entry = entry.address
                compiled_code.append(['ADD', entry, result_entry, result_entry])
            if operator == 'ALL':
                compiled_code.append(['TEST_EQU', len(entries), result_entry, result_entry])
            else: # operator == 'ANY'
                compiled_code.append(['TEST_GTE', result_entry, 1, result_entry])
        
        node_data = Data(result_entry, "TROOF_LITERAL")
        return node_data
'''
class LogicalLazyExpression(ASTNode):
    
    def __repr__(self):
        return f"LogicalLazyExpression({self.children})"
        
    def compile(self, symbol_table, compiled_code):
        
        def fail_lazy(lazy, end, compiled_code, result):
            compiled_code.append([f'{lazy}:'])
            compiled_code.append(['VAL_COPY', 0, result])
            compiled_code.append([f'{end}:'])
            
        def win_lazy(lazy, end, compiled_code, result):
            compiled_code.append([f'{lazy}:'])
            compiled_code.append(['VAL_COPY', 1, result])
            compiled_code.append([f'{end}:'])
            
        operator = self.children[0]
        nodes = self.children[1:]
        result_entry = symbol_table.get_entry()
        lazy_label = symbol_table.get_logical_lazy_jump_label()
        end_lazy = symbol_table.get_logical_end_label()
        node_types = []
        if operator == 'NOT':
            target_node = nodes[0].compile(symbol_table, compiled_code)
            target_node_address = target_node.address
            compiled_code.append(['TEST_EQU', target_node_address, 0, result_entry])
        else:
            if operator == 'BOTH' or operator == 'ALL':
                for node in nodes:
                    target_node = node.compile(symbol_table, compiled_code)
                    entry_address = target_node.address
                    compiled_code.append(['JUMP_IF_0', entry_address, lazy_label])
                    node_types.append(target_node.data_type)
                compiled_code.append(['VAL_COPY', entry_address, result_entry])
                compiled_code.append(['JUMP', end_lazy])
                fail_lazy(lazy_label, end_lazy, compiled_code, result_entry)
            elif operator == 'EITHER' or operator == 'ANY':
                for node in nodes:
                    target_node = node.compile(symbol_table, compiled_code)
                    entry_address = target_node.address
                    compiled_code.append(['JUMP_IF_N0', entry_address, lazy_label])
                    node_types.append(target_node.data_type)
                compiled_code.append(['VAL_COPY', entry_address, result_entry])
                compiled_code.append(['JUMP', end_lazy])
                win_lazy(lazy_label, end_lazy, compiled_code, result_entry)
            elif operator == 'WON':
                target_node1 = nodes[0].compile(symbol_table, compiled_code)
                node_types.append(target_node1.data_type)
                entry1_address = target_node1.address
                target_node2 = nodes[1].compile(symbol_table, compiled_code)
                node_types.append(target_node1.data_type)
                entry2_address = target_node2.address
                compiled_code.append(['TEST_NEQU', entry1_address, entry2_address, result_entry])
            type1 = node_types[0]
            type2 = node_types[1]
            try:
                type1 = type1.name
            except:
                type1 = node_types[0]
            try:
                type2 = type2.name
            except:
                type2 = node_types[1]
            types = [type1, type2]
            check_types = []
            Prim = {'NUMBR', 'TROOF', 'LETTR'}
            for elm in types:
                if elm in Prim:
                    elm = elm + '_LITERAL'
                check_types.append(elm)
            if (check_types[0] != check_types[1]):
                    raise TypeError("Incorrect Typing")
            node_types.clear()
        node_data = Data(result_entry, "TROOF_LITERAL")
        return node_data

class ComparisonExpression(ASTNode):
    """
    An expression that represents a comparison expression 
    (like 'BOTH SAEM 5 AN 7').
    The first child is the operator, and the rest of the children
    are the two operands.
    """
    def __repr__(self):
        return f"ComparisonExpression({self.children})"
        
    def compile(self, symbol_table, compiled_code):
        operator, expr_1, expr_2 = self.children
        entry_1 = expr_1.compile(symbol_table, compiled_code)
        entry_2 = expr_2.compile(symbol_table, compiled_code)
        result_entry = symbol_table.get_entry()
        node_data = Data(result_entry, "TROOF_LITERAL")
        
        entry_1_address = entry_1.address
        entry_2_address = entry_2.address
        
        type1 = entry_1.data_type
        type2 = entry_2.data_type
        
        try:
            type1 = type1.name
        except:
            type1 = entry_1.data_type
        try:
            type2 = type2.name
        except:
            type2 = entry_2.data_type
        types = [type1, type2]
        check_types = []
        Prim = {'NUMBR', 'TROOF', 'LETTR'}
        for elm in types:
            if elm in Prim:
                elm = elm + '_LITERAL'
            check_types.append(elm)
        if (check_types[0] != check_types[1]):
            compiled_code.append(['VAL_COPY', 0, result_entry])
            return node_data
            
        lol_to_lmao = {
            'SAEM': 'TEST_EQU',
            'DIFFRINT': 'TEST_NEQU',
            'FURSTSMALLR': 'TEST_LESS',
            'FURSTBIGGR': 'TEST_GTR',
        }
        lmao_command = lol_to_lmao[operator]
        compiled_code.append([lmao_command, entry_1_address, entry_2_address, result_entry])
        return node_data


class WhatevrExpression(ASTNode):
    """
    A node representing a random NUMBR.
    """
    def __init__(self):
        super().__init__()
    
    def compile(self, symbol_table, compiled_code):
        result_entry = symbol_table.get_entry()
        compiled_code.append(['RANDOM', result_entry])
        data_node = Data(result_entry, "NUMBR_LITERAL")
        return data_node
        
class GimmehExpression(ASTNode):
    def __init__(self):
        super().__init__()
    
    def compile(self, symbol_table, compiled_code):
        result_entry = symbol_table.get_entry()
        compiled_code.append(['IN_CHAR', result_entry])
        data_node = Data(result_entry, "LETTR_LITERAL")
        return data_node
