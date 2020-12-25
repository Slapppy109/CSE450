class CodeBlock:
    def __init__(self, statements):
        self.statements = statements
    
    def __repr__(self):
        return f"CodeBlock({self.statements})"
    
    def compile(self, compiled_code, symbol_table):
        if self.statements == None:
                return None
        for statement in self.statements:
            statement.compile(compiled_code, symbol_table)
            
class NumbrLiteral:
    """
    An expression that represents a Numbr (like 5).
    The string of the value is stored as its only child.
    """
    def __init__(self, value):
        self.value = value
    
    def __repr__(self):
        return f"NumbrLiteral({self.value})"
    
    def compile(self, compiled_code, symbol_table):
        destination = symbol_table.get_new_s_location()
        compiled_code.append(f"VAL_COPY {self.value} {destination}")
        return destination
            
class VisibleNode:
    def __init__(self, children, bang = None):
        self.children = children
        self.bang = bang
    
    def __repr__(self):
        return f"VisibleNode({self.children})"
    
    def compile(self, compiled_code, symbol_table):
        for child in self.children:
            address = child.compile(compiled_code, symbol_table)
            compiled_code.append(f'OUT_NUM {address}')
        if self.bang == None:
            compiled_code.append(f"OUT_CHAR '\\n'")

class DeclarationNode:
    def __init__(self, name, type):
        self.name = name
        self.type = type
    
    def __repr__(self):
        return f"DeclarationNode({self.name}, {self.type})"
    
    def compile(self, compiled_code, symbol_table):
        # Type Checking
        symbol_table.declare_variable(self.name, self.type)
        destination = symbol_table.get_new_s_location()
        symbol_table.add_sym(self.name, destination)
        return destination
            
class UseVariableNode:
    def __init__(self, name):
        self.name = name
        
    def __repr__(self):
        return f"UseVariableNode({self.name})"
    
    def compile(self, compiled_code, symbol_table):
        # Type Checking
        symbol_table.use_variable(self.name)
        return symbol_table.find_destination(self.name)
        
        
class AssignmentNode:
    def __init__(self, children):
        self.children = children
        
    def __repr__(self):
        return f"AssignmentNode({self.children})"
    
    def compile(self, compiled_code, symbol_table):
        lhs, rhs = self.children
        lhs_location = lhs.compile(compiled_code, symbol_table)
        rhs_location = rhs.compile(compiled_code, symbol_table)
        
        compiled_code.append(f"VAL_COPY {rhs_location} {lhs_location}")
        return lhs_location
            
class InitializationNode:
    def __init__(self, name, type, value):
        self.name = name
        self.type = type
        self.value = value
    def __repr__(self):
        return f"InitializationNode({self.name}, {self.type}, {self.value})"
    def compile(self, compiled_code, symbol_table):
        symbol_table.declare_variable(self.name, self.type)
        destination = symbol_table.get_new_s_location()
        symbol_table.add_sym(self.name, destination)
        rhs_location = self.value.compile(compiled_code, symbol_table)
        compiled_code.append(f"VAL_COPY {rhs_location} {destination}")
        return destination

class SumNode:
    def __init__(self, children):
        self.children = children
        
    def __repr__(self):
        return f"SumNode({self.children})"    
            
    def compile(self, compiled_code, symbol_table):
        factor1, factor2 = self.children
        factor1_location = factor1.compile(compiled_code, symbol_table)
        factor2_location = factor2.compile(compiled_code, symbol_table)
        
        destination = symbol_table.get_new_s_location()
        compiled_code.append(f"ADD {factor1_location} {factor2_location} {destination}")
        return destination
        
class SubNode:
    def __init__(self, children):
        self.children = children
        
    def __repr__(self):
        return f"SubNode({self.children})"    
            
    def compile(self, compiled_code, symbol_table):
        factor1, factor2 = self.children
        factor1_location = factor1.compile(compiled_code, symbol_table)
        factor2_location = factor2.compile(compiled_code, symbol_table)
        
        destination = symbol_table.get_new_s_location()
        compiled_code.append(f"SUB {factor1_location} {factor2_location} {destination}")
        return destination 

class MultNode:
    def __init__(self, children):
        self.children = children
        
    def __repr__(self):
        return f"MultNode({self.children})"    
            
    def compile(self, compiled_code, symbol_table):
        factor1, factor2 = self.children
        factor1_location = factor1.compile(compiled_code, symbol_table)
        factor2_location = factor2.compile(compiled_code, symbol_table)
        
        destination = symbol_table.get_new_s_location()
        compiled_code.append(f"MULT {factor1_location} {factor2_location} {destination}")
        return destination 

class DivNode:
    def __init__(self, children):
        self.children = children
        
    def __repr__(self):
        return f"MultNode({self.children})"    
            
    def compile(self, compiled_code, symbol_table):
        factor1, factor2 = self.children
        factor1_location = factor1.compile(compiled_code, symbol_table)
        factor2_location = factor2.compile(compiled_code, symbol_table)
        
        destination = symbol_table.get_new_s_location()
        compiled_code.append(f"DIV {factor1_location} {factor2_location} {destination}")
        return destination

class FlipNode:
    def __init__(self, value):
        self.value = value
        
    def __repr__(self):
        return f"FlipNode({self.value})"    
            
    def compile(self, compiled_code, symbol_table):
        factor = self.value
        numerator = NumbrLiteral('1')
        numerator_location = numerator.compile(compiled_code, symbol_table)
        factor_location = factor.compile(compiled_code, symbol_table)
        
        destination = symbol_table.get_new_s_location()
        compiled_code.append(f"DIV {numerator_location} {factor_location} {destination}")
        return destination   
        
class SquareNode:
    def __init__(self, value):
        self.value = value
        
    def __repr__(self):
        return f"SquareNode({self.value})"    
            
    def compile(self, compiled_code, symbol_table):
        factor = self.value
        factor_location = factor.compile(compiled_code, symbol_table)
        
        destination = symbol_table.get_new_s_location()
        compiled_code.append(f"MULT {factor_location} {factor_location} {destination}")
        return destination      
            
class SAEMNode:
    def __init__(self, children):
        self.children = children
        
    def __repr__(self):
        return f"SAEMNode({self.children})"    
            
    def compile(self, compiled_code, symbol_table):
        factor1, factor2 = self.children
        factor1_location = factor1.compile(compiled_code, symbol_table)
        factor2_location = factor2.compile(compiled_code, symbol_table)
        
        destination = symbol_table.get_new_s_location()
        compiled_code.append(f"TEST_EQU {factor1_location} {factor2_location} {destination}")
        return destination    
        
class DIFFRINTNode:
    def __init__(self, children):
        self.children = children
        
    def __repr__(self):
        return f"DIFFRINTNode({self.children})"    
            
    def compile(self, compiled_code, symbol_table):
        factor1, factor2 = self.children
        factor1_location = factor1.compile(compiled_code, symbol_table)
        factor2_location = factor2.compile(compiled_code, symbol_table)
        
        destination = symbol_table.get_new_s_location()
        compiled_code.append(f"TEST_NEQU {factor1_location} {factor2_location} {destination}")
        return destination 

class FSMALLRNode:
    def __init__(self, children):
        self.children = children
        
    def __repr__(self):
        return f"FSMALLRNode({self.children})"    
            
    def compile(self, compiled_code, symbol_table):
        factor1, factor2 = self.children
        factor1_location = factor1.compile(compiled_code, symbol_table)
        factor2_location = factor2.compile(compiled_code, symbol_table)
        
        destination = symbol_table.get_new_s_location()
        compiled_code.append(f"TEST_LTE {factor1_location} {factor2_location} {destination}")
        return destination  
        
class FBIGGRNode:
    def __init__(self, children):
        self.children = children
        
    def __repr__(self):
        return f"FBIGGRNode({self.children})"    
            
    def compile(self, compiled_code, symbol_table):
        factor1, factor2 = self.children
        factor1_location = factor1.compile(compiled_code, symbol_table)
        factor2_location = factor2.compile(compiled_code, symbol_table)
        
        destination = symbol_table.get_new_s_location()
        compiled_code.append(f"TEST_GTE {factor1_location} {factor2_location} {destination}")
        return destination  
        
class BothNode:
    def __init__(self, children):
        self.children = children
        
    def __repr__(self):
        return f"BothNode({self.children})"  
        
    def compile(self, compiled_code, symbol_table):
        factor1, factor2 = self.children
        factor1_location = factor1.compile(compiled_code, symbol_table)
        factor2_location = factor2.compile(compiled_code, symbol_table)
        inter_destination = symbol_table.get_new_s_location()
        compiled_code.append(f"ADD {factor1_location} {factor2_location} {inter_destination}")
        destination = symbol_table.get_new_s_location()
        compiled_code.append(f"TEST_EQU {inter_destination} 2 {destination}")
        return destination
    
class EitherNode:
    def __init__(self, children):
        self.children = children
        
    def __repr__(self):
        return f"EitherNode({self.children})"  
        
    def compile(self, compiled_code, symbol_table):
        factor1, factor2 = self.children
        factor1_location = factor1.compile(compiled_code, symbol_table)
        factor2_location = factor2.compile(compiled_code, symbol_table)
        inter_destination = symbol_table.get_new_s_location()
        compiled_code.append(f"ADD {factor1_location} {factor2_location} {inter_destination}")
        destination = symbol_table.get_new_s_location()
        compiled_code.append(f"TEST_GTE {inter_destination} 1 {destination}")
        return destination

class WonNode:
    def __init__(self, children):
        self.children = children
        
    def __repr__(self):
        return f"WonNode({self.children})"  
        
    def compile(self, compiled_code, symbol_table):
        factor1, factor2 = self.children
        factor1_location = factor1.compile(compiled_code, symbol_table)
        factor2_location = factor2.compile(compiled_code, symbol_table)
        inter_destination = symbol_table.get_new_s_location()
        compiled_code.append(f"ADD {factor1_location} {factor2_location} {inter_destination}")
        destination = symbol_table.get_new_s_location()
        compiled_code.append(f"TEST_EQU {inter_destination} 1 {destination}")
        return destination

class NotNode:
    def __init__(self, child):
        self.child = child
        
    def __repr__(self):
        return f"NotNode({self.child})"  
        
    def compile(self, compiled_code, symbol_table):
        factor = self.child
        factor_location = factor.compile(compiled_code, symbol_table)
        destination = symbol_table.get_new_s_location()
        compiled_code.append(f"TEST_EQU {factor_location} 0 {destination}")
        return destination

class AllNode:
    def __init__(self, children):
        self.children = children
        
    def __repr__(self):
        return f"AllNode({self.children})"  
        
    def compile(self, compiled_code, symbol_table):
        destinations = []
        for child in self.children:
            child_location = child.compile(compiled_code, symbol_table)
            destinations.append(child_location)
        destination = symbol_table.get_new_s_location()
        compiled_code.append(f"VAL_COPY 0 {destination}")
        for temp_des in destinations:
            compiled_code.append(f"ADD {temp_des} {destination} {destination}")
        num_elm = len(destinations)
        compiled_code.append(f"TEST_EQU {num_elm} {destination} {destination}")
        return destination

class AnyNode:
    def __init__(self, children):
        self.children = children
        
    def __repr__(self):
        return f"AnyNode({self.children})"  
        
    def compile(self, compiled_code, symbol_table):
        destinations = []
        for child in self.children:
            child_location = child.compile(compiled_code, symbol_table)
            destinations.append(child_location)
        destination = symbol_table.get_new_s_location()
        compiled_code.append(f"VAL_COPY 0 {destination}")
        for temp_des in destinations:
            compiled_code.append(f"ADD {temp_des} {destination} {destination}")
        compiled_code.append(f"TEST_GTE {destination} 1 {destination}")
        return destination

class RandomExpression:
    def __init__(self):
        pass
    def __repr__(self):
        return f"RandomExpression"
    
    def compile(self, compiled_code, symbol_table):
        destination = symbol_table.get_new_s_location()
        compiled_code.append(f"RANDOM {destination}")
        return destination














